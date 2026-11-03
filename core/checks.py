"""Simple ATS-friendliness checks on resume text."""
import re


def ats_checks(resume: str) -> dict:
    low = resume.lower()
    words = len(resume.split())
    checks = [
        ("Email address present", bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", resume)), "Add a professional email."),
        ("Phone number present", bool(re.search(r"(\+?\d[\d\s\-()]{8,}\d)", resume)), "Add a phone number."),
        ("Experience / projects section", bool(re.search(r"experience|projects?|internship", low)), "Add an Experience or Projects heading."),
        ("Education section", "education" in low, "Add an Education heading."),
        ("Skills section", "skills" in low, "Add a Skills heading listing tools and technologies."),
        ("Bullet points used", bool(re.search(r"^\s*[-•*▪●]", resume, re.M)), "Use bullet points for achievements."),
        ("Contains numbers / metrics", len(re.findall(r"\d+%|\d+\+|\$\d+|\b\d{2,}\b", resume)) >= 3, "Quantify results (%, counts, time saved)."),
        ("Length 250-900 words", 250 <= words <= 900, "Aim for 1 page (fresher) or 2 pages (experienced)."),
    ]
    passed = sum(1 for _, ok, _ in checks if ok)
    return {
        "score": round(100 * passed / len(checks)),
        "items": [{"check": c, "ok": ok, "hint": "" if ok else h} for c, ok, h in checks],
        "words": words,
    }
