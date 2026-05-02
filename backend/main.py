from fastapi import FastAPI
from src.GenerationPipeline import GenerationRAGPipeline
import os 
from pydantic import BaseModel

class RAGClass(BaseModel):
    role:str
    question :str

app = FastAPI()


@app.get("/")
def home():
    return "RBAC RAG Aplication Running....."

@app.post("/chat")
def chat(ragclass:RAGClass):
    generation = GenerationRAGPipeline()
    chain = generation.chatgeneration(ragclass.role)
    response = chain.invoke(ragclass.question)
    return response

    