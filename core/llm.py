"""Local LLM analysis through Ollama, returning structured JSON."""
import json
import re

import ollama

MAX_CHARS = 6000

SYSTEM = (
    "You are an expert ATS resume reviewer and career coach. Be specific and honest. "
    "Never invent experience, employers, degrees or numbers the candidate did not provide. "
    "Reply with a single valid JSON object only."
)

SCHEMA = """{
  "match_score": <integer 0-100>,
  "summary": "<2 sentence overall verdict>",
  "strengths": ["..."],
  "weaknesses": ["..."],
  "missing_skills": ["..."],
  "rewritten_bullets": [{"original": "<line from resume>", "improved": "<action verb + task + tool + measurable impact>"}],
  "tailored_summary": "<3 line professional summary tailored to the job, using only facts from the resume>",
  "tips": ["..."]
}"""


def build_prompt(resume: str, jd: str, missing_keywords: list[str]) -> str:
    return (
        f"JOB DESCRIPTION:\n{jd[:MAX_CHARS]}\n\nRESUME:\n{resume[:MAX_CHARS]}\n\n"
        f"Keywords from the job description that look missing in the resume: {', '.join(missing_keywords) or 'none'}\n\n"
        f"Return JSON in exactly this shape (3-6 rewritten_bullets, use real lines from the resume as 'original'; "
        f"where the resume has no metric, write a placeholder like [X%] instead of making one up):\n{SCHEMA}"
    )


def parse_json(raw: str) -> dict:
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.S)
        if not m:
            raise ValueError("Model did not return JSON.")
        return json.loads(m.group(0))


def _list(v) -> list:
    return [str(x) for x in v] if isinstance(v, list) else []


def normalize(d: dict) -> dict:
    bullets = []
    for b in d.get("rewritten_bullets", []) if isinstance(d.get("rewritten_bullets"), list) else []:
        if isinstance(b, dict) and b.get("improved"):
            bullets.append({"original": str(b.get("original", "")), "improved": str(b["improved"])})
    try:
        score = max(0, min(100, int(d.get("match_score", 0))))
    except (TypeError, ValueError):
        score = 0
    return {
        "match_score": score,
        "summary": str(d.get("summary", "")),
        "strengths": _list(d.get("strengths")),
        "weaknesses": _list(d.get("weaknesses")),
        "missing_skills": _list(d.get("missing_skills")),
        "rewritten_bullets": bullets,
        "tailored_summary": str(d.get("tailored_summary", "")),
        "tips": _list(d.get("tips")),
    }


def list_models(host: str | None = None) -> list[str]:
    try:
        client = ollama.Client(host=host) if host else ollama.Client()
        resp = client.list()
        models = resp["models"] if isinstance(resp, dict) else resp.models
        names = [(m["model"] if isinstance(m, dict) else m.model) for m in models]
        return sorted(names)
    except Exception:
        return []


def analyze(resume: str, jd: str, missing_keywords: list[str], model: str = "llama3.2",
            host: str | None = None, temperature: float = 0.3) -> dict:
    client = ollama.Client(host=host) if host else ollama.Client()
    resp = client.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": build_prompt(resume, jd, missing_keywords)},
        ],
        format="json",
        options={"temperature": temperature},
    )
    content = resp["message"]["content"] if isinstance(resp, dict) else resp.message.content
    return normalize(parse_json(content))
