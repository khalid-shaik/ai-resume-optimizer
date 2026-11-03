from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def test_app_runs_with_sample_data():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    [b for b in at.sidebar.button if b.label == "Load sample data"][0].click().run()
    assert not at.exception
    assert any(m.label == "Keyword match" for m in at.metric)


def test_app_renders_ai_feedback(monkeypatch):
    from core import llm

    fake = llm.normalize({
        "match_score": 78, "summary": "Good fit.", "strengths": ["SQL"], "weaknesses": ["No cloud"],
        "tailored_summary": "Data analyst.", "tips": ["Add metrics"],
        "rewritten_bullets": [{"original": "Built dashboard", "improved": "Built Power BI dashboard cutting reporting time by [X%]"}],
    })
    monkeypatch.setattr(llm, "analyze", lambda *a, **k: fake)
    monkeypatch.setattr(llm, "list_models", lambda host=None: ["llama3.2:latest"])
    at = AppTest.from_file(APP, default_timeout=30).run()
    [b for b in at.sidebar.button if b.label == "Load sample data"][0].click().run()
    [b for b in at.button if "AI feedback" in b.label][0].click().run()
    assert not at.exception
    assert any(m.value == "78%" for m in at.metric)
