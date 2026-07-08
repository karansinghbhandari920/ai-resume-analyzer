"""
resume_rewriter.py
Orchestration around the raw Gemini bullet-rewrite call in ai_engine.py:
pulling candidate bullet points out of a parsed resume, batching rewrites,
and packaging before/after pairs for the UI.
"""
from __future__ import annotations

from ai_engine import rewrite_bullet_point, AIEngineError
from parser import ParsedResume


def get_rewrite_candidates(parsed: ParsedResume, max_items: int = 8) -> list[str]:
    """Picks the resume's bullet points that are most worth improving:
    short, generic-sounding lines with no numbers and a weak opening verb."""
    from parser import ACTION_VERBS
    import re

    candidates = []
    for bullet in parsed.bullet_points:
        first_word = bullet.split()[0].lower().strip(".,") if bullet.split() else ""
        has_number = bool(re.search(r"\d", bullet))
        strong_verb = first_word in ACTION_VERBS
        weakness_score = (0 if strong_verb else 1) + (0 if has_number else 1)
        if weakness_score > 0:
            candidates.append((weakness_score, bullet))

    candidates.sort(key=lambda pair: pair[0], reverse=True)
    ordered = [b for _, b in candidates] or parsed.bullet_points
    return ordered[:max_items]


def rewrite_single(bullet: str, role: str | None = None) -> dict:
    """Returns {'original':..., 'rewritten':..., 'error': optional str}."""
    try:
        rewritten = rewrite_bullet_point(bullet, role=role)
        return {"original": bullet, "rewritten": rewritten, "error": None}
    except AIEngineError as exc:
        return {"original": bullet, "rewritten": None, "error": str(exc)}


def rewrite_batch(bullets: list[str], role: str | None = None) -> list[dict]:
    return [rewrite_single(b, role=role) for b in bullets]
