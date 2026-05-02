from fastapi import FastAPI, HTTPException
from src.GenerationPipeline import GenerationRAGPipeline
from pydantic import BaseModel, field_validator
from typing import Optional

class ChatRequest(BaseModel):
    role: str
    question: str
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if not v.strip():
            raise ValueError('role cannot be empty')
        return v

class ChatResponse(BaseModel):
    response: str
    source: Optional[str] = None

app = FastAPI(title="RBAC RAG System")
_generation_pipeline = GenerationRAGPipeline()

@app.get("/")
async def home():
    return {"status": "RBAC RAG Application Running..."}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        chain = _generation_pipeline.chatgeneration(request.role)
        response = chain.invoke(request.question)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))