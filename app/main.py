from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import asyncio
import uvicorn
import os
from datetime import datetime

# Import our enhanced modules
from utils.code_analyzer import CodeAnalyzer
from utils.refactor import CodeRefactor
from utils.ai_chatbot import AIChatbot
from utils.code2flow import Code2FlowGenerator
from utils.demo_runner import DemoRunner
from app.config import settings

app = FastAPI(title="AI-Powered Code Review & Refactoring Assistant")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize services
code_analyzer = CodeAnalyzer()
code_refactor = CodeRefactor()
ai_chatbot = AIChatbot()
code2flow_generator = Code2FlowGenerator()
demo_runner = DemoRunner()

# Pydantic models
class CodeRequest(BaseModel):
    code: str
    language: str
    file_name: Optional[str] = None

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class RefactorRequest(BaseModel):
    code: str
    language: str
    refactor_type: str = "general"  # general, performance, security, readability

class DemoRequest(BaseModel):
    code: str
    language: str
    input_data: Optional[str] = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Ana sayfa"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/analyze")
async def analyze_code_endpoint(request: CodeRequest):
    """Gelişmiş kod analizi"""
    try:
        # Kod analizi
        analysis_result = await code_analyzer.analyze_comprehensive(
            request.code, 
            request.language,
            request.file_name
        )
        
        # Code2Flow diyagramı oluştur
        flowchart_data = await code2flow_generator.generate_flow(
            request.code, 
            request.language
        )
        
        return {
            "status": "success",
            "analysis": analysis_result,
            "flowchart": flowchart_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/refactor")
async def refactor_code_endpoint(request: RefactorRequest):
    """AI destekli kod refaktörü"""
    try:
        refactored_result = await code_refactor.refactor_with_ai(
            request.code,
            request.language,
            request.refactor_type
        )
        
        return {
            "status": "success",
            "original_code": request.code,
            "refactored_code": refactored_result["code"],
            "improvements": refactored_result["improvements"],
            "performance_gain": refactored_result.get("performance_estimation"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_with_ai(message: ChatMessage):
    """AI Chatbot ile etkileşim (Function Calling destekli)"""
    try:
        response = await ai_chatbot.process_message(
            message.message,
            message.conversation_id
        )
        
        return {
            "status": "success",
            "response": response["message"],
            "function_calls": response.get("function_calls", []),
            "conversation_id": response["conversation_id"],
            "suggestions": response.get("suggestions", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/demo/run")
async def run_demo(request: DemoRequest):
    """Canlı kod demo çalıştırıcı"""
    try:
        demo_result = await demo_runner.execute_code(
            request.code,
            request.language,
            request.input_data
        )
        
        return {
            "status": "success",
            "output": demo_result["output"],
            "execution_time": demo_result["execution_time"],
            "memory_usage": demo_result.get("memory_usage"),
            "errors": demo_result.get("errors", []),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/code2flow/{session_id}")
async def get_flowchart(session_id: str):
    """Code2Flow diyagramını al"""
    try:
        flowchart_path = f"static/flowcharts/{session_id}.png"
        if os.path.exists(flowchart_path):
            return {"status": "success", "flowchart_url": f"/static/flowcharts/{session_id}.png"}
        else:
            return {"status": "error", "message": "Flowchart not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Real-time chat WebSocket"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # AI ile işle
            response = await ai_chatbot.process_message(
                message_data["message"],
                client_id
            )
            
            # Yanıtı gönder
            await manager.send_personal_message(
                json.dumps({
                    "type": "ai_response",
                    "message": response["message"],
                    "function_calls": response.get("function_calls", []),
                    "timestamp": datetime.now().isoformat()
                }),
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/health")
async def health_check():
    """Sistem durumu kontrolü"""
    return {
        "status": "healthy",
        "services": {
            "code_analyzer": "active",
            "ai_chatbot": "active",
            "code2flow": "active",
            "demo_runner": "active"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/languages")
async def get_supported_languages():
    """Desteklenen programlama dilleri"""
    return {
        "languages": [
            {"code": "python", "name": "Python", "demo_support": True},
            {"code": "javascript", "name": "JavaScript", "demo_support": True},
            {"code": "java", "name": "Java", "demo_support": False},
            {"code": "cpp", "name": "C++", "demo_support": False},
            {"code": "csharp", "name": "C#", "demo_support": False},
            {"code": "go", "name": "Go", "demo_support": True},
            {"code": "rust", "name": "Rust", "demo_support": False}
        ]
    }
@app.post("/api/flowchart")
async def generate_flowchart_endpoint(request: CodeRequest):
    try:
        from utils.code2flow import Code2FlowGenerator
        generator = Code2FlowGenerator()
        result = await generator.generate_flow(request.code, request.language, "flowchart")
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)