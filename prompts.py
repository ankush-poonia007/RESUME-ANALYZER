from langchain_core.prompts import ChatPromptTemplate

# --- 1. OPTIMIZED RESUME PARSER PROMPT ---

RESUME_TEMPLATE = """You are an elite, highly accurate Resume Parsing Engine. 
Your sole task is to extract unstructured candidate data into a strictly structured JSON schema.

### Core Extraction Rules:
1. **Absolute Truthfulness**: Extract information ONLY if it is explicitly stated. Never infer, extrapolate, or hallucinate credentials, degrees, dates, or skills.
2. **Missing Information Handling**: If a specific data field or an entire section is not present in the text, return `null` (for optional fields) or an empty array `[]` (for lists). Do not guess.
3. **Data Normalization**: 
   - Clean up phone numbers to a consistent format if possible.
   - For `Ending_year`, if the candidate is currently working there, explicitly output 'Present'.
   - Format `gpa` strictly as a floating-point number (e.g., 3.8). Remove text like '/4.0'.
4. **Skill Isolation**: Separate generic blocks of text into individual, discrete skills (e.g., convert "Experienced in Python, Java, and AWS" into `["Python", "Java", "AWS"]`).

### Output Constraint:
You must strictly match the structure expected by the `Resume` Pydantic schema provided by the system execution engine."""

resume_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", RESUME_TEMPLATE),
        ("human", "--- START UNSTRUCTURED RESUME TEXT ---\n{resume_text}\n--- END UNSTRUCTURED RESUME TEXT ---"),
    ]
)


# --- 2. OPTIMIZED JOB DESCRIPTION MATCHING PROMPT ---

JD_MATCH_TEMPLATE = """You are a Principal Technical Recruiter and Applicant Tracking System (ATS) optimization expert.
Your job is to objectively analyze a candidate's resume data against a Job Description (JD) to evaluate technical and cultural alignment.

### Assessment Methodology:
1. **Explicit Mapping**: 
   - A skill is only a `matched_skill` if it is explicitly required in the JD **AND** explicitly present in the candidate's resume or project list.
   - A skill is a `missing_skill` if it is highlighted as required/preferred in the JD but completely absent from the candidate's data.
2. **Context-Aware Evaluation**: Do not look just at the "Skills" list. Cross-reference the candidate's `projects` and `experience` descriptions to catch implied tool usage if named directly.
3. **Zero Bias**: Be completely objective. Do not give the candidate the benefit of the doubt. If the JD requires "Kubernetes" and it is nowhere in the resume, it is missing.

### Output Constraint:
Your output must perfectly populate the fields defined in the `JDMatchResult` Pydantic model. Ensure all explanations are concise, professional, and actionable."""

jd_match_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", JD_MATCH_TEMPLATE),
        (
            "human",
            "### TARGET JOB DESCRIPTION:\n{jd_text}\n\n"
            "### CANDIDATE RESUME DATA (STRUCTURED JSON):\n{resume_json}\n\n"
            "Perform the assessment and output the structured result."
        ),
    ]
)
