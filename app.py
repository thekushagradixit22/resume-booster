"""
AI Resume Analyzer & ATS Scanner
--------------------------------
A Streamlit app that uses Google's Gemini API (free tier) to compare a resume
(PDF) against a job description and return a structured ATS-style analysis:
match score, matched keywords, missing keywords, and actionable suggestions.

Deploy on Streamlit Community Cloud with your GEMINI_API_KEY set in
st.secrets (see README / deployment instructions). Get a free key with no
credit card at https://aistudio.google.com/app/apikey
"""

import json

import streamlit as st
from PyPDF2 import PdfReader
from pydantic import BaseModel
from google import genai
from google.genai import types
from google.genai import errors as genai_errors

# --------------------------------------------------------------------------
# Page configuration
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer & ATS Scanner",
    page_icon="📄",
    layout="wide",
)

# gemini-2.5-flash is on Google AI Studio's free tier (no credit card required).
# If you hit free-tier rate limits, gemini-2.5-flash-lite has more generous limits.
MODEL_NAME = "gemini-2.5-flash"

SYSTEM_PROMPT = """You are an expert technical recruiter and Applicant Tracking System (ATS) \
scanning specialist with 15+ years of experience hiring for technical and non-technical roles. \
You have deep knowledge of how modern ATS software (Workday, Greenhouse, Lever, Taleo) parses \
and ranks resumes against job descriptions.

You will be given a candidate's RESUME TEXT and a JOB DESCRIPTION. Your task is to analyze how \
well the resume matches the job description, exactly as an ATS + human recruiter combination would.

Evaluate:
1. Keyword and skills overlap (technical skills, tools, certifications, soft skills, job titles).
2. Relevant experience alignment with the role's core responsibilities.
3. Missing hard requirements (skills/qualifications explicitly in the JD but absent from the resume).

Rules:
- match_score reflects realistic ATS + recruiter alignment (be strict and honest, not generous).
- matched_keywords and missing_keywords should be specific terms pulled from the job description \
(skills, tools, technologies, certifications, methodologies), not generic words.
- Provide exactly 3 suggestions, each concrete and specific to this resume and this job \
description (e.g., "Add a bullet quantifying your experience with X" rather than vague advice).
- Do not invent experience the candidate does not have; suggestions should be about how to better \
surface, phrase, or quantify existing experience, or which missing skills to address.
"""


class ResumeAnalysis(BaseModel):
    match_score: int
    score_summary: str
    matched_keywords: list[str]
    missing_keywords: list[str]
    suggestions: list[str]


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract all text from an uploaded PDF file object."""
    reader = PdfReader(uploaded_file)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_parts.append(page_text)
    return "\n".join(text_parts).strip()


def get_api_key() -> str | None:
    """Fetch the Gemini API key from Streamlit secrets."""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        return None


def call_gemini(resume_text: str, job_description: str, api_key: str) -> dict:
    """Send resume + JD to Gemini and return the parsed JSON analysis."""
    client = genai.Client(api_key=api_key)

    user_message = f"""RESUME TEXT:
---
{resume_text}
---

JOB DESCRIPTION:
---
{job_description}
---

