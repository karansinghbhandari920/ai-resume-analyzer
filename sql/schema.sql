-- =====================================================================
-- AI Resume Analyzer - Supabase schema
-- Run this in the Supabase SQL editor (Project -> SQL Editor -> New query)
-- =====================================================================

create extension if not exists "uuid-ossp";

-- ---------------------------------------------------------------------
-- profiles: one row per auth.users row (Supabase Auth owns the actual
-- credentials; this table just mirrors the public-facing bits + lets us
-- join against it from the rest of the schema).
-- ---------------------------------------------------------------------
create table if not exists public.profiles (
    id          uuid references auth.users(id) on delete cascade primary key,
    email       text unique not null,
    full_name   text,
    is_admin    boolean default false,
    created_at  timestamptz default now()
);

-- ---------------------------------------------------------------------
-- resume_analysis: one row per resume a user has analyzed
-- ---------------------------------------------------------------------
create table if not exists public.resume_analysis (
    id              uuid primary key default uuid_generate_v4(),
    user_id         uuid references auth.users(id) on delete cascade not null,
    resume_name     text not null,
    role            text,
    raw_text        text,
    parsed_data     jsonb,          -- name/email/phone/skills/education/...
    ats_score       numeric(5,2),
    score_breakdown jsonb,          -- {skills: 90, sections: 75, ...}
    ai_review       jsonb,          -- {summary, strengths, weaknesses, ...}
    created_at      timestamptz default now()
);

create index if not exists idx_resume_analysis_user_id on public.resume_analysis(user_id);
create index if not exists idx_resume_analysis_created_at on public.resume_analysis(created_at desc);

-- ---------------------------------------------------------------------
-- job_matches: job-description match runs, optionally tied to an analysis
-- ---------------------------------------------------------------------
create table if not exists public.job_matches (
    id                  uuid primary key default uuid_generate_v4(),
    user_id             uuid references auth.users(id) on delete cascade not null,
    analysis_id         uuid references public.resume_analysis(id) on delete cascade,
    job_title           text,
    job_description     text,
    match_score         numeric(5,2),
    matching_skills     jsonb,
    missing_keywords    jsonb,
    created_at          timestamptz default now()
);

create index if not exists idx_job_matches_user_id on public.job_matches(user_id);

-- ---------------------------------------------------------------------
-- chat_history: resume chatbot conversation log (gives the chatbot memory
-- within a session and lets users revisit past answers)
-- ---------------------------------------------------------------------
create table if not exists public.chat_history (
    id          uuid primary key default uuid_generate_v4(),
    user_id     uuid references auth.users(id) on delete cascade not null,
    analysis_id uuid references public.resume_analysis(id) on delete cascade,
    role        text check (role in ('user', 'assistant')) not null,
    message     text not null,
    created_at  timestamptz default now()
);

create index if not exists idx_chat_history_user_id on public.chat_history(user_id);

-- =====================================================================
-- Row Level Security: every user can only ever see / write their own rows
-- =====================================================================
alter table public.profiles        enable row level security;
alter table public.resume_analysis enable row level security;
alter table public.job_matches     enable row level security;
alter table public.chat_history    enable row level security;

create policy "Users select own profile"   on public.profiles        for select using (auth.uid() = id);
create policy "Users update own profile"   on public.profiles        for update using (auth.uid() = id);

create policy "Users manage own analyses"  on public.resume_analysis for all
    using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "Users manage own matches"   on public.job_matches     for all
    using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "Users manage own chat"      on public.chat_history    for all
    using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- =====================================================================
-- Auto-create a profile row whenever someone signs up via Supabase Auth
-- =====================================================================
create or replace function public.handle_new_user()
returns trigger as $$
begin
    insert into public.profiles (id, email, full_name)
    values (new.id, new.email, coalesce(new.raw_user_meta_data->>'full_name', ''));
    return new;
end;
$$ language plpgsql security definer;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute procedure public.handle_new_user();

-- =====================================================================
-- Admin dashboard stats view.
-- NOTE: this view aggregates across ALL users, so it must only ever be
-- queried with the SUPABASE_SERVICE_ROLE_KEY (server-side, never shipped
-- to the browser) - see database.py:get_admin_stats(). It deliberately
-- has no RLS-friendly policy of its own.
-- =====================================================================
create or replace view public.admin_stats as
select
    (select count(*) from public.profiles)                                as total_users,
    (select count(*) from public.resume_analysis)                         as total_analyses,
    (select round(avg(ats_score), 2) from public.resume_analysis)         as avg_score,
    (select round(max(ats_score), 2) from public.resume_analysis)         as best_score,
    (select count(*) from public.resume_analysis
        where created_at >= now() - interval '1 day')                    as analyses_today;

create or replace view public.admin_role_popularity as
select role, count(*) as analysis_count
from public.resume_analysis
where role is not null
group by role
order by analysis_count desc;

create or replace view public.admin_daily_activity as
select date_trunc('day', created_at)::date as day, count(*) as analyses
from public.resume_analysis
group by 1
order by 1 desc
limit 30;
