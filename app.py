from pathlib import Path

import pandas as pd
import streamlit as st

from core import checks, export, keywords, llm, parser

st.set_page_config(page_title="AI Resume Optimizer", page_icon="📄", layout="wide")
SAMPLES = Path(__file__).parent / "samples"

st.session_state.setdefault("resume_text", "")
st.session_state.setdefault("jd_text", "")
st.session_state.setdefault("ai", None)


def load_sample():
    st.session_state.resume_text = (SAMPLES / "sample_resume.txt").read_text(encoding="utf-8")
    st.session_state.jd_text = (SAMPLES / "sample_jd.txt").read_text(encoding="utf-8")
    st.session_state.ai = None


# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")
    host = st.text_input("Ollama host", value="http://localhost:11434")
    installed = llm.list_models(host)
    if installed:
        model = st.selectbox("Model", installed)
    else:
        model = st.text_input("Model", value="llama3.2")
        st.warning("Ollama not detected. Start it and run `ollama pull llama3.2`. The keyword and ATS checks still work offline.")
    temperature = st.slider("Creativity", 0.0, 1.0, 0.3, 0.1)
    st.button("Load sample data", on_click=load_sample, use_container_width=True)
    st.caption("Everything runs locally. Your resume is never uploaded anywhere.")

st.title("📄 AI Resume Optimizer")
st.caption("Match your resume to a job description, fix ATS issues and get AI-written improvements.")

# ---------- Inputs ----------
left, right = st.columns(2)
with left:
    st.subheader("1. Your resume")
    upload = st.file_uploader("Upload PDF, DOCX or TXT", type=["pdf", "docx", "txt", "md"])
    if upload:
        try:
            resume = parser.extract_text(upload.getvalue(), upload.name)
            st.success(f"Read {len(resume.split())} words from {upload.name}")
        except ValueError as e:
            st.error(str(e))
            resume = ""
    else:
        resume = st.text_area("...or paste your resume text", key="resume_text", height=280)
with right:
    st.subheader("2. Job description")
    jd = st.text_area("Paste the job description", key="jd_text", height=395)

if not resume.strip() or not jd.strip():
    st.info("Add a resume and a job description (or click **Load sample data** in the sidebar) to begin.")
    st.stop()

# ---------- Offline analysis (instant) ----------
kw = keywords.match(resume, jd)
ats = checks.ats_checks(resume)

c1, c2, c3 = st.columns(3)
c1.metric("Keyword match", f"{kw['score']}%")
c2.metric("ATS format score", f"{ats['score']}%")
c3.metric("AI match score", f"{st.session_state.ai['match_score']}%" if st.session_state.ai else "run AI below")

if st.button("🤖 Get AI feedback", type="primary"):
    with st.spinner(f"Asking {model}... (first run can take a minute)"):
        try:
            st.session_state.ai = llm.analyze(resume, jd, kw["missing"], model, host, temperature)
            st.rerun()
        except Exception as e:
            st.error(f"Could not get AI feedback: {e}")

ai = st.session_state.ai
tab1, tab2, tab3, tab4 = st.tabs(["🔑 Keywords", "✅ ATS checks", "🤖 AI feedback", "⬇️ Export"])

with tab1:
    a, b = st.columns(2)
    a.markdown("**Matched** ✅")
    a.write(", ".join(kw["matched"]) or "None")
    b.markdown("**Missing** ❌ (add only if you truly have the skill)")
    b.write(", ".join(kw["missing"]) or "None")
    if kw["rows"]:
        df = pd.DataFrame(kw["rows"]).rename(columns={"job_description": "Job description", "resume": "Resume"})
        st.bar_chart(df.set_index("keyword")[["Job description", "Resume"]])

with tab2:
    st.progress(ats["score"] / 100, text=f"{ats['score']}% of checks passed ({ats['words']} words)")
    for item in ats["items"]:
        st.write(("✅ " if item["ok"] else "⚠️ ") + item["check"] + (f" - {item['hint']}" if item["hint"] else ""))

with tab3:
    if not ai:
        st.info("Click **Get AI feedback** above. Requires Ollama running locally.")
    else:
        st.subheader("Verdict")
        st.write(ai["summary"])
        s, w = st.columns(2)
        s.markdown("**Strengths**")
        for x in ai["strengths"]:
            s.write(f"- {x}")
        w.markdown("**Weaknesses**")
        for x in ai["weaknesses"]:
            w.write(f"- {x}")
        st.subheader("Tailored summary")
        st.code(ai["tailored_summary"], language=None, wrap_lines=True)
        st.subheader("Rewritten bullets")
        for bl in ai["rewritten_bullets"]:
            st.markdown(f"~~{bl['original']}~~")
            st.success(bl["improved"])
        st.subheader("Tips")
        for x in ai["tips"]:
            st.write(f"- {x}")
        st.caption("Review every rewrite: replace placeholders like [X%] with real numbers and never claim skills you do not have.")

with tab4:
    st.download_button("Download report (.docx)", export.to_docx(kw, ats, ai), "resume_report.docx",
                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    st.download_button("Download report (.md)", export.to_markdown(kw, ats, ai), "resume_report.md", "text/markdown")
