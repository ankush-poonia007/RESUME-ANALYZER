# 📄 AI Resume Analyzer & JD Matcher

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Orchestration-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLM_Inference-F55036?style=for-the-badge)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)

### Parse any resume PDF. Match it against any job description. Get a structured, explainable score — in seconds.

</div>

---

## 🧠 What This Actually Does

Most "resume matchers" are keyword-count hacks. This one isn't.

It uses an LLM with **structured output** (function-calling forced into a Pydantic schema) to turn a messy, human-written PDF into clean typed data — then runs a second structured LLM call to compare that data against a job description and produce a scored, evidence-based verdict.

```
 resume.pdf
     │   PyPDF text extraction
     ▼
 raw resume text
     │   resume_prompt (system + human message)
     ▼
 Groq LLM  ──with_structured_output──▶  Resume  (Pydantic)
     │
     │   + job description text
     ▼
 jd_match_prompt (resume_json + jd_text)
     ▼
 Groq LLM  ──with_structured_output──▶  JDMatchResult (Pydantic)
     │
     ▼
 Streamlit dashboard
```

No regex keyword matching. No hallucinated skills — the schema and prompts explicitly forbid inferring anything not stated in the source text.

---

## ✨ Features

- **🔎 Structured Resume Extraction** — Pulls name, contact info, education (with GPA normalized to a 0–10 scale), work experience, projects, and a deduplicated skills list into a strict `Resume` schema.
- **🎯 JD Match Scoring** — Produces a `match_score` (0–100), explicit `matched_skills` / `missing_skills`, evidence-based `strengths` and `gaps`, and a recruiter-style written `summary`.
- **📤 In-Memory Upload Handling** — Streamlit file uploads (bytes) are routed through a temp-file bridge so the same `PyPDFLoader`/`pypdf` extraction path works for both CLI and UI usage.
- **🖥️ Two Ways to Run It** — as a Streamlit web app (`main.py`) or as standalone CLI tools (`python parser.py resume.pdf`, `python matcher.py resume.pdf jd.txt`).
- **🧱 Schema-Driven Design** — Add a field to `models.py` (e.g. `linkedin_url`) and it flows through extraction and the UI automatically — no other code changes required.
- **⬇️ JSON Export** — Download the parsed resume as a `.json` file directly from the dashboard.

---

## 🏗️ Project Structure

```
resume-analyzer/
│
├── main.py              # Streamlit UI — upload, parse, match, and visualize results
├── parser.py             # get_llm() + PDF → text (path & bytes) + parse_resume()
├── matcher.py             # match_resume_to_jd() — Resume + JD text → JDMatchResult
├── models.py               # Pydantic schemas: Education, Experience, Project, Resume, JDMatchResult
├── prompts.py                # resume_prompt and jd_match_prompt (ChatPromptTemplate)
│
├── requirements.txt            # Pinned dependencies
├── .env.example                  # Template for required environment variables
└── .gitignore                      # Excludes .venv, .env, __pycache__, uploads/
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/ankush-poonia007/resume-analyzer.git
cd resume-analyzer
```

### 2. Create a virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure your API key
```bash
cp .env.example .env
```
Then open `.env` and add your free [Groq API key](https://console.groq.com):
```
GROQ_API_KEY=gsk_your_key_here
```

### 5. Run the app
```bash
streamlit run main.py
```

---

## 🖥️ CLI Usage (no Streamlit needed)

Parse a resume directly:
```bash
python parser.py resume.pdf
```

Match a parsed resume against a job description:
```bash
python matcher.py resume.pdf jd.txt
```

---

## 🧩 The Data Contract

Every field in `models.py` carries a `Field(description=...)` — the LLM reads these at inference time, so the schema *is* the prompt. A quick look at what gets extracted:

| Model | Captures |
|---|---|
| `Education` | University name, degree/major, GPA normalized to 0–10 |
| `Experience` | Company, duration, project name/description, tech stack |
| `Project` | Name, description, discrete skills list, link |
| `Resume` | Name, email, phone, education, experience, projects, skills |
| `JDMatchResult` | Match score, matched/missing skills, strengths, gaps, summary |

---

## 🛡️ Prompt Design Notes

- **Zero-hallucination instructions** — both prompts explicitly forbid inferring dates, degrees, or skills that aren't present in the source text; missing fields return `null` or `[]` rather than a guess.
- **Delimited input** — raw resume text is wrapped in clear `--- START / END ---` boundaries in the human message, separating untrusted document content from system instructions.
- **Two-stage structured extraction** — the same `with_structured_output(..., method="function_calling")` pattern is reused for both the resume parser and the JD matcher, so the LLM always returns a validated Pydantic object rather than free text to parse.

---

## 🚀 Possible Next Steps

- [ ] Add `linkedin_url` and `certifications` fields to `Resume`
- [ ] Add a third prompt/model for "Resume Improvement Tips"
- [ ] Support ranking multiple resumes against one JD (recruiter mode)
- [ ] Add `.docx` resume support alongside PDF
- [ ] Graceful handling for non-resume PDFs uploaded by mistake

---

## 🤝 Contact

<p align="left">
  <a href="https://www.linkedin.com/in/ankush-poonia007/" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-Ankush_Poonia-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/>
  </a>
  <a href="https://github.com/ankush-poonia007/" target="_blank">
    <img src="https://img.shields.io/badge/GitHub-ankush--poonia007-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/>
  </a>
  <a href="mailto:pooniaankush007@gmail.com">
    <img src="https://img.shields.io/badge/Email-pooniaankush007%40gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"/>
  </a>
</p>

**Ankush Poonia**

---

<div align="center">
<sub>Built with LangChain, Groq, and Pydantic — a hands-on exploration of structured LLM output for real-world document parsing.</sub>
</div>