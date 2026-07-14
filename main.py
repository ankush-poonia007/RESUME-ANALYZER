# ==========================================
# main.py
# Streamlit UI — Resume Parser + JD Matcher
# ==========================================

import os

import streamlit as st
from dotenv import load_dotenv

from parser import load_resume_text_from_bytes, parse_resume, get_llm
from matcher import match_resume_to_jd

# ==========================================
# Page config — must be the very first
# Streamlit call in the script.
# ==========================================

st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# Custom CSS — tightens Streamlit's default
# spacing and adds a few visual accents
# without fighting its component system.
# ==========================================

st.markdown(
    """
    <style>
        /* Tighten top padding */
        .block-container { padding-top: 1.8rem; }

        /* Section card */
        .card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 1rem;
        }

        /* Score badge colours */
        .score-high  { color: #16a34a; font-size: 2.4rem; font-weight: 700; }
        .score-mid   { color: #d97706; font-size: 2.4rem; font-weight: 700; }
        .score-low   { color: #dc2626; font-size: 2.4rem; font-weight: 700; }

        /* Skill pill */
        .pill {
            display: inline-block;
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
            border-radius: 999px;
            padding: 2px 10px;
            font-size: 0.78rem;
            margin: 2px 2px;
        }
        .pill-red {
            background: #fef2f2;
            color: #b91c1c;
            border-color: #fecaca;
        }
        .pill-green {
            background: #f0fdf4;
            color: #15803d;
            border-color: #bbf7d0;
        }

        /* Sidebar step label */
        .step-label {
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #64748b;
            margin-bottom: 0.3rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# Setup
# ==========================================

load_dotenv()  # reads GROQ_API_KEY from .env

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ==========================================
# LLM — cached so we don't re-create the
# Groq client on every Streamlit rerun.
# ==========================================

@st.cache_resource
def get_cached_llm():
    """Create the Groq LLM client once and reuse it across reruns."""
    return get_llm()

# ==========================================
# API-key guard — stop early with a helpful
# message rather than crashing later.
# ==========================================

if not os.environ.get("GROQ_API_KEY"):
    st.error(
        "**GROQ_API_KEY is not set.**  \n"
        "Create a `.env` file in this folder with:  \n"
        "```\nGROQ_API_KEY=gsk_your_key_here\n```  \n"
        "Then restart the app.",
        icon="🔑",
    )
    st.stop()

# ==========================================
# Session state — Streamlit reruns the whole
# script on every interaction; session_state
# is how data survives those reruns.
# ==========================================

if "resume" not in st.session_state:
    st.session_state.resume = None
if "match_result" not in st.session_state:
    st.session_state.match_result = None
if "parsed_file_name" not in st.session_state:
    st.session_state.parsed_file_name = None

# ==========================================
# Header
# ==========================================

st.title("📄 Resume Analyzer")
st.caption("Parse any PDF resume and score it against a job description — powered by LangChain + Groq.")
st.divider()

# ==========================================
# Sidebar — Step 1: Upload + Parse
# ==========================================

with st.sidebar:
    st.markdown('<p class="step-label">Step 1</p>', unsafe_allow_html=True)
    st.subheader("Upload Resume")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Text-based PDFs work best. Scanned / image PDFs cannot be read.",
    )

    # Warn if the user swapped to a different file without re-parsing
    if (
        uploaded_file is not None
        and st.session_state.parsed_file_name is not None
        and uploaded_file.name != st.session_state.parsed_file_name
    ):
        st.warning(
            f"New file detected (**{uploaded_file.name}**).  \n"
            "Click **Parse Resume** to update.",
            icon="⚠️",
        )

    if uploaded_file is not None:
        if st.button("Parse Resume", type="primary", use_container_width=True):
            with st.spinner("Extracting text and parsing with LLM…"):
                try:
                    # --- Guard: empty / image-only PDF ---
                    resume_text = load_resume_text_from_bytes(uploaded_file.getvalue())
                    if not resume_text.strip():
                        st.error(
                            "No text could be extracted from this PDF.  \n"
                            "It may be a scanned or image-only file.  \n"
                            "Please upload a text-based PDF.",
                            icon="📵",
                        )
                        st.stop()

                    # --- Save a local copy for reference ---
                    save_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getvalue())

                    # --- Parse ---
                    llm = get_cached_llm()
                    resume = parse_resume(resume_text, llm=llm)

                    # --- Persist in session ---
                    st.session_state.resume = resume
                    st.session_state.match_result = None        # clear stale match
                    st.session_state.parsed_file_name = uploaded_file.name

                except Exception as exc:
                    st.error(f"Parsing failed: {exc}", icon="❌")
                    st.stop()

            st.success(f"**{uploaded_file.name}** parsed successfully!", icon="✅")

    # Progress indicator in sidebar
    st.divider()
    if st.session_state.resume:
        st.markdown("✅ &nbsp;Resume parsed")
    else:
        st.markdown("⬜ &nbsp;Resume not yet parsed")

    if st.session_state.match_result:
        st.markdown("✅ &nbsp;JD matched")
    else:
        st.markdown("⬜ &nbsp;JD not yet matched")

# ==========================================
# Main — Step 2: Parsed Resume Display
# ==========================================

if st.session_state.resume:
    resume = st.session_state.resume

    # --- Section header ---
    st.subheader("📋 Parsed Resume")

    col1, col2 = st.columns(2, gap="large")

        # ---- Left column: identity + skills ----
    with col1:
        # Open, populate, and close the candidate container in ONE single markdown block
        candidate_html = f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 1.2rem 1.4rem; margin-bottom: 1rem;">
            <p style="margin-top:0; font-weight:bold; color:#1d4ed8;">👤 Candidate</p>
            <p style="margin-bottom:0.4rem;"><strong>Name:</strong> {resume.name}</p>
            <p style="margin-bottom:0.4rem;"><strong>Email:</strong> {resume.email}</p>
            <p style="margin-bottom:0;"><strong>Phone:</strong> {resume.phone_number}</p>
        </div>
        """
        st.markdown(candidate_html, unsafe_allow_html=True)

        if resume.skills:
            # Generate the pills first, then wrap them in a single structural container string
            pills_html = "".join(f'<span class="pill">{s}</span>' for s in resume.skills)
            skills_html = f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 1.2rem 1.4rem; margin-bottom: 1rem;">
                <p style="margin-top:0; font-weight:bold; color:#1d4ed8; margin-bottom:0.6rem;">🛠 Skills</p>
                <div>{pills_html}</div>
            </div>
            """
            st.markdown(skills_html, unsafe_allow_html=True)


        # ---- Right column: education + experience ----
    with col2:
        if resume.education:
            # Generate the education list items inside a string loop
            edu_items_html = ""
            for edu in resume.education:
                gpa_str = f" — GPA: {edu.gpa}" if edu.gpa is not None else ""
                edu_items_html += f"<li style='margin-bottom:0.5rem; color: #f8fafc;'><strong>{edu.degree}</strong><br><span style='color:#94a3b8;'>{edu.university_name}{gpa_str}</span></li>"
            
            education_html = f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 1.2rem 1.4rem; margin-bottom: 1rem;">
                <p style="margin-top:0; font-weight:bold; color:#1d4ed8; margin-bottom: 0.6rem;">🎓 Education</p>
                <ul style="margin:0; padding-left:1.2rem; color: #f8fafc;">{edu_items_html}</ul>
            </div>
            """
            st.markdown(education_html, unsafe_allow_html=True)

        if resume.experience:
            # Generate the experience list items inside a string loop
            exp_items_html = ""
            for exp in resume.experience:
                company = exp.company_name if exp.company_name else "Independent"
                duration = f" ({exp.years})" if exp.years else ""
                
                project_block = f"<br><strong style='font-size:0.85rem; color:#d97706;'>🚀 Project: {exp.project_name}</strong>" if exp.project_name else ""
                tech_block = f"<br><span style='font-size:0.8rem; color:#94a3b8;'>Tech Stack: {exp.tech_stack}</span>" if exp.tech_stack else ""
                desc_block = f"<br><span style='font-size:0.85rem; font-style:italic; color: #cbd5e1;'>{exp.project_description}</span>" if exp.project_description else ""
                
                exp_items_html += f"<li style='margin-bottom:1rem; color: #f8fafc;'><strong>{company}</strong>{duration}{project_block}{tech_block}{desc_block}</li>"
            
            experience_html = f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 1.2rem 1.4rem; margin-bottom: 1rem;">
                <p style="margin-top:0; font-weight:bold; color:#1d4ed8; margin-bottom: 0.6rem;">💼 Experience</p>
                <ul style="margin:0; padding-left:1.2rem; color: #f8fafc;">{exp_items_html}</ul>
            </div>
            """
            st.markdown(experience_html, unsafe_allow_html=True)


    # ---- Projects (full width) ----
    if resume.projects:
        with st.expander(f"🗂 Projects ({len(resume.projects)} found)", expanded=False):
            for proj in resume.projects:
                cols = st.columns([3, 1])
                with cols[0]:
                    st.markdown(f"**{proj.name}**")
                    st.caption(proj.description)
                    if proj.skills:
                        pills = "".join(
                            f'<span class="pill">{s}</span>' for s in proj.skills
                        )
                        st.markdown(pills, unsafe_allow_html=True)
                with cols[1]:
                    if proj.link:
                        st.link_button("View →", proj.link)
                st.divider()

    # ---- Raw JSON download ----
    with st.expander("🔍 Raw JSON", expanded=False):
        st.json(resume.model_dump())
        st.download_button(
            label="⬇️ Download as JSON",
            data=resume.model_dump_json(indent=2),
            file_name=f"{resume.name.replace(' ', '_')}_parsed.json",
            mime="application/json",
        )

    st.divider()

    # ==========================================
    # Step 3 — JD Matching
    # ==========================================

    st.markdown('<p class="step-label">Step 2</p>', unsafe_allow_html=True)
    st.subheader("🎯 Match Against a Job Description")

    jd_text = st.text_area(
        "Paste the full job description here",
        height=220,
        placeholder="Copy and paste the job description from LinkedIn, Naukri, Internshala, etc.",
    )

    if st.button(
        "Run JD Match",
        type="primary",
        disabled=not (jd_text or "").strip(),
        use_container_width=False,
    ):
        with st.spinner("Comparing resume to job description…"):
            try:
                llm = get_cached_llm()
                match_result = match_resume_to_jd(resume, jd_text, llm=llm)
                st.session_state.match_result = match_result
            except Exception as exc:
                st.error(f"Matching failed: {exc}", icon="❌")

    # ---- Match results ----
    if st.session_state.match_result:
        match_result = st.session_state.match_result
        score = match_result.match_score

        st.subheader("📊 Match Results")

        # Score with colour-coded badge
        if score >= 70:
            score_class = "score-high"
            verdict = "Strong Match 🟢"
        elif score >= 40:
            score_class = "score-mid"
            verdict = "Partial Match 🟡"
        else:
            score_class = "score-low"
            verdict = "Weak Match 🔴"

        score_col, verdict_col, _ = st.columns([1, 2, 3])
        with score_col:
            st.markdown(
                f'<p class="{score_class}">{score:.0f}<span style="font-size:1rem;font-weight:400">/100</span></p>',
                unsafe_allow_html=True,
            )
        with verdict_col:
            st.markdown(f"**{verdict}**", unsafe_allow_html=True)

        st.divider()

        col3, col4 = st.columns(2, gap="large")

        with col3:
            # Matched skills as green pills
            st.markdown("**✅ Matched Skills**")
            if match_result.matched_skills:
                pills = "".join(
                    f'<span class="pill pill-green">{s}</span>'
                    for s in match_result.matched_skills
                )
                st.markdown(pills, unsafe_allow_html=True)
            else:
                st.caption("None found.")

            st.markdown("<br>**💪 Strengths**", unsafe_allow_html=True)
            for s in match_result.strengths:
                st.markdown(f"- {s}")

        with col4:
            # Missing skills as red pills
            st.markdown("**❌ Missing Skills**")
            if match_result.missing_skills:
                pills = "".join(
                    f'<span class="pill pill-red">{s}</span>'
                    for s in match_result.missing_skills
                )
                st.markdown(pills, unsafe_allow_html=True)
            else:
                st.caption("None — great coverage!")

            st.markdown("<br>**⚠️ Gaps**", unsafe_allow_html=True)
            for g in match_result.gaps:
                st.markdown(f"- {g}")

        st.divider()
        st.markdown("**📝 Summary**")
        st.info(match_result.summary)

# ==========================================
# Empty state — shown before any resume
# is uploaded and parsed.
# ==========================================

else:
    st.info(
        "👈 &nbsp; Upload a PDF resume from the sidebar and click **Parse Resume** to get started.",
        icon="ℹ️",
    )