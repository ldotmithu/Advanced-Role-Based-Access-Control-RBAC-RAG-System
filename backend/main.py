from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.GenerationPipeline import GenerationRAGPipeline
from pydantic import BaseModel, field_validator
from typing import Optional
import logging
import os
from utils.config import settings
import warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    role: str
    question: str
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if not v.strip():
            raise ValueError('role cannot be empty')
        return v.strip().lower()
    
    @field_validator('question')
    @classmethod
    def validate_question(cls, v):
        if not v or not v.strip():
            raise ValueError('question cannot be empty')
        if len(v) > 2000:
            raise ValueError('question cannot exceed 2000 characters')
        return v.strip()

class ChatResponse(BaseModel):
    response: str
    source: Optional[str] = None

app = FastAPI(
    title="RBAC RAG System",
    description="Role-Based Access Control RAG System with hybrid retrieval",
    version="1.0.0"
)

# Add CORS middleware for production
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
try:
    _generation_pipeline = GenerationRAGPipeline()
    logger.info("✅ Generation pipeline initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize generation pipeline: {str(e)}")
    _generation_pipeline = None

@app.get("/")
async def home():
    return {"status": "RBAC RAG Application Running...", "version": "1.0.0"}

@app.get("/health")
async def health():
    """Health check endpoint for orchestrators"""
    return {"status": "healthy", "service": "RBAC RAG System"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint with role-based access control"""
    if _generation_pipeline is None:
        logger.error("Generation pipeline not initialized")
        raise HTTPException(status_code=503, detail="Service unavailable. Pipeline not initialized.")
    
    try:
        logger.info(f"Chat request from role: {request.role}")
        chain = _generation_pipeline.chatgeneration(request.role)
        response = chain.invoke(request.question)
        logger.info(f"Chat response generated successfully for role: {request.role}")
        return ChatResponse(response=response)
    except ValueError as e:
        logger.warning(f"Validation error for role {request.role}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_msg = str(e)
        # Handle rate limiting errors specifically
        if "429" in error_msg or "Too Many Requests" in error_msg:
            logger.warning(f"Rate limit hit: {error_msg}")
            raise HTTPException(
                status_code=429,
                detail="Service is busy (rate limited). Please wait 30-60 seconds and try again. Groq free tier has rate limits."
            )
        if "timeout" in error_msg.lower():
            logger.warning(f"Request timeout: {error_msg}")
            raise HTTPException(
                status_code=504,
                detail="Request timed out. Please try again with a shorter question."
            )
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while processing your request. Please try again."
        )