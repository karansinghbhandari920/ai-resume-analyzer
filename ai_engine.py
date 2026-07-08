"""
ai_engine.py
All calls to the generative model (Google Gemini) live here. Every public
function fails soft: if GEMINI_API_KEY isn't configured or the API call
errors out, we return a dict/string with an "error" explanation instead of
raising, so a missing key degrades one feature instead of crashing the app.
"""
from __future__ import annotations

import json
import os
import re
import random
import streamlit as st

from utils import truncate


class AIEngineError(Exception):
    pass


@st.cache_resource(show_spinner=False)
def _model():
    from groq import Groq

    api_key = os.environ.get("GROQ_API_KEY", "")

    if not api_key:
        raise AIEngineError(
            "GROQ_API_KEY is not set. Add it to your .env file."
        )

    return Groq(api_key=api_key)


def _generate_text(prompt: str, temperature: float = 0.6) -> str:
    try:
        model = _model()
        response = model.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
        {
            "role": "user",
            "content": prompt
        }
        ],
        temperature=temperature,
         max_tokens=1024,
        )

        return response.choices[0].message.content.strip()
    except AIEngineError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise AIEngineError(f"Groq request failed: {exc}") from exc


def _generate_json(prompt: str, temperature: float = 0.4) -> dict:
    full_prompt = (
        f"{prompt}\n\n"
        "Respond with ONLY valid JSON. No markdown fences, no commentary, no preamble."
    )
    raw = _generate_text(full_prompt, temperature=temperature)

    print("=" * 80)
    print("RAW AI RESPONSE:")
    print(raw)
    print("=" * 80)

    cleaned = re.sub(
        r"^```(?:json)?|```$",
        "",
        raw.strip(),
        flags=re.MULTILINE,
    ).strip()

    print("CLEANED RESPONSE:")
    print(cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Last resort: grab the largest {...} block in the response
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        raise AIEngineError("The AI response could not be parsed. Please try again.")


# --------------------------------------------------------------------------- #
# 7. AI Resume Review
# --------------------------------------------------------------------------- #
def generate_resume_review(resume_text: str, role: str | None = None) -> dict:
    role_line = f"The candidate is targeting the role: {role}." if role else "No specific target role was given."
    prompt = f"""
You are a senior technical recruiter reviewing a resume. {role_line}

RESUME:
{truncate(resume_text)}

Return a JSON object with exactly these keys:
- "summary": a 2-3 sentence overview of the candidate's profile
- "strengths": array of 3-5 short strings
- "weaknesses": array of 3-5 short strings
- "missing_skills": array of skills/keywords that would strengthen this resume for the target role
- "improvement_suggestions": array of 3-6 specific, actionable suggestions
- "recruiter_verdict": one short paragraph giving a frank hiring-manager verdict
"""
    return _generate_json(prompt)


# --------------------------------------------------------------------------- #
# 8. AI Bullet Rewriter (raw model call - orchestration lives in resume_rewriter.py)
# --------------------------------------------------------------------------- #
def rewrite_bullet_point(bullet: str, role: str | None = None) -> str:
    role_line = f"for a {role} resume" if role else ""
    prompt = f"""
Rewrite this resume bullet point {role_line} to be more impactful: use a strong
action verb, be specific, and add a plausible quantified outcome if none exists
(keep it realistic, don't invent absurd numbers). Return ONLY the rewritten
bullet point as plain text - no quotes, no explanation, no bullet marker.

ORIGINAL: {bullet}
"""
    return _generate_text(prompt, temperature=0.5)


# --------------------------------------------------------------------------- #
# 9. AI Cover Letter Generator
# --------------------------------------------------------------------------- #
def generate_cover_letter(resume_text: str, role: str, job_description: str = "", company_name: str = "") -> str:
    company_line = f"The target company is {company_name}." if company_name else ""
    jd_block = f"\nJOB DESCRIPTION:\n{truncate(job_description, 3000)}\n" if job_description else ""
    prompt = f"""
Write a professional, concise cover letter (under 350 words) for this candidate
applying to a {role} position. {company_line}
Use the resume content for specifics, sound genuine and not generic, and avoid
cliches like "I am writing to express my interest". Output plain text only,
formatted as a ready-to-send letter (no markdown).

RESUME:
{truncate(resume_text)}
{jd_block}
"""
    return _generate_text(prompt, temperature=0.65)


# --------------------------------------------------------------------------- #
# 10. Interview Question Generator
# --------------------------------------------------------------------------- #
import random

def generate_interview_questions(resume_text: str, skills: list[str], role: str) -> dict:
    skills_line = ", ".join(skills[:20]) if skills else "general skills found in the resume"

    seed = random.randint(1000, 999999)

    prompt = f"""
Random Seed: {seed}

Role: {role}

Detected Skills:
{skills_line}

Resume:
{truncate(resume_text)}

Generate a completely NEW set of interview questions every time.

Requirements:
- Do NOT repeat common questions.
- Questions must be tailored to the role and skills.
- Include real-world and scenario-based questions.
- Mix Easy, Medium, and Hard difficulty levels.
- Focus on technologies found in the resume.
- Generate fresh questions on every request.

Return ONLY valid JSON with exactly these keys:

{{
    "technical": [
        "question1",
        "question2",
        "question3",
        "question4",
        "question5"
    ],
    "behavioral": [
        "question1",
        "question2",
        "question3",
        "question4",
        "question5"
    ],
    "project_based": [
        "question1",
        "question2",
        "question3",
        "question4",
        "question5"
    ]
}}
"""
    return _generate_json(prompt)


# --------------------------------------------------------------------------- #
# 11. AI Career Roadmap
# --------------------------------------------------------------------------- #
def generate_career_roadmap(current_skills: list[str], target_role: str) -> dict:
    skills_line = ", ".join(current_skills[:25]) if current_skills else "no detected skills"
    prompt = f"""
Create a learning roadmap for someone with these current skills: {skills_line},
who wants to become a {target_role}.

Return a JSON object with exactly these keys: "beginner", "intermediate", "advanced".
Each maps to an object with exactly these keys:
- "skills_to_learn": array of 3-5 strings
- "certifications": array of 2-3 strings (real, well-known certifications)
- "project_ideas": array of 2-3 strings (concrete project ideas, one sentence each)
"""
    return _generate_json(prompt)


# --------------------------------------------------------------------------- #
# 12. Resume Chatbot
# --------------------------------------------------------------------------- #
def chatbot_response(message: str, resume_context: dict, chat_history: list[dict]) -> str:
    history_lines = "\n".join(
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['message']}" for m in chat_history[-6:]
    )
    context_summary = json.dumps(
        {
            "ats_score": resume_context.get("ats_score"),
            "role": resume_context.get("role"),
            "skills": resume_context.get("parsed_data", {}).get("skills", []),
            "missing_skills": resume_context.get("missing_skills", []),
        }
    )
    prompt = f"""
You are a friendly, knowledgeable resume coach chatbot embedded in an AI
Resume Analyzer app. Answer the user's question using the resume context
below. Be specific and concrete, not generic. Keep responses under 150 words
unless the user asks for detail. Plain text only, no markdown headers.

RESUME CONTEXT (JSON): {context_summary}

CONVERSATION SO FAR:
{history_lines}

User: {message}
"""
    return _generate_text(prompt, temperature=0.6)
