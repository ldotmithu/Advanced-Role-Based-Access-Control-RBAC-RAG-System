import os 

class settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL",default="llama-3.1-8b-instant")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL",default="sentence-transformers/all-MiniLM-L6-v2")
    CHUNK_SIZE = 1100
    CHUNK_OVERLAP = 450
    TOP_K = 6
    DATADIR = "data"
    FAISS_INDEX = "Faiss-Vectors"
    DEPAERTMENTS = os.listdir(path=DATADIR)
    
     