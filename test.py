from dotenv import load_dotenv; load_dotenv()
from parser import load_resume_text_from_path, parse_resume, get_llm
resume = parse_resume(load_resume_text_from_path("resume.pdf"),get_llm())
print(type(resume))          # <class 'models.Resume'> — NOT a string!
print(resume.name, "|", resume.email)
print(resume.skills)