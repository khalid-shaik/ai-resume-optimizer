"""Build downloadable reports (DOCX and Markdown)."""
from io import BytesIO

from docx import Document


def _bullets(doc, items):
    for i in items:
        doc.add_paragraph(i, style="List Bullet")


def to_markdown(kw: dict, ats: dict, ai: dict | None) -> str:
    out = ["# Resume Optimization Report", "",
           f"- Keyword match: **{kw['score']}%**", f"- ATS format score: **{ats['score']}%**"]
    if ai:
        out += [f"- AI match score: **{ai['match_score']}%**", "", "## Summary", ai["summary"]]
    out += ["", "## Matched keywords", ", ".join(kw["matched"]) or "-",
            "", "## Missing keywords", ", ".join(kw["missing"]) or "-", "", "## ATS format checks"]
    out += [f"- {'PASS' if i['ok'] else 'FIX'}: {i['check']} {i['hint']}".strip() for i in ats["items"]]
    if ai:
        for title, key in [("Strengths", "strengths"), ("Weaknesses", "weaknesses"), ("Tips", "tips")]:
            out += ["", f"## {title}"] + [f"- {x}" for x in ai[key]]
        out += ["", "## Tailored summary", ai["tailored_summary"], "", "## Rewritten bullets"]
        for b in ai["rewritten_bullets"]:
            out += [f"- Before: {b['original']}", f"  After: {b['improved']}"]
    return "\n".join(out)


def to_docx(kw: dict, ats: dict, ai: dict | None) -> bytes:
    doc = Document()
    doc.add_heading("Resume Optimization Report", 0)
    doc.add_paragraph(f"Keyword match: {kw['score']}%   |   ATS format score: {ats['score']}%"
                      + (f"   |   AI match score: {ai['match_score']}%" if ai else ""))
    if ai and ai["summary"]:
        doc.add_heading("Summary", 1)
        doc.add_paragraph(ai["summary"])
    doc.add_heading("Keywords", 1)
    doc.add_paragraph("Matched: " + (", ".join(kw["matched"]) or "-"))
    doc.add_paragraph("Missing: " + (", ".join(kw["missing"]) or "-"))
    doc.add_heading("ATS format checks", 1)
    _bullets(doc, [f"{'PASS' if i['ok'] else 'FIX'} - {i['check']}. {i['hint']}".strip() for i in ats["items"]])
    if ai:
        for title, key in [("Strengths", "strengths"), ("Weaknesses", "weaknesses"), ("Tips", "tips")]:
            doc.add_heading(title, 1)
            _bullets(doc, ai[key])
        doc.add_heading("Tailored professional summary", 1)
        doc.add_paragraph(ai["tailored_summary"])
        doc.add_heading("Rewritten bullet points", 1)
        for b in ai["rewritten_bullets"]:
            p = doc.add_paragraph()
            p.add_run("Before: ").bold = True
            p.add_run(b["original"])
            p = doc.add_paragraph()
            p.add_run("After: ").bold = True
            p.add_run(b["improved"])
    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()
