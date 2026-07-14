from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
import os

load_dotenv()

def get_llm( model_name:str = "llama-3.3-70b-versatile", temperature:float = 0 ) -> ChatGroq:
    
    if not os.getenv("GROQ_API_KEY"):
        raise ""
    
    return ChatGroq(model=model_name, temperature=temperature)

def load_resume_text_from_path(pdf_path: str) -> str:

    try:
        loader = PyPDFLoader(f"./uploads/{pdf_path}")
        
        page_content = ""
        for text in loader.load():
            page_content += text.page_content + "\n\n"
            
        return page_content
    
    except FileNotFoundError:
        raise "Error: File not found!!\nPleaze check you file path"
    
if __name__ == "__main__":
    load_resume_text_from_path("ANKUSH_RESUME.pdf")