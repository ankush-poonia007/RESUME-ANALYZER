# 📄 Resume Analyzer — Student Task Sheet (3 Hours)

Build a **Resume Parser + JD Matcher** yourself, step by step.
Every task is small. Every task has a **checkpoint** — do NOT move to the next task until your checkpoint passes.

---

## 🧠 The Flow (memorize this first — 5 min)

Say it out loud twice before you write any code:

```
PDF file
   │  (PyPDFLoader)
   ▼
Raw text (one big string)
   │  (PromptTemplate fills {resume_text})
   ▼
Prompt sent to LLM (ChatGroq)
   │  (with_structured_output forces the answer shape)
   ▼
Resume object (Pydantic — name, email, skills, ...)
   │  (+ Job Description text → second prompt → LLM again)
   ▼
JDMatchResult (score, matched skills, missing skills)
   │
   ▼
Streamlit UI shows everything
```

**One sentence version:** *PDF → text → prompt → LLM → structured object → compare with JD → show in UI.*

Files you will create:

| File | Job of the file |
|---|---|
| `models.py` | The **shape** of the data (Pydantic classes) |
| `prompts.py` | The **instructions** we give the LLM |
| `parser.py` | PDF → text → LLM → `Resume` object |
| `matcher.py` | `Resume` + JD text → LLM → `JDMatchResult` |
| `main.py` | Streamlit UI (**given by instructor at the end**) |

---

## ⏱️ Time Plan

| # | Task | Minutes |
|---|---|---|
| 0 | Setup | 15 |
| 1 | Hello, LLM | 10 |
| 2 | PDF → text | 15 |
| 3 | Data shapes (Pydantic) | 20 |
| 4 | The resume prompt | 10 |
| 5 | The magic: structured output | 20 |
| 6 | Make it a CLI tool | 10 |
| — | **BREAK** | 10 |
| 7 | JD match: model + prompt | 20 |
| 8 | JD match: the function | 15 |
| 9 | Streamlit: connect the UI | 25 |
| 10 | Demo + bonus | 10 |
| | **Total** | **180** |

---

## Task 0 — Setup (15 min)

**Goal:** Environment ready, API key working.

1. Create a project folder and a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   ```
2. Create `requirements.txt` with:
   ```
   langchain
   langchain-groq
   langchain-community
   pypdf
   pydantic
   python-dotenv
   streamlit
   ```
   Then: `pip install -r requirements.txt`
3. Get a free API key from https://console.groq.com → create `.env`:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```
4. Put ONE sample resume PDF in the folder as `resume.pdf` (use your own!).

✅ **Checkpoint:** `python -c "import langchain_groq, pypdf, streamlit; print('OK')"` prints `OK`.

---

## Task 1 — Hello, LLM (10 min)

**Goal:** Prove your key works. Talk to the LLM once.

Create `parser.py` and write ONE function:

```python
def get_llm(model_name: str = "llama-3.3-70b-versatile", temperature: float = 0) -> ChatGroq:
    ...
```

Rules:
- If `GROQ_API_KEY` is missing from the environment → raise an error with a helpful message.
- Return a `ChatGroq(model=model_name, temperature=temperature)`.

✅ **Checkpoint:** run this in a Python shell:
```python
from dotenv import load_dotenv; load_dotenv()
from parser import get_llm
print(get_llm().invoke("Say hi in 3 words").content)
```
You should see a short reply from the model.

🧠 **Flow question:** Why `temperature=0`? *(Hint: do we want creative answers or consistent extraction?)*

---

## Task 2 — PDF → Text (15 min)

**Goal:** Turn a PDF file into one big string.

Add to `parser.py`:

```python
def load_resume_text_from_path(pdf_path: str) -> str:
    ...
```

Rules:
- Use `PyPDFLoader` from `langchain_community.document_loaders`.
- `loader.load()` gives a **list of documents** (one per page).
- Join every page's `.page_content` with `"\n"` and return one string.

✅ **Checkpoint:**
```python
from parser import load_resume_text_from_path
text = load_resume_text_from_path("resume.pdf")
print(len(text), text[:300])
```
You should see your resume's real text.

🧠 **Flow question:** Why one string instead of a list of pages? *(Hint: what will we paste into the prompt?)*

