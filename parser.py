import os
import tempfile
from dotenv import load_dotenv
from langchain_groq import ChatGroq
# Deprecated langchain_community import completely removed to fix the warning
from models import Resume
from pypdf import PdfReader
from prompts import resume_prompt


load_dotenv()

def get_llm( model_name:str = "llama-3.3-70b-versatile", temperature:float = 0 ) -> ChatGroq:
    """Used to crate a ChatGroq client and return its obejct """
    if not os.getenv("GROQ_API_KEY"):
        raise ""
    
    return ChatGroq(model=model_name, temperature=temperature)

def load_resume_text_from_path(pdf_path: str) -> str:
    """Useful to load text from file hardcode using file_path and return the string"""
    
    full_path = f"./uploads/{pdf_path}"
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(
            f"Error: File not found at {full_path}. Please check your configuration."
        )
    
    reader = PdfReader(full_path)
    page_content = ""
    for page in page_content:
        text = page.extract_text()
        if text :
            page_content += text + "\n\n"
            
    return page_content


def load_resume_text_from_bytes(file:bytes, suffix:str = ".pdf") -> str:
    """Useful for stereamlit's uploaded_file.getvalue() bytes -> write to temp file -> load."""
    import io
    reader = PdfReader(io.BytesIO(file))
    return "\n".join(
        page.extract_text() for page in reader.pages if page.extract_text()
    )


def parse_resume(resume_text: str, llm: ChatGroq ) -> Resume:
    client = llm.with_structured_output(Resume,method="function_calling")
    chain = resume_prompt | client
    
    return chain.invoke(
        {
            'resume_text':resume_text
        }
    )
    
def parse_resume_from_path(pdf_path):
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"Error: File not found at {pdf_path}. Please check your path configuration."
        )
    
    reader = PdfReader(pdf_path)
    doc_content = "\n".join(
        page.extract_text() for page in reader.pages if page.extract_text()
    )
    
    client = get_llm().with_structured_output(Resume, method="function_calling")
    chain = resume_prompt | client
    
    return chain.invoke(
        {
            'resume_text':doc_content
        }
    )
    
    
if __name__ == "__main__":
    
    os.makedirs("./uploads", exist_ok=True)
    try:
        content = parse_resume_from_path("./uploads/resume.pdf")
        print("\nSuccessfully Parsed Reume Data Structure:\n")
        print(content)
    except Exception as e:
        print(f"\nExecution Failed: {e}")