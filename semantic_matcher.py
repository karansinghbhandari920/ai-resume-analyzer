"""
semantic_matcher.py
Job Description Matcher: scores how well a resume semantically matches a
pasted job description, independent of exact keyword overlap (e.g. "led a
team" should partially match "leadership experience"). Falls back to a
TF-IDF cosine similarity if sentence-transformers / the embedding model
isn't available in the environment, so the feature degrades gracefully
rather than crashing.
"""
from __future__ import annotations

import re

import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity

from skills import SKILL_TAXONOMY


@st.cache_resource(show_spinner=False)
def _embedding_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("all-MiniLM-L6-v2")


def _semantic_similarity(resume_text: str, jd_text: str) -> float:
    try:
        model = _embedding_model()
        embeddings = model.encode([resume_text, jd_text])
        sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return float(max(0.0, min(1.0, sim)))
    except Exception:
        return _tfidf_similarity(resume_text, jd_text)


def _tfidf_similarity(resume_text: str, jd_text: str) -> float:
    from sklearn.feature_extraction.text import TfidfVectorizer

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([resume_text, jd_text])
    sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    return float(max(0.0, min(1.0, sim)))


def _skills_in_text(text: str) -> set[str]:
    lowered = text.lower()
    found = set()
    for canonical, patterns in SKILL_TAXONOMY.items():
        for pat in patterns:
            if re.search(rf"(?<![A-Za-z0-9]){pat}(?![A-Za-z0-9])", lowered):
                found.add(canonical)
                break
    return found


def _extract_keywords(jd_text: str, top_n: int = 25) -> list[str]:
    """Light keyword extraction from the JD for the 'missing keywords' list -
    pulls capitalized terms and taxonomy skills mentioned, since full topic
    modeling is overkill for a single job description."""
    keywords = set(_skills_in_text(jd_text))
    # Also catch multi-word capitalized phrases like "Google Cloud Platform"
    for match in re.finditer(r"\b([A-Z][a-zA-Z0-9+.#]*(?:\s[A-Z][a-zA-Z0-9+.#]*){0,2})\b", jd_text):
        phrase = match.group(1).strip()
        if 2 <= len(phrase) <= 40 and phrase.lower() not in {"the", "and", "for"}:
            keywords.add(phrase)
    return list(keywords)[:top_n]


def match_resume_to_job(resume_text: str, jd_text: str) -> dict:
    """Returns match_percent, matching_skills, missing_keywords, and a
    semantic similarity score the UI can show as a secondary metric."""
    semantic_score = _semantic_similarity(resume_text, jd_text)

    resume_skills = _skills_in_text(resume_text)
    jd_skills = _skills_in_text(jd_text)

    matching_skills = sorted(resume_skills & jd_skills)
    missing_keywords = sorted(jd_skills - resume_skills)

    keyword_overlap_ratio = len(matching_skills) / len(jd_skills) if jd_skills else 1.0

    # Blend semantic similarity (captures phrasing/context) with explicit
    # keyword overlap (captures hard ATS-style requirements) - 50/50.
    match_percent = round(((semantic_score * 0.5) + (keyword_overlap_ratio * 0.5)) * 100, 1)

    return {
        "match_percent": match_percent,
        "semantic_score": round(semantic_score * 100, 1),
        "keyword_overlap_percent": round(keyword_overlap_ratio * 100, 1),
        "matching_skills": matching_skills,
        "missing_keywords": missing_keywords if missing_keywords else _extract_keywords(jd_text)[:10],
        "jd_skills_detected": sorted(jd_skills),
    }