Analyze the resume against the job description and return the structured analysis."""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=ResumeAnalysis,
            temperature=0.3,
        ),
    )

    return json.loads(response.text)


def score_color(score: int) -> str:
    if score >= 75:
        return "#16a34a"  # green
    if score >= 50:
        return "#eab308"  # yellow
    return "#dc2626"  # red


def render_results(result: dict):
    score = int(result.get("match_score", 0))
    summary = result.get("score_summary", "")
    matched = result.get("matched_keywords", [])
    missing = result.get("missing_keywords", [])
    suggestions = result.get("suggestions", [])

    st.markdown("## 📊 ATS Match Results")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(
            f"""
            <div style="text-align:center; padding: 1.5rem; border-radius: 12px;
                        border: 2px solid {score_color(score)}; background: rgba(0,0,0,0.02);">
                <div style="font-size: 3rem; font-weight: 800; color: {score_color(score)};">
                    {score}%
                </div>
                <div style="font-size: 0.9rem; color: #666;">ATS Match Score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.progress(min(max(score, 0), 100) / 100)
        if summary:
            st.write(summary)

    st.divider()

    col_match, col_miss = st.columns(2)
    with col_match:
        st.markdown("### ✅ Matched Keywords")
        if matched:
            st.markdown(
                " ".join(
                    f'<span style="background:#dcfce7;color:#166534;padding:4px 10px;'
                    f'border-radius:14px;margin:3px;display:inline-block;font-size:0.85rem;">{kw}</span>'
                    for kw in matched
                ),
                unsafe_allow_html=True,
            )
        else:
            st.caption("No strong keyword matches found.")

    with col_miss:
        st.markdown("### ⚠️ Missing Keywords (Skills Gap)")
        if missing:
            st.markdown(
                " ".join(
                    f'<span style="background:#fee2e2;color:#991b1b;padding:4px 10px;'
                    f'border-radius:14px;margin:3px;display:inline-block;font-size:0.85rem;">{kw}</span>'
                    for kw in missing
                ),
                unsafe_allow_html=True,
            )
        else:
            st.caption("No significant gaps found. 🎉")

    st.divider()

    st.markdown("### 💡 Actionable Suggestions")
    for i, tip in enumerate(suggestions, start=1):
        st.markdown(f"**{i}.** {tip}")


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 📄 About")
    st.write(
        "This tool uses Google's Gemini API (free tier) to analyze how well your resume "
        "matches a job description, the same way an ATS + recruiter would."
    )
    st.markdown("### How it works")
    st.markdown(
        "1. Upload your resume (PDF)\n"
        "2. Paste the job description\n"
        "3. Click **Analyze Resume**\n"
        "4. Review your ATS score, keyword gaps, and tips"
    )
    st.markdown("---")
    st.caption(
        "Your resume and job description are sent to the Gemini API for analysis. "
        "Note: on Google's free tier, prompts may be used to improve their models — "
        "avoid uploading highly sensitive personal data."
    )

# --------------------------------------------------------------------------
# Main UI
# --------------------------------------------------------------------------
st.title("📄 AI Resume Analyzer & ATS Scanner")
st.write(
    "Upload your resume and paste a job description to get an instant ATS match score, "
    "keyword gap analysis, and tailored suggestions — powered by Google Gemini (free tier)."
)

api_key = get_api_key()
if not api_key:
    st.warning(
        "⚠️ No Gemini API key found. Get a free key (no credit card) at "
        "https://aistudio.google.com/app/apikey, then add it as `GEMINI_API_KEY` to your "
        "Streamlit secrets (`.streamlit/secrets.toml` locally, or the **Secrets** section in "
        "Streamlit Community Cloud) before analyzing."
    )

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 1. Upload Resume (PDF)")
    resume_file = st.file_uploader("Choose a PDF file", type=["pdf"])

with col_right:
    st.markdown("### 2. Paste Job Description")
    job_description = st.text_area(
        "Job description text",
        height=260,
        placeholder="Paste the full job description here...",
        label_visibility="collapsed",
    )

analyze_clicked = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)

if analyze_clicked:
    if not api_key:
        st.error("Cannot analyze: no Gemini API key configured in `st.secrets`.")
    elif not resume_file:
        st.error("Please upload a resume PDF.")
    elif not job_description or not job_description.strip():
        st.error("Please paste a job description.")
    else:
        try:
            with st.spinner("Extracting text from your resume..."):
                resume_text = extract_text_from_pdf(resume_file)

            if not resume_text:
                st.error(
                    "Couldn't extract any text from that PDF. It may be a scanned image "
                    "without a text layer — try a different file."
                )
            else:
                with st.spinner("Asking Gemini to analyze your resume against the job description..."):
                    result = call_gemini(resume_text, job_description, api_key)
                render_results(result)

        except json.JSONDecodeError:
            st.error(
                "Gemini returned a response that couldn't be parsed as JSON. "
                "Please try again."
            )
        except genai_errors.ClientError as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                st.error(
                    "Free-tier rate limit hit. Wait a minute and try again, or switch "
                    "MODEL_NAME to `gemini-2.5-flash-lite` for higher free-tier limits."
                )
            else:
                st.error(f"Gemini API request error: {e}")
        except genai_errors.ServerError as e:
            st.error(f"Gemini API server error, please try again shortly: {e}")
        except Exception as e:  # noqa: BLE001
            st.error(f"Something went wrong: {e}")
