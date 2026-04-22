import { dismissalRate, lastNInningsSummary, meanRuns, strikeRate100 } from "@/lib/stats";

function Card({ label, value, hint }) {
  return (
    <div className="elevated-panel group relative overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5">
      <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-[var(--glow)] opacity-40 blur-2xl transition-opacity group-hover:opacity-70" />
      <p className="text-xs font-medium uppercase tracking-wider text-[var(--muted)]">{label}</p>
      <p className="mt-2 font-[family-name:var(--font-display)] text-3xl font-semibold tracking-tight text-[var(--foreground)]">
        {value}
      </p>
      <p className="mt-2 text-sm text-[var(--muted)]">{hint}</p>
    </div>
  );
}

/** @param {{ player: { innings: object[] } }} props */
export function StatCards({ player }) {
  const all = player.innings;
  const last10 = lastNInningsSummary(player, 10);

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <Card
        label="IPL sample avg"
        value={meanRuns(all).toFixed(1)}
        hint={`Across ${all.length} IPL innings in this demo set.`}
      />
      <Card
        label="Last 10 innings"
        value={last10.avgRuns.toFixed(1)}
        hint={`${last10.outs} dismissals · ${last10.notOuts} not outs`}
      />
      <Card
        label="Strike rate (sample)"
        value={`${strikeRate100(all).toFixed(0)} SR`}
        hint="Runs per 100 balls in this IPL demo."
      />
      <Card
        label="Out rate"
        value={`${(dismissalRate(all) * 100).toFixed(0)}%`}
        hint="Share of innings ending in dismissal."
      />
    </div>
  );
}
