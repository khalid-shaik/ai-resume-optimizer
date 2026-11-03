from io import BytesIO

import pytest
from docx import Document

from core import checks, export, keywords, llm, parser

RESUME = "Skills: Python, SQL, Excel, Power BI.\n- Built dashboards with 95% accuracy"
JD = "We need Python, SQL, Tableau and Power BI experience. SQL is essential. Dashboards and reporting."


def test_extract_keywords_finds_skills():
    kws = keywords.extract_keywords(JD)
    assert "sql" in kws and "tableau" in kws and "power bi" in kws


def test_match_score_and_missing():
    m = keywords.match(RESUME, JD)
    assert "tableau" in m["missing"]
    assert "python" in m["matched"]
    assert 0 < m["score"] < 100


def test_c_plus_plus_not_confused_with_c():
    assert keywords.count_occurrences("c++", "I know c++ well") == 1
    assert keywords.count_occurrences("java", "javascript only") == 0


def test_ats_checks_has_score():
    r = checks.ats_checks(RESUME)
    assert 0 <= r["score"] <= 100 and len(r["items"]) == 8


def test_parse_txt_and_unsupported():
    assert parser.extract_text(b"hello  world", "a.txt") == "hello world"
    with pytest.raises(ValueError):
        parser.extract_text(b"x", "a.exe")


def test_parse_docx_roundtrip():
    d = Document()
    d.add_paragraph("Python developer")
    buf = BytesIO()
    d.save(buf)
    assert "Python developer" in parser.extract_text(buf.getvalue(), "cv.docx")


def test_llm_parse_json_with_noise_and_normalize():
    raw = 'Here you go: {"match_score": "82", "rewritten_bullets": [{"original": "a", "improved": "b"}], "tips": "bad"}'
    out = llm.normalize(llm.parse_json(raw))
    assert out["match_score"] == 82 and out["tips"] == [] and out["rewritten_bullets"][0]["improved"] == "b"
    with pytest.raises(ValueError):
        llm.parse_json("no json here")


def test_export_docx_and_md():
    m = keywords.match(RESUME, JD)
    a = checks.ats_checks(RESUME)
    ai = llm.normalize({"match_score": 70, "summary": "ok", "tailored_summary": "x",
                        "rewritten_bullets": [{"original": "o", "improved": "i"}]})
    data = export.to_docx(m, a, ai)
    assert "Resume Optimization Report" in Document(BytesIO(data)).paragraphs[0].text
    assert "AI match score" in export.to_markdown(m, a, ai)
    assert export.to_docx(m, a, None)
