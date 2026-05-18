import os 
import logging
from utils.config import settings
from langchain_community.document_loaders import DirectoryLoader,PyPDFLoader,CSVLoader,UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv

# Configure logging instead of suppressing warnings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class IngestionRagPipeline:
    def __init__(self):
        self.datadir = settings.DATADIR
        self.departments = settings.DEPARTMENTS
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.faiss_index = settings.FAISS_INDEX
        self.embeddings_model = settings.EMBEDDING_MODEL
        
    def run(self):
        self.embeddings = HuggingFaceEmbeddings(model_name = self.embeddings_model)
        
        for dep in self.departments:
            dep_path = os.path.join(self.datadir,dep)
            
            if not os.path.exists(dep_path):
                logger.warning(f"Skipping the {dep_path} Department - path does not exist")
                continue
            
            logger.info(f"Processing {dep} Department data....")
            loaders = [
                DirectoryLoader(dep_path,glob="**/*.pdf",loader_cls=PyPDFLoader), #type:ignore
                DirectoryLoader(dep_path,glob="**/*.csv",loader_cls=CSVLoader),
                DirectoryLoader(dep_path,glob="**/*.md",loader_cls=UnstructuredMarkdownLoader)
            ]
            all_documents = []
            for loader in loaders:
                documents = loader.load()
                for doc in documents:
                    doc.metadata["allowed_roles"] =[dep.capitalize()]
                all_documents.extend(documents)
            
            splitter = RecursiveCharacterTextSplitter(chunk_size = self.chunk_size,
                                                      chunk_overlap = self.chunk_overlap,
                                                      keep_separator=True)
            
            split_docs = splitter.split_documents(all_documents)
            logger.info(f"Chunked {len(split_docs)} documents for {dep} department")        
            
            db = FAISS.from_documents(documents=split_docs,
                                      embedding=self.embeddings)
            save_path = os.path.join(self.faiss_index,dep)
            db.save_local(folder_path=save_path)
            logger.info(f"Stored FAISS vectors for {dep} department at {save_path}")
            


# if __name__=="__main__":
#     ingest = IngestionRagPipeline()
#     ingest.run()            
            

