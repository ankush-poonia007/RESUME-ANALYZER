# ==========================================
# models.py
# Pydantic schemas — the "contract" between
# our prompts and the structured LLM output.
#
# Every Field(description=...) is read by the
# LLM at inference time — write them clearly!
# ==========================================

from pydantic import BaseModel, Field
from typing import List, Optional


# ------------------------------------------
# Supporting / Nested Models
# ------------------------------------------

class Education(BaseModel):
    """One academic entry: university, degree, and optional GPA."""

    university_name: str = Field(
        description=(
            "The full official name of the educational institution or university "
            "(e.g. 'Massachusetts Institute of Technology', not 'MIT')."
        )
    )
    degree: str = Field(
        description=(
            "The specific degree title, major, or certification earned "
            "(e.g. 'Bachelor of Technology in Computer Science', "
            "'Master of Business Administration', 'AWS Certified Solutions Architect')."
        )
    )
    gpa: Optional[float] = Field(
        default=None,
        description=(
            "The Grade Point Average as a floating-point number. "
            "Normalize to a 0–10 scale (e.g. '3.8/4.0' → 9.5, '8.2/10' → 8.2). "
            "Return null if not mentioned."
        ),
        ge=0.0,
        le=10.0,
    )


class Experience(BaseModel):
    """One professional work experience entry at a single company or role."""

    company_name: Optional[str] = Field(
        default=None,
        description=(
            "The official name of the organization or company where the candidate worked "
            "(e.g. 'Google LLC', 'Infosys Limited'). Return null if not clearly stated."
        ),
    )
    years: Optional[str] = Field(
        default=None,
        description=(
            "Total duration at this role or company as a human-readable string "
            "(e.g. '2 years', '6 months', '1.5 years'). "
            "Derive this from start/end dates if explicit years are not written. "
            "Return null if dates are entirely absent."
        ),
    )
    project_name: Optional[str] = Field(
        default=None,
        description=(
            "The name or title of the primary project the candidate worked on at this company. "
            "Return null if no specific project is mentioned."
        ),
    )
    project_description: Optional[str] = Field(
        default=None,
        description=(
            "A concise 1–3 sentence summary of what the project does, "
            "the candidate's role, and the business impact or outcome. "
            "Return null if not present."
        ),
    )
    tech_stack: Optional[str] = Field(
        default=None,
        description=(
            "A comma-separated string of the specific technologies, languages, "
            "frameworks, or tools used in this role or project "
            "(e.g. 'Python, Django, PostgreSQL, AWS S3'). "
            "Return null if none are mentioned."
        ),
    )


class Project(BaseModel):
    """One personal, academic, or open-source project entry."""

    name: str = Field(
        description=(
            "The title or name of the project exactly as written in the resume "
            "(e.g. 'E-Commerce API', 'Sentiment Analyzer Chrome Extension')."
        )
    )
    description: str = Field(
        description=(
            "A concise summary (2–4 sentences) covering: what the project does, "
            "the problem it solves, the candidate's specific contributions, "
            "and any measurable results (e.g. 'reduced load time by 40%')."
        )
    )
    skills: List[str] = Field(
        description=(
            "Discrete list of every technical skill, language, library, "
            "framework, or tool used in this project. "
            "Split compound phrases — 'React.js and Node.js' → ['React.js', 'Node.js']. "
            "Return an empty list if nothing is specified."
        )
    )
    link: Optional[str] = Field(
        default=None,
        description=(
            "The full URL to the project's GitHub repository, live deployment, "
            "demo video, or portfolio page. Return null if not provided."
        ),
    )


# ------------------------------------------
# Top-Level / Main Schemas
# ------------------------------------------

