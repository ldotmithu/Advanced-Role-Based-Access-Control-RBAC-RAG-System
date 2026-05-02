import os 

class settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL",default="openai/gpt-oss-20b")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL",default="sentence-transformers/all-MiniLM-L6-v2")
    CHUNK_SIZE = 1100
    CHUNK_OVERLAP = 450
    TOP_K = 6
    DATADIR = "data"
    FAISS_INDEX = "FAISS-VECTORS"
    DEPAERTMENTS = os.listdir(path=DATADIR)
    
     