---

## Task 3 — Data Shapes with Pydantic (20 min)

**Goal:** Define exactly WHAT we want to extract. This is the "contract" with the LLM.

Create `models.py` with three classes:

**`Education`** → `university_name: str`, `degree: str`, `gpa: Optional[float]` (between 0 and 10)

**`Experience`** → `company_name`, `years`, `project_name`, `project_description`, `tech_stack` (all Optional)

**`Resume`** → `name: str`, `email: str`, `phone_number: str`, `education: Optional[List[Education]]`, `experience: Optional[List[Experience]]`, `skills: Optional[List[str]]`

Rules:
- Every field gets a `Field(description="...")` — **the LLM reads these descriptions!**
- Use `ge=0, le=10` on gpa to enforce the range.

✅ **Checkpoint:**
```python
from models import Resume
r = Resume(name="Test", email="t@t.com", phone_number="123", skills=["Python"])
print(r.model_dump())
```
Also try `Resume(name="Test")` — it should **fail** (missing required fields). Failure here is success!

🧠 **Flow question:** Who reads the `description=` strings — you, or the LLM?

---

## Task 4 — The Resume Prompt (10 min)

**Goal:** Write the instruction we send to the LLM.

Create `prompts.py`:

```python
from langchain_core.prompts import PromptTemplate

resume_template = """..."""

resume_prompt = PromptTemplate(
    template=resume_template,
    input_variables=["resume_text"],
)
```

Your template must tell the LLM:
1. Its role ("You are an expert Resume Parser").
2. Extract ONLY what the schema defines.
3. Missing info → null / empty list.
4. **Never invent information.**
5. End with the placeholder: `{resume_text}`

✅ **Checkpoint:**
```python
from prompts import resume_prompt
print(resume_prompt.format(resume_text="FAKE RESUME HERE"))
```
Your fake text should appear inside the printed prompt.

🧠 **Flow question:** Why do we say "do not invent information"? What is this problem called in LLMs? *(Hallucination.)*

---

## Task 5 — The Magic: Structured Output (20 min)

**Goal:** Make the LLM fill your `Resume` class directly. This is the heart of the project.

Add to `parser.py`:

```python
def parse_resume(resume_text: str, llm: ChatGroq | None = None) -> Resume:
    ...
```

Three lines of logic:
1. `structured_llm = llm.with_structured_output(Resume, method="function_calling")`
2. `chain = resume_prompt | structured_llm`   ← the `|` pipes prompt into LLM
3. `result = chain.invoke({"resume_text": resume_text})` → return it

✅ **Checkpoint:**
```python
from dotenv import load_dotenv; load_dotenv()
from parser import load_resume_text_from_path, parse_resume
resume = parse_resume(load_resume_text_from_path("resume.pdf"))
print(type(resume))          # <class 'models.Resume'> — NOT a string!
print(resume.name, "|", resume.email)
print(resume.skills)
```

🧠 **Flow question:** Normally an LLM returns text. What did `with_structured_output` change?

---

## Task 6 — Make It a CLI Tool (10 min)

**Goal:** Run your parser from the terminal like a real tool.

Add to the bottom of `parser.py`:

```python
if __name__ == "__main__":
    ...
```

Rules:
- `load_dotenv()` first.
- Read the PDF path from `sys.argv[1]`; if missing, print usage and exit.
- Also write a tiny helper `parse_resume_from_path(pdf_path)` that combines Task 2 + Task 5.

✅ **Checkpoint:**
```bash
python parser.py resume.pdf
```
prints a full dictionary of your parsed resume. **First half done! Take a break. 🎉**

---

## Task 7 — JD Match: Model + Prompt (20 min)

**Goal:** Same pattern, second use case. Prove to yourself the pattern repeats.

**In `models.py`** add `JDMatchResult`:
- `match_score: float` (0–100)
- `matched_skills: List[str]`, `missing_skills: List[str]`
- `strengths: List[str]`, `gaps: List[str]`
- `summary: str`
- Use `default_factory=list` for the lists.

**In `prompts.py`** add `jd_match_prompt` with TWO input variables: `jd_text` and `resume_json`.
Tell the LLM: you are an expert recruiter, compare resume vs JD, base matched/missing skills strictly on the JD.

