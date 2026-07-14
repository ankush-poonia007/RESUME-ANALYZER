from pydantic import BaseModel, Field
from typing import List, Optional


# --- Supporting Models for Resume Structure ---

class Education(BaseModel):
    """Schema for a candidate's academic background."""
    university_name: str = Field(description="The full name of the educational institution or university.")
    degree: str = Field(description="The specific degree, major, or certification earned.")
    gpa: Optional[float] = Field(description="The Grade Point Average achieved, typically out of 4.0 or 10.0.",ge=0.0, le=10.0)
    
class Experience(BaseModel):
    """Schema for a candidate's professional work history."""
    company_name: str = Field(description="The official name of the organization or company where the candidate worked.")
    starting_year: str = Field(description="The year the candidate started working at this company.")
    Ending_year: str = Field(description="The year the candidate finished working at this company, or 'Present' if currently employed.")

class Project(BaseModel):
    """Schema for individual personal or professional projects."""
    name: str = Field(description="The title or name of the project.")
    description: str = Field(description="A brief summary of what the project does, its goals, and the developer's contributions.")
    skills: List[str] = Field(description="A list of technical skills, languages, tools, or frameworks utilized in this project.")
    link: Optional[str] = Field(None, description="The URL to the project's repository, live deployment, or portfolio page.")


# --- Main Resilient Schemas ---
        
class Resume(BaseModel):
    """Comprehensive schema to parse and structure a candidate's complete resume."""
    name: str = Field(description="The full legal name of the candidate.")
    email: str = Field(description="The primary email address provided for contact.")
    phone_number: str = Field(description="The contact phone number of the candidate, including country code if applicable.")
    education: Optional[List[Education]] = Field(description="A list of academic institutions and degrees the candidate attended.")
    projects: Optional[List[Project]] = Field(None, description="A structured list of projects the candidate has worked on.")
    experience: Optional[List[Experience]] = Field(description="A chronological list of the candidate's past professional roles and work experience.")
    skills: Optional[List[str]] = Field(description="A list of core technical competencies, tools, and soft skills possessed by the candidate.")

class Job_Description(BaseModel):
    """Schema to extract relevant data requirements from a job posting."""
    matched_skill: List[str] = Field(description="A list of key technical and soft skills explicitly required or mentioned in the job description.")


if __name__ == "__main__":
    from models import Resume

    # 1. Define the complete sample data as a dictionary
    sample_resume_data = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone_number": "+1-555-0199",
        "education": [
            {
                "university_name": "State University",
                "degree": "Bachelor of Science in Computer Science",
                "gpa": 3.85
            }
        ],
        "projects": [
            {
                "name": "E-Commerce API",
                "description": "Built a high-performance REST API handling 10k daily active requests.",
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "link": "https://github.com"
            }
        ],
        "experience": [
            {
                "company_name": "Tech Corp Inc.",
                "starting_year": "2024",
                "Ending_year": "Present"
            }
        ],
        "skills": ["Python", "Pydantic", "Docker", "Git", "SQL"]
    }

    # 2. Unpack the dictionary into your Pydantic Resume model
    r = Resume(**sample_resume_data)

    # 3. Dump and print the validated data
    print(r.model_dump())
