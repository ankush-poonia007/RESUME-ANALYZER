from matcher import *
from models import Resume
from parser import get_llm, load_resume_text_from_path
from prompts import resume_prompt, jd_match_prompt

file_path = "ANKUSH_RESUME.pdf"

from langchain_core.output_parsers import StrOutputParser
llm = get_llm()
jd_description = """# Role: Generative AI & Backend Engineer Intern

### Company Overview:
We are a privacy-first AI engineering firm building production-ready, decentralized intelligence systems. We focus on deploying high-efficiency local small language models (SLMs) and complex data retrieval architectures for enterprise operations. 

### Position Summary:
We are seeking a highly analytical AI/ML Engineer Intern with strong computer science fundamentals and a passion for system design. In this role, you will help architect context-aware conversational agents and optimize advanced retrieval structures like GraphRAG. 

### Key Responsibilities:
- Build and optimize multi-turn conversational agents with state management.
- Develop privacy-first applications leveraging locally deployed, quantized SLMs.
- Implement efficient backend APIs using Python and FastAPI frameworks.
- Collaborate on implementing advanced RAG pipelines, incorporating Graph databases and semantic search patterns.
- Write clean, production-ready, object-oriented code backed by strong Data Structures and Algorithms (DSA).

### Required Qualifications & Technical Skills:
- Currently pursuing a B.Tech in Computer Science, AI/ML, or a highly quantitative field.
- Excellent academic standing (GPA 8.5+ preferred).
- Proficient in Python, Java, or C++ with a strong foundation in OOP and system design.
- Hands-on experience with Generative AI concepts, Prompt Engineering, NLP, and Local LLM deployment.
- Deep theoretical and practical knowledge of core DSA concepts (Graphs, Dynamic Programming, Trees).
- Experience working with version control systems (Git/GitHub) and REST APIs.

### Preferred (Bonus) Qualifications:
- Experience with containerization technologies like Docker.
- Experience with cloud platforms (AWS or Azure AI studio).
- Exposure to blockchain technologies, smart contracts, or decentralized systems (e.g., Stellar/Soroban).
- Continuous learner with a track record of completing rigorous technical certifications or coding challenges.
"""

chain = resume_prompt | llm | StrOutputParser()

resume_content = load_resume_text_from_path(file_path)
resume_response = chain.invoke(
    {
        'resume_text':resume_content
    }
)

jd_chain = jd_match_prompt | llm | StrOutputParser()

jd_response = jd_chain.invoke(
    {
        'jd_text':jd_description,
    'resume_json':resume_response
    }
)

print(jd_response)