✅ **Checkpoint:**
```python
from prompts import jd_match_prompt
print(jd_match_prompt.format(jd_text="JD", resume_json="{}"))
```

🧠 **Flow question:** In Task 5 the prompt had 1 variable, here 2. Where do both get filled in?

---

## Task 8 — JD Match: The Function (15 min)

**Goal:** Write `matcher.py`. You already know this pattern — no new concepts!

```python
def match_resume_to_jd(resume: Resume, jd_text: str, llm: ChatGroq | None = None) -> JDMatchResult:
    ...
```

Same 3 steps as Task 5, but:
- Structured output class is `JDMatchResult`.
- Invoke with `{"jd_text": jd_text, "resume_json": resume.model_dump_json(indent=2)}`.

Create `jd.txt` — paste any real job description from LinkedIn/Internshala.

✅ **Checkpoint:** add an `if __name__ == "__main__":` block and run:
```bash
python matcher.py resume.pdf jd.txt
```
You should see a match score, matched skills, missing skills.

🧠 **Flow question:** Why do we send the resume as JSON and not the original PDF text? *(Cleaner, smaller, already structured.)*

---

## Task 9 — Streamlit: Connect the UI (25 min)

**Goal:** Wire the instructor's UI to YOUR code.

Your instructor will now share `main.py` (the Streamlit app). But it needs ONE function you haven't written yet.

**Step 1** — In Streamlit, `st.file_uploader` gives you **bytes**, not a file path. But `PyPDFLoader` needs a path! Write the bridge in `parser.py`:

```python
def load_resume_text_from_bytes(file_bytes: bytes, suffix: str = ".pdf") -> str:
    ...
```

Recipe:
1. Write the bytes into a `tempfile.NamedTemporaryFile(delete=False, suffix=suffix)`.
2. Call your existing `load_resume_text_from_path` on `tmp.name`.
3. In a `finally:` block, `os.remove` the temp file (always clean up, even on error!).

**Step 2** — Copy the instructor's `main.py` into your folder. **Read it before running.** Find and highlight:
- where YOUR `load_resume_text_from_bytes` is called
- where YOUR `parse_resume` is called
- where YOUR `match_resume_to_jd` is called
- what `st.session_state` is storing and WHY *(Streamlit reruns the whole script on every click — session_state is how data survives the rerun)*

✅ **Checkpoint:**
```bash
streamlit run main.py
```
Upload your resume → Parse → paste a JD → Run JD Match → see your score.

🧠 **Flow question:** Why does Streamlit need the bytes→temp-file trick at all?

---

## Task 10 — Demo (10 min)

Show a classmate:
1. Upload YOUR resume → parsed info appears.
2. Paste a real JD → match score appears.
3. Explain the whole flow in **under 60 seconds** without looking at notes:
   *"PDF → text → prompt → LLM → structured object → compare with JD → UI."*

If you can explain it, you own it. ✅

---

## 🚀 Bonus Tasks (homework / fast finishers)

1. **Easy:** Add `linkedin_url` and `certifications: List[str]` to the `Resume` model. Nothing else needs changing — see it appear in the JSON. *(Lesson: the schema drives everything.)*
2. **Easy:** Add a `st.download_button` to download the parsed resume as a JSON file.
3. **Medium:** Add a "Resume Improvement Tips" feature — third prompt, third Pydantic model (`ImprovementTips`), same pattern a third time.
4. **Medium:** Upload **multiple** resumes and rank all candidates for one JD by match score (recruiter mode!).
5. **Hard:** Swap `PyPDFLoader` for another loader so `.docx` resumes also work.
6. **Think:** What happens if someone uploads a PDF that is not a resume? Handle it gracefully.

---

## 🆘 Common Errors Cheat Sheet

| Error | Likely cause |
|---|---|
| `GROQ_API_KEY is not set` | Forgot `.env`, or forgot `load_dotenv()` |
| `ModuleNotFoundError` | venv not activated, or missing `pip install` |
| `ValidationError` from Pydantic | LLM output didn't match your model — check field types & descriptions |
| Empty text from PDF | Scanned/image PDF — PyPDF can't read images, use a text-based PDF |
| Streamlit "forgets" the parsed resume | You stored it in a normal variable instead of `st.session_state` |