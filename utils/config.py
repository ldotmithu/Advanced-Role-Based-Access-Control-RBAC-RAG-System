import os 
import logging
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

logger = logging.getLogger(__name__)

class settings:
    # Validate critical environment variables at startup
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise ValueError("❌ GROQ_API_KEY environment variable is required but not set. Please configure it and try again.")
    
    LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    CHUNK_SIZE = 1100
    CHUNK_OVERLAP = 450
    TOP_K = 6
    DATADIR = "data"
    FAISS_INDEX = "Faiss-Vectors"
    DEPARTMENTS = os.listdir(path=DATADIR)
    BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    
    # Rate limiting configuration
    # Groq free tier: ~30 requests/minute, adjust based on your tier
    RATE_LIMIT_RPM = int(os.getenv("RATE_LIMIT_RPM", "25"))  # Requests per minute
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "120"))  # Seconds
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))  # Max retry attempts
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "10"))  # Initial delay in seconds