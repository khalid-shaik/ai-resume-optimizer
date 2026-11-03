"""Deterministic keyword matching: works offline, no LLM needed."""
import re
from collections import Counter

STOPWORDS = set("""
a about above after again all also am an and any are as at be because been before being below between both but by
can could did do does doing down during each few for from further had has have having he her here hers him his how
i if in into is it its just me more most my no nor not of off on once only or other our out over own same she should
so some such than that the their theirs them then there these they this those through to too under until up very was
we were what when where which while who whom why will with would you your yours
ability able across work working experience years year role team teams strong including include required requirements
preferred responsibilities responsible looking join candidate candidates company etc using use used well new
good great plus must may need needs ensure within knowledge skills skill job position opportunity
""".split())

SKILLS = [
    "python", "sql", "mysql", "postgresql", "sqlite", "mongodb", "excel", "power bi", "tableau", "looker",
    "pandas", "numpy", "scikit-learn", "matplotlib", "seaborn", "plotly", "pyspark", "spark", "hadoop", "airflow",
    "etl", "data cleaning", "data wrangling", "data modeling", "data visualization", "data analysis",
    "statistics", "hypothesis testing", "a/b testing", "regression", "forecasting", "machine learning",
    "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "dax", "power query", "vba",
    "dashboards", "kpi", "reporting", "storytelling", "stakeholder", "git", "github", "docker", "aws", "azure",
    "gcp", "bigquery", "snowflake", "rest api", "flask", "fastapi", "streamlit", "javascript", "java", "c++",
    "r", "agile", "scrum", "jira", "ci/cd", "linux", "communication", "problem solving",
]


def _skill_pattern(skill: str) -> re.Pattern:
    return re.compile(r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])")


_SKILL_PATTERNS = {s: _skill_pattern(s) for s in SKILLS}


def _words(text: str) -> list[str]:
    return [w.strip(".") for w in re.findall(r"[a-z][a-z0-9+#.\-]*", text.lower()) if len(w.strip(".")) > 1]


def _stem(word: str) -> str:
    return re.sub(r"(ing|ed|es|s)$", "", word) if len(word) > 4 else word


def count_occurrences(keyword: str, text: str) -> int:
    t = text.lower()
    if keyword in _SKILL_PATTERNS:
        return len(_SKILL_PATTERNS[keyword].findall(t))
    stem = _stem(keyword)
    return sum(1 for w in _words(t) if _stem(w) == stem)


def extract_keywords(job_description: str, top_n: int = 25) -> list[str]:
    jd = job_description.lower()
    skill_hits = {s: len(p.findall(jd)) for s, p in _SKILL_PATTERNS.items()}
    skills = [s for s, c in sorted(skill_hits.items(), key=lambda x: -x[1]) if c > 0]

    skill_words = {w for s in skills for w in s.split()}
    counts = Counter(
        w for w in _words(jd) if w not in STOPWORDS and len(w) >= 4 and w not in skill_words
    )
    by_stem: dict[str, str] = {}
    for w, _ in counts.most_common():
        by_stem.setdefault(_stem(w), w)
    stem_counts = Counter()
    for w, c in counts.items():
        stem_counts[_stem(w)] += c
    extras = [by_stem[s] for s, c in stem_counts.most_common() if c >= 2]
    return (skills + extras)[:top_n]


def match(resume: str, job_description: str, top_n: int = 25) -> dict:
    kws = extract_keywords(job_description, top_n)
    matched = [k for k in kws if count_occurrences(k, resume) > 0]
    missing = [k for k in kws if k not in matched]
    score = round(100 * len(matched) / len(kws)) if kws else 0
    rows = [
        {"keyword": k, "job_description": count_occurrences(k, job_description), "resume": count_occurrences(k, resume)}
        for k in kws
    ]
    return {"score": score, "keywords": kws, "matched": matched, "missing": missing, "rows": rows}
