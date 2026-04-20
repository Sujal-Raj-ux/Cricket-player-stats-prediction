-- Run this in Supabase: SQL Editor → New query → Paste → Run
-- Or use: supabase db push (if using Supabase CLI linked project)

create table if not exists public.ipl_ml_features (
  id bigserial primary key,
  rolling_avg_5 double precision,
  rolling_avg_10 double precision,
  rolling_sr_5 double precision,
  rolling_sr_10 double precision,
  innings_count double precision,
  career_avg double precision,
  consistency double precision,
  bat_pos double precision,
  innings double precision,
  is_playoff double precision,
  toss_bat_first double precision,
  venue_avg double precision,
  vs_team_avg double precision,
  venue_overall_avg double precision,
  is_home double precision,
  opp_bowling_econ double precision,
  opp_bowling_sr double precision,
  runs double precision not null,
  batter text not null,
  match_id text not null,
  date date not null,
  season text
);

create index if not exists idx_ipl_ml_features_batter_date
  on public.ipl_ml_features (batter, date);

-- Optional: enable RLS + policies in Supabase if you expose PostgREST to the browser.
