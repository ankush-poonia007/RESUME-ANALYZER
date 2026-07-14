from typing import Optional
from langchain_groq import ChatGroq
from models import Resume, JDMatchResult
from prompts import jd_match_prompt
from parser import get_llm

def match_resume_to_jd(resume: Resume, job_description: str, llm: Optional[ChatGroq] = None) -> JDMatchResult:
    """Compares an instantiated Resume object against a Job Description string.
    
    Returns a validated JDMatchResult Pydantic object using structured output extraction.
    """
    # Fallback to default LLM instance if none is explicitly provided by the caller
    active_llm = llm if llm is not None  else get_llm()
    
    # Bind the verification model structure to the Groq inference engine
    client = active_llm.with_structured_output(JDMatchResult, method="function_calling")
    
    # Construct the LangChain Expression Language (LCEL) chain
    chain = jd_match_prompt | client 
    
    # Execute the comparison loop and return the instantiated model object
    return chain.invoke(
        {
            'jd_text': job_description,
            'resume_json': resume.model_dump_json(indent=4)
        }
    )
