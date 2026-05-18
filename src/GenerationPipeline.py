import os 
import logging
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough ,RunnableLambda
from langchain_core.prompts import PromptTemplate
from utils.config import settings
from src.RetrieverPipeline import RetrieverRAGPipeline
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv

# Configure logging instead of suppressing warnings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
os.environ["GROQ_API_KEY"]  = os.getenv("GROQ_API_KEY")  # type:ignore

class GenerationRAGPipeline:
    def __init__(self):
        self.llm_model = settings.LLM_MODEL
        self.api_key = settings.GROQ_API_KEY
        self.retriever = RetrieverRAGPipeline()
        

        self.llm = ChatGroq(
            model=self.llm_model,
            temperature=0.1,
            api_key=self.api_key,
            timeout=settings.REQUEST_TIMEOUT,
            max_retries=settings.MAX_RETRIES
        ) # type:ignore
    def _format_docs(self, docs):
        """Formats a list of documents into a readable string."""
        formatted_docs = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get('source', 'Unknown Source')
            page = doc.metadata.get('page', 'N/A')
            allowed_roles = doc.metadata.get("allowed_roles", [])
            
            
            roles_str = ", ".join(allowed_roles) if isinstance(allowed_roles, list) else allowed_roles

            content_block = f"""
            [Source: {source}] [Page: {page}] [Role: {roles_str}]
            ---
            {doc.page_content}
            ---
            """
            
            formatted_docs.append(content_block)
    
        return "\n\n".join(formatted_docs)
        
    def chatgeneration(self,role):
        self.context = self.retriever.run_retriever(role)
        
        self.prompt = PromptTemplate(
            template="""
            ### SYSTEM ROLE
            You are an AI assistant exclusively for the **{role}** department. 
            Your knowledge is strictly limited to the provided **Context**.

            ### CRITICAL RULES
            1. **STRICTLY USE CONTEXT**: Answer the question ONLY using the information in the **Context**.
            2. **NO EXTERNAL KNOWLEDGE**: Do NOT use your training data, general knowledge, or make assumptions.
            3. **ACCESS DENIED**: If the **Context** does not contain the answer, OR if the question is about a different department, you MUST output EXACTLY this sentence:
            "I do not have access to information regarding this topic for the {role} department."
            4. **NO HALLUCINATIONS**: Do not invent facts. If the answer is not in the context, refuse.
            

            ### CONTEXT
            {context}

            ### QUESTION
            {question}

            ### ANSWER
            """,
            input_variables=["context", "question", "role"]
        )  
        rag_chain = (
            {
                "context" : self.context |self._format_docs,
                "question":RunnablePassthrough(),
                "role": RunnableLambda(lambda x:role)
            }
        | self.prompt
        | self.llm
        | StrOutputParser()
        ) 
        
        return rag_chain

#for testing

# if __name__=="__main__":
#     generation = GenerationRAGPipeline()
#     role = input("enter your role ..: ").strip()
#     chain = generation.chatgeneration(role)
#     question = input("enter your question ? ").strip()
#     response = chain.invoke(question)
#     print(response)