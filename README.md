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
A<img width="1870" height="845" alt="Screenshot 2026-11-03 133041" src="https://github.com/user-attachments/assets/e983c0e6-f0d0-4b4c-a878-f7a32255e772" />
<img width="1722" height="782" alt="Screenshot 2026-09-19 225626" src="https://github.com/user-attachments/assets/008c640f-e6ce-45cb-85e8-acc7c37f62ab" />
<img width="1868" height="852" alt="Screenshot 2026-11-03 133009" src="https://github.com/user-attachments/assets/d8defd9f-6049-4986-b404-b4ab05a1cd9e" />
