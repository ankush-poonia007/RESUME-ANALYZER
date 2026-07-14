from parser import load_resume_text_from_path
text = load_resume_text_from_path("ANKUSH_RESUME.pdf")
print(len(text), text[:300])