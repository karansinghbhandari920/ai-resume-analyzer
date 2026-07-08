# ai-resume-analyzer# 🧠 AI Resume Analyzer

A production-ready, full-stack AI resume intelligence platform built with Python, Streamlit, Supabase, and Google Gemini.

---

## Features

| Feature | Description |
|---|---|
| **ATS Scoring** | 7-component weighted score (skills, sections, contact info, action verbs, quantified achievements, readability, word count) |
| **Resume Parser** | Extracts name, email, phone, LinkedIn, GitHub, skills, education, experience, projects, certifications using spaCy + regex |
| **Role Matching** | Compares detected skills against 5 role profiles: Data Analyst, Data Scientist, Software Engineer, ML Engineer, Business Analyst |
| **JD Matcher** | Semantic similarity (sentence-transformers) + keyword overlap against a pasted job description |
| **AI Review** | Gemini-generated recruiter-style feedback: summary, strengths, weaknesses, missing skills, improvement suggestions, verdict |
| **Bullet Rewriter** | AI rewrites weak resume bullets into impact statements with action verbs and quantified outcomes |
| **Cover Letter Generator** | Custom cover letter generated from resume + role + optional JD |
| **Interview Prep** | Technical, behavioral, and project-based questions generated from the resume |
| **Career Roadmap** | Beginner → Intermediate → Advanced learning path with skills, certifications, and project ideas |
| **Resume Chatbot** | Context-aware chatbot that answers questions about the loaded resume |
| **Analytics Dashboard** | Score history, role popularity charts (line, bar, pie) using Plotly |
| **PDF Report** | Downloadable PDF with ATS score, skill analysis, AI review, job match, suggestions |
| **Admin Dashboard** | Platform-wide stats (service-role only, never exposed to users) |
| **Auth** | Supabase Auth (signup, login, logout) with Row Level Security — every user sees only their own data |

---

## Tech Stack

```
Frontend:      Streamlit
Backend:       Python 3.10+
Database:      Supabase PostgreSQL
Auth:          Supabase Auth
AI:            Google Gemini (gemini-2.0-flash)
NLP:           spaCy (en_core_web_sm), pdfplumber, python-docx
Semantic ML:   sentence-transformers (all-MiniLM-L6-v2), scikit-learn
Charts:        Plotly
PDF:           ReportLab
```

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/yourname/ai-resume-analyzer.git
cd ai-resume-analyzer

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

# Download the spaCy model (one-time)
python -m spacy download en_core_web_sm
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-public-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key   # Admin Dashboard only
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash
```

Get your keys:
- **Supabase**: [supabase.com](https://supabase.com) → Project Settings → API
- **Gemini**: [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### 3. Initialize the database

In Supabase → **SQL Editor → New query**, paste and run the entire contents of `sql/schema.sql`. This creates all tables, RLS policies, the auto-profile trigger, and the admin views.

### 4. Run locally

```bash
# Load .env vars (or use a tool like python-dotenv-cli)
export $(cat .env | xargs)
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

---

## Project Structure

```
ai-resume-analyzer/
├── app.py                  # Entry point + auth-gated navigation (st.navigation/st.Page)
├── auth.py                 # Supabase Auth wrapper (sign_up, sign_in, sign_out)
├── database.py             # All Supabase CRUD (user-scoped + admin-scoped clients)
├── parser.py               # Text extraction (PDF/DOCX/TXT) + NLP entity parsing
├── scorer.py               # ATS Score Engine (7-component weighted algorithm)
├── skills.py               # Skill taxonomy + per-role requirement profiles
├── semantic_matcher.py     # JD matcher (sentence-transformers + TF-IDF fallback)
├── ai_engine.py            # Gemini API calls: review, rewrite, cover letter, interview Qs, roadmap, chatbot
├── resume_rewriter.py      # Bullet-rewrite orchestration layer
├── analytics.py            # Builds DataFrames for Plotly from raw Supabase rows
├── pdf_report.py           # ReportLab PDF generator
├── utils.py                # CSS loading, session-state bootstrap, UI component builders
├── requirements.txt
├── .env.example
├── .streamlit/
│   └── config.toml         # Dark theme ("scan readout" design system)
├── assets/
│   └── style.css           # Custom CSS: palette, typography, gauge, chips, cards
├── sql/
│   └── schema.sql          # Complete Postgres schema + RLS + admin views
└── views/                  # One file per page (loaded via st.Page)
    ├── dashboard.py
    ├── upload_resume.py
    ├── ats_analysis.py
    ├── job_match.py
    ├── ai_suggestions.py
    ├── ai_review.py
    ├── cover_letter.py
    ├── interview_questions.py
    ├── chatbot.py
    ├── roadmap.py
    ├── analytics_page.py
    ├── profile.py
    ├── settings_page.py
    └── admin.py
```

---

## Deployment

### Streamlit Cloud (simplest)

1. Push to GitHub (make sure `.env` is in `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → select your repo.
3. Set **Secrets** in the Streamlit Cloud UI (Settings → Secrets):

```toml
SUPABASE_URL = "https://..."
SUPABASE_ANON_KEY = "..."
SUPABASE_SERVICE_ROLE_KEY = "..."
GEMINI_API_KEY = "..."
GEMINI_MODEL = "gemini-2.0-flash"
```

4. Add a `packages.txt` (for system deps if spaCy needs them):

```
# packages.txt — leave empty if no extra system packages needed
```

5. Add a `setup.sh` or post-install hook to download the spaCy model. The easiest approach: add this to `requirements.txt`:

```
https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

### Render / Railway

Set the same env vars as **Secrets** above in your service's environment settings. Start command:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

---

## Making a User an Admin

Run this in the Supabase SQL Editor, replacing the email:

```sql
UPDATE public.profiles
SET is_admin = true
WHERE email = 'admin@yourcompany.com';
```

The Admin Dashboard link will appear in that user's sidebar on next sign-in.

---

## Architecture Notes

### Authentication & RLS
Supabase Auth owns credentials. Every other table references `auth.users(id)`. Row Level Security policies enforce that users can only ever read or write their own rows — even if someone got hold of the anon key. The service-role key (used only by `database.py:_admin_client()`) bypasses RLS and should **never** reach the browser.

### AI Fallback
Every function in `ai_engine.py` raises `AIEngineError` (not a raw exception) when Gemini isn't configured or the API call fails. Every page catches this and shows a user-friendly inline error, so the rest of the app (ATS scoring, parsing, job matching) works without any API keys configured.

### Semantic Matcher Fallback
`semantic_matcher.py` tries `sentence-transformers` first; if the model isn't downloaded or available, it silently falls back to TF-IDF cosine similarity via scikit-learn. Both paths produce a 0–100 match score — the UI is identical.

### Session State Design
Streamlit re-runs the entire script on every interaction. Session state holds:
- `auth_user` — access/refresh tokens + user metadata
- `current_analysis` — the most recently uploaded/selected resume (dict mirroring the DB row)
- `chat_messages` — chatbot transcript for the current session

No page should import another page module directly. Data flows through `st.session_state` and `st.switch_page()`.

---

## License

MIT
