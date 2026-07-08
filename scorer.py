"""
scorer.py
The ATS Score Engine. Combines signals from the parsed resume into a single
0-100 score with a letter grade and a component breakdown, mirroring how
real ATS / resume-screening tools weight these factors.

Weighting (100 pts total):
    Skills Match            30
    Resume Sections         15
    Contact Information     10
    Action Verbs            15
    Quantified Achievements 15
    Readability             10
    Word Count                5
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from parser import ParsedResume, ResumeParser, SECTION_HEADERS
from skills import ROLE_REQUIREMENTS
from utils import word_count


WEIGHTS = {
    "skills_match": 30,
    "resume_sections": 15,
    "contact_information": 10,
    "action_verbs": 15,
    "quantified_achievements": 15,
    "readability": 10,
    "word_count": 5,
}


@dataclass
class ATSResult:
    overall_score: float
    grade: str
    breakdown: dict[str, float]
    tips: list[str]


def _flesch_reading_ease(text: str) -> float:
    """Standard Flesch Reading Ease formula, computed without extra deps."""
    sentences = max(1, len(re.findall(r"[.!?]+", text)))
    words = max(1, len(re.findall(r"\b[a-zA-Z']+\b", text)))
    syllables = sum(_count_syllables(w) for w in re.findall(r"\b[a-zA-Z']+\b", text))
    score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    return max(0.0, min(100.0, score))


def _count_syllables(word: str) -> int:
    word = word.lower()
    vowels = "aeiouy"
    count, prev_was_vowel = 0, False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_was_vowel:
            count += 1
        prev_was_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


class ATSScorer:
    def __init__(self, text: str, parsed: ParsedResume, role: str | None = None):
        self.text = text
        self.parsed = parsed
        self.role = role

    def score_contact_info(self) -> float:
        points, total = 0, 4
        if self.parsed.email:
            points += 1
        if self.parsed.phone:
            points += 1
        if self.parsed.linkedin:
            points += 1
        if self.parsed.github:
            points += 1
        return (points / total) * WEIGHTS["contact_information"]

    def score_sections(self) -> float:
        expected = len(SECTION_HEADERS)
        found = len(self.parsed.sections_found)
        return (found / expected) * WEIGHTS["resume_sections"]

    def score_skills_match(self) -> float:
        found_skills = set(self.parsed.skills)
        if self.role and self.role in ROLE_REQUIREMENTS:
            profile = ROLE_REQUIREMENTS[self.role]
            target = set(profile["required"]) | set(profile["nice_to_have"])
            if not target:
                return 0.0
            hit = len(found_skills & target)
            return min(1.0, hit / max(1, len(profile["required"]))) * WEIGHTS["skills_match"]
        # No role selected: score on breadth of detected skills, capped.
        return min(1.0, len(found_skills) / 12) * WEIGHTS["skills_match"]

    def score_action_verbs(self) -> float:
        parser_obj = ResumeParser(self.text)
        ratio = parser_obj.action_verb_ratio()
        return ratio * WEIGHTS["action_verbs"]

    def score_quantified_achievements(self) -> float:
        parser_obj = ResumeParser(self.text)
        ratio = parser_obj.quantified_ratio()
        return ratio * WEIGHTS["quantified_achievements"]

    def score_readability(self) -> float:
        ease = _flesch_reading_ease(self.text)
        # Ideal resume readability sits around 50-70 (fairly easy / plain
        # business English) - too simple or too dense both lose points.
        if 50 <= ease <= 70:
            normalized = 1.0
        else:
            distance = min(abs(ease - 50), abs(ease - 70)) if ease < 50 or ease > 70 else 0
            normalized = max(0.0, 1 - distance / 50)
        return normalized * WEIGHTS["readability"]

    def score_word_count(self) -> float:
        count = word_count(self.text)
        if 400 <= count <= 800:
            normalized = 1.0
        elif count < 400:
            normalized = count / 400
        else:
            normalized = max(0.0, 1 - (count - 800) / 800)
        return normalized * WEIGHTS["word_count"]

    def calculate(self) -> ATSResult:
        breakdown = {
            "Skills Match": round(self.score_skills_match(), 1),
            "Resume Sections": round(self.score_sections(), 1),
            "Contact Information": round(self.score_contact_info(), 1),
            "Action Verbs": round(self.score_action_verbs(), 1),
            "Quantified Achievements": round(self.score_quantified_achievements(), 1),
            "Readability": round(self.score_readability(), 1),
            "Word Count": round(self.score_word_count(), 1),
        }
        overall = round(sum(breakdown.values()), 1)
        grade = _grade_for(overall)
        tips = generate_tips(breakdown, self.parsed)
        return ATSResult(overall_score=overall, grade=grade, breakdown=breakdown, tips=tips)


def _grade_for(score: float) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def generate_tips(breakdown: dict[str, float], parsed: ParsedResume) -> list[str]:
    tips = []
    if breakdown["Contact Information"] < WEIGHTS["contact_information"] * 0.75:
        missing = []
        if not parsed.email:
            missing.append("email")
        if not parsed.phone:
            missing.append("phone number")
        if not parsed.linkedin:
            missing.append("LinkedIn URL")
        if not parsed.github:
            missing.append("GitHub URL")
        if missing:
            tips.append(f"Add your {', '.join(missing)} near the top of your resume.")
    if breakdown["Resume Sections"] < WEIGHTS["resume_sections"] * 0.75:
        present = set(parsed.sections_found)
        missing_sections = [s for s in SECTION_HEADERS if s not in present]
        if missing_sections:
            tips.append(f"Add clear section headers for: {', '.join(missing_sections)}.")
    if breakdown["Action Verbs"] < WEIGHTS["action_verbs"] * 0.6:
        tips.append("Start more bullet points with strong action verbs (e.g. 'Built', 'Led', 'Optimized').")
    if breakdown["Quantified Achievements"] < WEIGHTS["quantified_achievements"] * 0.6:
        tips.append("Quantify your impact with numbers - %, $, time saved, users reached, etc.")
    if breakdown["Skills Match"] < WEIGHTS["skills_match"] * 0.6:
        tips.append("Your detected skill set is thin for the selected role - add relevant tools and technologies you've used.")
    if breakdown["Word Count"] < WEIGHTS["word_count"] * 0.75:
        tips.append("Aim for roughly 400-800 words - long enough to show depth, short enough to stay scannable.")
    if not tips:
        tips.append("Solid resume! Fine-tune wording and keep tailoring it per job description for the best results.")
    return tips
