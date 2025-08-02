import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import os

class AIChatbot:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            self.client = None
            print("OpenAI API key bulunamadı! AI özellikleri demo modunda çalışacak.")
        else:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                self.client = None
                print("OpenAI paketi bulunamadı! pip install openai komutu ile yükleyin.")
        
        self.conversations = {}
        
        # Function definitions for OpenAI Function Calling
        self.functions = [
            {
                "type": "function",
                "function": {
                    "name": "analyze_code_quality",
                    "description": "Kod kalitesini analiz eder ve iyileştirme önerileri sunar",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "Analiz edilecek kod"},
                            "language": {"type": "string", "description": "Programlama dili"},
                            "focus": {"type": "string", "enum": ["security", "performance", "readability", "all"]}
                        },
                        "required": ["code", "language"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "suggest_refactoring",
                    "description": "Kod refaktörü önerileri sunar",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "Refaktör edilecek kod"},
                            "language": {"type": "string", "description": "Programlama dili"},
                            "strategy": {"type": "string", "enum": ["performance", "maintainability", "security"]}
                        },
                        "required": ["code", "language"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_code_flow",
                    "description": "Kod akış diyagramı oluşturur",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "Diyagram oluşturulacak kod"},
                            "language": {"type": "string", "description": "Programlama dili"},
                            "style": {"type": "string", "enum": ["flowchart", "sequence", "class"]}
                        },
                        "required": ["code", "language"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_code_demo",
                    "description": "Kod canlı olarak çalıştırır ve sonuçları gösterir",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "Çalıştırılacak kod"},
                            "language": {"type": "string", "description": "Programlama dili"},
                            "input_data": {"type": "string", "description": "Kod için input verisi"}
                        },
                        "required": ["code", "language"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "explain_code",
                    "description": "Kod parçasını detaylı olarak açıklar",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "Açıklanacak kod"},
                            "language": {"type": "string", "description": "Programlama dili"},
                            "level": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]}
                        },
                        "required": ["code", "language"]
                    }
                }
            }
        ]

    async def process_message(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Ana mesaj işleme fonksiyonu"""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                "messages": [
                    {
                        "role": "system",
                        "content": """Sen bir AI destekli kod inceleme ve refaktör asistanısın. 
                        Görevin kullanıcılara kod analizi, refaktör önerileri, kod açıklamaları ve 
                        canlı kod çalıştırma konularında yardım etmek. Function calling özelliğini 
                        kullanarak kullanıcının isteklerini uygun fonksiyonlara yönlendir.
                        
                        Yeteneklerin:
                        - Kod kalite analizi
                        - Güvenlik açığı tespiti
                        - Performans optimizasyonu
                        - Kod refaktörü
                        - Akış diyagramı oluşturma
                        - Canlı kod çalıştırma
                        - Kod açıklama
                        
                        Kullanıcıya dostça ve profesyonel yaklaş."""
                    }
                ],
                "created_at": datetime.now().isoformat()
            }
        
        # Kullanıcı mesajını ekle
        self.conversations[conversation_id]["messages"].append({
            "role": "user",
            "content": message
        })
        
        if not self.client:
            # Fallback response when OpenAI is not available
            return {
                "message": "OpenAI API bağlantısı yok. Demo modunda çalışıyor. Kodunuzla ilgili genel öneriler: Kod okunabilirliğini artırın, hata yakalama ekleyin, ve performansı optimize edin.",
                "function_calls": [],
                "conversation_id": conversation_id,
                "suggestions": self._generate_suggestions(message)
            }
        
        try:
            # OpenAI API çağrısı (Function Calling ile)
            response = await self._call_openai_with_functions(
                self.conversations[conversation_id]["messages"]
            )
            
            assistant_message = response.choices[0].message
            
            # Function call var mı kontrol et
            function_calls = []
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    function_result = await self._execute_function_call(tool_call.function)
                    function_calls.append(function_result)
                    
                    # Function call sonucunu conversation'a ekle
                    self.conversations[conversation_id]["messages"].append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(function_result)
                    })
                
                # Final response al
                final_response = await self._call_openai_with_functions(
                    self.conversations[conversation_id]["messages"]
                )
                assistant_message = final_response.choices[0].message
            
            # Assistant mesajını conversation'a ekle
            self.conversations[conversation_id]["messages"].append({
                "role": "assistant",
                "content": assistant_message.content
            })
            
            return {
                "message": assistant_message.content,
                "function_calls": function_calls,
                "conversation_id": conversation_id,
                "suggestions": self._generate_suggestions(message)
            }
            
        except Exception as e:
            return {
                "message": f"Üzgünüm, bir hata oluştu: {str(e)}",
                "function_calls": [],
                "conversation_id": conversation_id,
                "suggestions": []
            }

    async def _call_openai_with_functions(self, messages: List[Dict]) -> Any:
        """OpenAI API'sını function calling ile çağır"""
        return await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # gpt-4 yerine gpt-3.5-turbo kullan
                messages=messages,
                # tools=self.functions,  # Tool calling'i şimdilik kapat
                # tool_choice="auto",
                temperature=0.7,
                max_tokens=1500
            )
        )

    async def _execute_function_call(self, function_call) -> Dict[str, Any]:
        """Function call'u çalıştır"""
        function_name = function_call.name
        function_args = json.loads(function_call.arguments)
        
        try:
            if function_name == "analyze_code_quality":
                return await self._analyze_code_quality(**function_args)
            elif function_name == "suggest_refactoring":
                return await self._suggest_refactoring(**function_args)
            elif function_name == "generate_code_flow":
                return await self._generate_code_flow(**function_args)
            elif function_name == "run_code_demo":
                return await self._run_code_demo(**function_args)
            elif function_name == "explain_code":
                return await self._explain_code(**function_args)
            else:
                return {"error": f"Bilinmeyen fonksiyon: {function_name}"}
                
        except Exception as e:
            return {"error": f"Fonksiyon çalıştırılırken hata: {str(e)}"}

    async def _analyze_code_quality(self, code: str, language: str, focus: str = "all") -> Dict:
        """Kod kalitesi analizi"""
        try:
            from utils.code_analyzer import analyze_code
            result = analyze_code(code, language)
            return {
                "function": "analyze_code_quality",
                "result": result,
                "focus": focus
            }
        except Exception as e:
            return {"error": f"Code analysis failed: {str(e)}"}

    async def _suggest_refactoring(self, code: str, language: str, strategy: str = "maintainability") -> Dict:
        """Refaktör önerisi"""
        try:
            from utils.refactor import refactor_code
            result = refactor_code(code)
            return {
                "function": "suggest_refactoring",
                "result": {"refactored_code": result},
                "strategy": strategy
            }
        except Exception as e:
            return {"error": f"Refactoring failed: {str(e)}"}

    async def _generate_code_flow(self, code: str, language: str, style: str = "flowchart") -> Dict:
        """Kod akış diyagramı"""
        try:
            from utils.code_analyzer import generate_flowchart
            result = generate_flowchart(code, language)
            return {
                "function": "generate_code_flow",
                "result": {"flowchart": result},
                "style": style
            }
        except Exception as e:
            return {"error": f"Flow generation failed: {str(e)}"}

    async def _run_code_demo(self, code: str, language: str, input_data: str = "") -> Dict:
        """Canlı kod çalıştırma"""
        try:
            from utils.demo_runner import DemoRunner
            runner = DemoRunner()
            result = await runner.execute_code(code, language, input_data)
            return {
                "function": "run_code_demo",
                "result": result
            }
        except Exception as e:
            return {"error": f"Code execution failed: {str(e)}"}

    async def _explain_code(self, code: str, language: str, level: str = "intermediate") -> Dict:
        """Kod açıklama"""
        # Basit kod açıklama implementasyonu
        explanation = f"Bu {language} kodu basit bir fonksiyon tanımlar ve çalıştırır. {level} seviyesi için uygun."
        return {
            "function": "explain_code",
            "result": {
                "explanation": explanation,
                "complexity": "medium",
                "key_concepts": ["function definition", "function call", "output"]
            },
            "level": level
        }

    def _generate_suggestions(self, message: str) -> List[str]:
        """Kullanıcı mesajına göre öneriler oluştur"""
        suggestions = []
        
        if "analiz" in message.lower() or "analyze" in message.lower():
            suggestions.append("Kodun güvenlik açıklarını kontrol et")
            suggestions.append("Performans iyileştirme önerileri al")
        
        if "refactor" in message.lower():
            suggestions.append("Kod okunabilirliğini artır")
            suggestions.append("Fonksiyonları küçült ve modülerleştir")
        
        if "çalıştır" in message.lower() or "run" in message.lower():
            suggestions.append("Kodu test verileri ile dene")
            suggestions.append("Hata durumlarını kontrol et")
        
        if not suggestions:
            suggestions = [
                "Kod kalitesini analiz et",
                "Refactoring önerileri al",
                "Kod açıklaması iste"
            ]
        
        return suggestions[:3]  # Maximum 3 öneri

    def get_conversation_history(self, conversation_id: str) -> Optional[Dict]:
        """Konuşma geçmişini al"""
        return self.conversations.get(conversation_id)

    def clear_conversation(self, conversation_id: str) -> bool:
        """Konuşmayı temizle"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False