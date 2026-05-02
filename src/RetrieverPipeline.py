import os 
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_community.embeddings import HuggingFaceEmbeddings
from utils.config import settings
from langchain_community.document_loaders import DirectoryLoader,PyPDFLoader,CSVLoader,UnstructuredMarkdownLoader
from src.IngestionPipeline import IngestionRagPipeline
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

class RetrieverRAGPipeline:
    def __init__(self):
        self.faiss_index = settings.FAISS_INDEX
        self.embeddings_model = settings.EMBEDDING_MODEL
        self.departments = settings.DEPAERTMENTS
        self.top_k = settings.TOP_K
        self.datadir = settings.DATADIR
        
        self.embeddings = HuggingFaceEmbeddings(model_name = self.embeddings_model)
        
    def _load_raw_document(self,role):
        """ only load the specific data based on the ROLE """
        for dep in self.departments:
            dep_path = os.path.join(self.datadir,role) 
            
            loaders = [
                DirectoryLoader(dep_path,glob="**/*.pdf",loader_cls=PyPDFLoader), #type:ignore
                DirectoryLoader(dep_path,glob="**/*.csv",loader_cls=CSVLoader),
                DirectoryLoader(dep_path,glob="**/*.md",loader_cls=UnstructuredMarkdownLoader),
            ]    
            all_documents = []
            for loader in loaders:
                documents = loader.load()
                for doc in documents:
                    doc.metadata["allowed_roles"] = [dep.capitalize()]
                all_documents.extend(documents)
                
        return all_documents            
                
        
    def run_retriever(self,role):
        if not os.path.exists(self.faiss_index):
            print("FAISS index Not Found, SO Running the Ingestion Pipeline..")
            ingestion = IngestionRagPipeline()
            ingestion.run()
        
        dep_path = os.path.join(self.faiss_index,role)
        vector_db = FAISS.load_local(folder_path=dep_path,embeddings=self.embeddings,
                         allow_dangerous_deserialization=True)
        
        vector_retriever = vector_db.as_retriever(search_kwargs={'k': self.top_k})
        docs = self._load_raw_document(role) 
        bm25_retriever = BM25Retriever.from_documents(documents=docs)
        hybrid_retriever = EnsembleRetriever(
            retrievers=[vector_retriever,bm25_retriever],
            weights=[0.6,0.4]
        )
        
        return hybrid_retriever

#for testing

# if __name__=="__main__":
#     retriever = RetrieverRAGPipeline()
#     role = input("enter role... : ")
#     response = retriever.run_retriever(role)
#     question = input("enter the question .. : ")
#     result = response.invoke(question)
#     print(result)
        
             
        