class Resume(BaseModel):
    """
    Comprehensive schema representing a candidate's complete resume.
    
    The LLM must populate every field from the raw resume text.
    Fields marked Optional should be null (not guessed) when absent.
    """

    name: str = Field(
        description=(
            "The candidate's full legal name as it appears at the top of the resume "
            "(e.g. 'Arjun Sharma', 'Jane Marie Doe'). "
            "Do not include titles like 'Mr.' or 'Dr.'."
        )
    )
    email: str = Field(
        description=(
            "The primary contact email address. "
            "Return it exactly as written, preserving case "
            "(e.g. 'arjun.sharma@gmail.com')."
        )
    )
    phone_number: str = Field(
        description=(
            "The candidate's contact phone number including country code if present "
            "(e.g. '+91-98765-43210', '+1 (555) 012-3456'). "
            "Return exactly as written; do not reformat."
        )
    )
    education: Optional[List[Education]] = Field(
        default=None,
        description=(
            "Chronological list (most recent first) of all academic qualifications: "
            "degrees, diplomas, bootcamps, or certifications from institutions. "
            "Return null if no education section exists."
        ),
    )
    experience: Optional[List[Experience]] = Field(
        default=None,
        description=(
            "Chronological list (most recent first) of all professional work experiences, "
            "internships, and contract roles. "
            "Return null if the candidate has no work experience listed."
        ),
    )
    projects: Optional[List[Project]] = Field(
        default=None,
        description=(
            "List of personal, academic, freelance, or open-source projects "
            "the candidate has built or contributed to. "
            "Return null if no projects section exists."
        ),
    )
    skills: Optional[List[str]] = Field(
        default=None,
        description=(
            "Flat list of every individual technical skill, tool, language, "
            "framework, or soft skill mentioned anywhere in the resume. "
            "Deduplicate and separate compound entries "
            "(e.g. 'Python/Java' → ['Python', 'Java']). "
            "Return null if no skills are identifiable."
        ),
    )


class JDMatchResult(BaseModel):
    """
    Structured assessment of how well a candidate's resume matches a job description.
    
    Produced by the JD-matching LLM chain. Every list field defaults to []
    so the UI never receives None where it expects to iterate.
    """

    match_score: float = Field(
        description=(
            "An overall fit score from 0 to 100. "
            "Weight technical skill coverage most heavily (~60%), "
            "then relevant experience (~25%), then education/other (~15%). "
            "Be objective — a score above 80 means the candidate is a strong match; "
            "below 40 means significant gaps exist."
        ),
        ge=0.0,
        le=100.0,
    )
    matched_skills: List[str] = Field(
        default_factory=list,
        description=(
            "Skills that are explicitly required or preferred in the JD "
            "AND explicitly present in the candidate's resume, skills list, or projects. "
            "Only include confirmed matches — no benefit of the doubt."
        ),
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description=(
            "Skills that are explicitly required or strongly preferred in the JD "
            "but are completely absent from the candidate's resume. "
            "List each missing skill as a short phrase (e.g. 'Kubernetes', 'system design')."
        ),
    )
    strengths: List[str] = Field(
        default_factory=list,
        description=(
            "2–5 specific, evidence-based strengths the candidate brings to this role. "
            "Each item should be one actionable sentence referencing actual resume content "
            "(e.g. 'Built 3 production REST APIs in FastAPI, directly matching the JD requirement for Python web services.')."
        ),
    )
    gaps: List[str] = Field(
        default_factory=list,
        description=(
            "2–5 concrete gaps or concerns the hiring manager would flag. "
            "Each item should be a specific, actionable observation "
            "(e.g. 'No cloud deployment experience despite AWS being a required skill.'). "
            "Avoid vague statements like 'needs improvement'."
        ),
    )
    summary: str = Field(
        description=(
            "A 3–5 sentence executive summary for a recruiter: "
            "overall fit verdict, top 1–2 reasons to advance the candidate, "
            "top 1–2 concerns, and a clear hire/no-hire recommendation at this stage. "
            "Write professionally in third person (e.g. 'The candidate demonstrates...')."
        )
    )


# ------------------------------------------
# Quick self-test  →  python models.py
# ------------------------------------------

if __name__ == "__main__":
    sample = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone_number": "+1-555-0199",
        "education": [
            {
                "university_name": "State University",
                "degree": "Bachelor of Science in Computer Science",
                "gpa": 3.85,
            }
        ],
        "projects": [
            {
                "name": "E-Commerce API",
                "description": "High-performance REST API handling 10k daily requests.",
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "link": "https://github.com/jane/ecommerce-api",
            }
        ],
        "experience": [
            {
                "company_name": "Tech Corp Inc.",
                "years": "1 year",
                "project_name": "Inventory Dashboard",
                "project_description": "Built an internal dashboard to track warehouse inventory in real time.",
                "tech_stack": "React, Node.js, MongoDB",
            }
        ],
        "skills": ["Python", "FastAPI", "Docker", "Git", "SQL"],
    }

    r = Resume(**sample)
    print("✅ Resume model OK")
    print(r.model_dump_json(indent=2))

    # JDMatchResult smoke test
    m = JDMatchResult(
        match_score=78.5,
        matched_skills=["Python", "FastAPI"],
        missing_skills=["Kubernetes"],
        strengths=["Strong Python background with production API experience."],
        gaps=["No containerisation / orchestration experience."],
        summary="The candidate is a good fit for the backend role.",
    )
    print("\n✅ JDMatchResult model OK")
    print(m.model_dump_json(indent=2))