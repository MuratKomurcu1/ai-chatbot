import subprocess
import os
import ast
import json
import uuid
import re
import tempfile
from typing import Dict, List, Optional, Any
from datetime import datetime

class Code2FlowGenerator:
    def __init__(self):
        self.output_dir = "static/flowcharts"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_flow(self, code: str, language: str, style: str = "flowchart") -> Dict[str, Any]:
        """Ana akış diyagramı oluşturma fonksiyonu"""
        try:
            # Kod parse et
            parsed_structure = await self._parse_code_structure(code, language)
            
            # Mermaid syntax oluştur
            mermaid_content = self._generate_mermaid_syntax(parsed_structure, style, language)
            
            # Session ID oluştur
            session_id = str(uuid.uuid4())[:8]
            
            return {
                "session_id": session_id,
                "mermaid_code": mermaid_content,
                "structure": parsed_structure,
                "style": style,
                "language": language,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "fallback_diagram": await self._create_fallback_diagram(code, language)
            }

    async def _parse_code_structure(self, code: str, language: str) -> Dict[str, Any]:
        """Kod yapısını parse et"""
        if language.lower() == "python":
            return self._parse_python(code)
        elif language.lower() == "javascript":
            return self._parse_javascript(code)
        else:
            return self._generic_parse(code, language)

    def _parse_python(self, code: str) -> Dict[str, Any]:
        """Python kodu parse et"""
        try:
            tree = ast.parse(code)
            structure = {
                "functions": [],
                "classes": [],
                "imports": [],
                "control_flow": [],
                "variables": [],
                "calls": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                        "line": node.lineno,
                        "calls": self._extract_function_calls(node)
                    }
                    structure["functions"].append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        "line": node.lineno
                    }
                    structure["classes"].append(class_info)
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            structure["imports"].append(alias.name)
                    else:
                        structure["imports"].append(f"{node.module}")
                
                elif isinstance(node, (ast.If, ast.For, ast.While)):
                    structure["control_flow"].append({
                        "type": type(node).__name__,
                        "line": node.lineno
                    })
                
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        structure["calls"].append(node.func.id)
            
            return structure
            
        except Exception as e:
            return {"error": f"Python parsing error: {str(e)}"}

    def _parse_javascript(self, code: str) -> Dict[str, Any]:
        """JavaScript kodu parse et"""
        structure = {
            "functions": [],
            "classes": [],
            "imports": [],
            "control_flow": [],
            "calls": []
        }
        
        # Function declarations
        func_pattern = r'function\s+(\w+)\s*\([^)]*\)'
        functions = re.findall(func_pattern, code)
        structure["functions"] = [{"name": f, "type": "function"} for f in functions]
        
        # Arrow functions
        arrow_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>'
        arrow_functions = re.findall(arrow_pattern, code)
        structure["functions"].extend([{"name": f, "type": "arrow"} for f in arrow_functions])
        
        # Function calls
        call_pattern = r'(\w+)\s*\('
        calls = re.findall(call_pattern, code)
        structure["calls"] = list(set(calls))
        
        # Classes
        class_pattern = r'class\s+(\w+)'
        classes = re.findall(class_pattern, code)
        structure["classes"] = [{"name": c} for c in classes]
        
        # Control flow
        if 'if' in code:
            structure["control_flow"].append({"type": "If"})
        if any(keyword in code for keyword in ['for', 'while']):
            structure["control_flow"].append({"type": "Loop"})
        
        return structure

    def _generic_parse(self, code: str, language: str) -> Dict[str, Any]:
        """Genel kod analizi"""
        return {
            "language": language,
            "lines": len(code.splitlines()),
            "has_functions": bool(re.search(r'function|def|void|public|private', code)),
            "has_loops": bool(re.search(r'for|while|do', code)),
            "has_conditionals": bool(re.search(r'if|else|switch|case', code)),
            "complexity": "medium"
        }

    def _extract_function_calls(self, node) -> List[str]:
        """Fonksiyon çağrılarını çıkar"""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        return calls

    def _generate_mermaid_syntax(self, structure: Dict[str, Any], style: str, language: str) -> str:
        """Mermaid syntax oluştur"""
        if style == "flowchart":
            return self._generate_flowchart(structure, language)
        elif style == "sequence":
            return self._generate_sequence_diagram(structure, language)
        else:
            return self._generate_flowchart(structure, language)

    def _generate_flowchart(self, structure: Dict[str, Any], language: str) -> str:
        """Flowchart Mermaid syntax"""
        mermaid = "flowchart TD\n"
        
        # Start node
        mermaid += "    START([\"🚀 Program Start\"])\n"
        
        last_node = "START"
        
        # Imports/Includes
        if structure.get("imports") and len(structure["imports"]) > 0:
            mermaid += "    IMPORTS[\"📚 Import Libraries\"]\n"
            mermaid += "    START --> IMPORTS\n"
            last_node = "IMPORTS"
        
        # Classes
        if structure.get("classes"):
            for i, cls in enumerate(structure["classes"]):
                class_id = f"CLASS{i}"
                class_name = cls.get('name', f'Class{i}')
                mermaid += f"    {class_id}[\"🏗️ Class: {class_name}\"]\n"
                mermaid += f"    {last_node} --> {class_id}\n"
                last_node = class_id
        
        # Functions
        if structure.get("functions"):
            for i, func in enumerate(structure["functions"]):
                func_id = f"FUNC{i}"
                func_name = func.get("name", f"Function{i}")
                mermaid += f"    {func_id}[\"⚙️ {func_name}()\"]\n"
                mermaid += f"    {last_node} --> {func_id}\n"
                
                # Function calls (limit to 2 per function)
                if "calls" in func and func["calls"]:
                    for j, call in enumerate(func["calls"][:2]):
                        call_id = f"CALL{i}_{j}"
                        mermaid += f"    {call_id}[\"📞 {call}()\"]\n"
                        mermaid += f"    {func_id} --> {call_id}\n"
        
        # Control flow
        if structure.get("control_flow"):
            control_id = "CTRL"
            control_types = [ctrl.get("type", "Control") for ctrl in structure["control_flow"]]
            control_text = ", ".join(set(control_types))
            mermaid += f"    {control_id}{{\"🔄 {control_text}\"}}\n"
            mermaid += f"    {last_node} --> {control_id}\n"
            last_node = control_id
        
        # Main execution calls
        if structure.get("calls"):
            main_calls = list(set(structure["calls"]))[:2]  # Limit to 2
            for i, call in enumerate(main_calls):
                if call not in ['print']:  # Skip common functions already shown
                    call_id = f"MAIN{i}"
                    mermaid += f"    {call_id}[\"▶️ Execute {call}()\"]\n"
                    mermaid += f"    {last_node} --> {call_id}\n"
                    last_node = call_id
        
        # End node
        mermaid += "    END([\"✅ Program End\"])\n"
        mermaid += f"    {last_node} --> END\n"
        
        # Styling
        mermaid += "\n"
        mermaid += "    classDef startEnd fill:#e1f5fe,stroke:#01579b,stroke-width:2px\n"
        mermaid += "    classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px\n"
        mermaid += "    classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px\n"
        mermaid += "    class START,END startEnd\n"
        
        return mermaid

    def _generate_sequence_diagram(self, structure: Dict[str, Any], language: str) -> str:
        """Sequence diagram Mermaid syntax"""
        mermaid = "sequenceDiagram\n"
        mermaid += "    participant User\n"
        mermaid += "    participant Main\n"
        
        # Add functions as participants
        if structure.get("functions"):
            for func in structure["functions"][:5]:  # Limit to 5
                mermaid += f"    participant {func['name']}\n"
        
        mermaid += "\n"
        mermaid += "    User->>Main: Execute Program\n"
        
        # Function calls
        if structure.get("functions"):
            for func in structure["functions"]:
                mermaid += f"    Main->>+{func['name']}: Call {func['name']}()\n"
                if "calls" in func and func["calls"]:
                    for call in func["calls"][:2]:  # Limit to 2 calls per function
                        mermaid += f"    {func['name']}->>+Main: {call}()\n"
                mermaid += f"    {func['name']}->>-Main: Return\n"
        
        mermaid += "    Main->>User: Program Complete\n"
        
        return mermaid

    async def _create_fallback_diagram(self, code: str, language: str) -> Dict[str, Any]:
        """Hata durumunda fallback diagram"""
        lines = code.splitlines()
        
        mermaid = "flowchart TD\n"
        mermaid += "    A[📝 Code Analysis]\n"
        mermaid += f"    B[🔤 Language: {language}]\n"
        mermaid += f"    C[📏 Lines: {len(lines)}]\n"
        mermaid += "    D[❌ Parsing Failed]\n"
        mermaid += "    A --> B --> C --> D\n"
        
        session_id = f"fallback_{uuid.uuid4().hex[:8]}"
        
        return {
            "session_id": session_id,
            "mermaid_code": mermaid,
            "error": "Fallback diagram created due to parsing error"
        }

# Backward compatibility
async def generate_flowchart(code: str, language: str):
    generator = Code2FlowGenerator()
    result = await generator.generate_flow(code, language)
    return result.get("mermaid_code", "")