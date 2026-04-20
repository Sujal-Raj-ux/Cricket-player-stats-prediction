-- IPL season labels in CSV are strings (e.g. 2009/10), not floats.
-- Run in Supabase SQL Editor if you already applied 001 with season double precision.

alter table public.ipl_ml_features
  alter column season type text using (
    case
      when season is null then null
      else trim(season::text)
    end
  );
