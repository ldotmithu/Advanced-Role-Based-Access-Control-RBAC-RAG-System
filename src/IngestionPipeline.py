import os 
from utils.config import settings
from langchain_community.document_loaders import DirectoryLoader,PyPDFLoader,CSVLoader,UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

class IngestionRagPipeline:
    def __init__(self):
        self.datadir = settings.DATADIR
        self.departments = settings.DEPAERTMENTS
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.faiss_index = settings.FAISS_INDEX
        self.embeddings_model = settings.EMBEDDING_MODEL
        
    def run(self):
        self.embeddings = HuggingFaceEmbeddings(model_name = self.embeddings_model)
        
        for dep in self.departments:
            dep_path = os.path.join(self.datadir,dep)
            
            if not os.path.exists(dep_path):
                print(f"Skipping the {dep_path} Department")
                continue
            
            print(f"processing {dep} Department data....")
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
            print(f"Chunking size {len(split_docs)}")        
            
            db = FAISS.from_documents(documents=split_docs,
                                      embedding=self.embeddings)
            save_path = os.path.join(self.faiss_index,dep)
            db.save_local(folder_path=save_path)
            # print(f"Strore Vectors in {save_path}")
            


# if __name__=="__main__":
#     ingest = IngestionRagPipeline()
#     ingest.run()            
            

