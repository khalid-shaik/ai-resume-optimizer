# 📄 AI Resume Optimizer

**Project  AI agents.** Upload a resume, paste a job description, and get:

- **Keyword match score** and a matched/missing keyword chart (instant, works offline)
- **ATS format checks** (contact info, sections, bullets, metrics, length)
- **AI feedback** from a *local* LLM via Ollama: strengths, weaknesses, a tailored summary, rewritten bullets and tips
- **Export** a report as DOCX or Markdown

Your resume never leaves your machine.

## Tech stack
Python · Streamlit · Ollama · pypdf · python-docx · pandas · pytest · GitHub Actions

## Quick start
```bash
# 1. Install Ollama from https://ollama.com, then:
ollama pull llama3.2

# 2. Set up Python (Windows PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```
Click **Load sample data** in the sidebar to try it instantly.

## Project structure
```
app.py            Streamlit UI
core/parser.py    PDF / DOCX / TXT text extraction
core/keywords.py  keyword extraction + match score (no LLM)
core/checks.py    ATS format checks
core/llm.py       Ollama call, JSON parsing and validation
core/export.py    DOCX / Markdown report
tests/            pytest unit + UI tests
samples/          demo resume and job description
```

## Run tests
```bash
pytest -q
```

## How it works
1. Text is extracted from the resume.
2. Keywords are pulled from the job description (curated skills list + frequent terms) and matched against the resume.
3. The local model receives the resume, the job description and the missing keywords, and returns structured JSON that is validated before display.
4. The AI never invents metrics: where numbers are unknown it writes placeholders like `[X%]` for you to fill in.

## Roadmap
- [ ] Scanned-PDF OCR
- [ ] Multiple job descriptions at once
- [ ] Export an improved resume as DOCX

## Screenshots
Add screenshots here (`docs/` folder).
