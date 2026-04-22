/** @param {{ innings: object[], maxDots?: number }} props */
export function OutcomesStrip({ innings, maxDots = 24 }) {
  const slice = innings.slice(-maxDots);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap gap-1.5">
        {slice.map((row) => (
          <span
            key={row.id}
            title={`${row.matchLabel}: ${row.runs} runs${row.out ? ` — ${row.dismissal ?? "out"}` : " — not out"}`}
            className={[
              "inline-flex h-8 min-w-[2rem] items-center justify-center rounded-md px-2 text-xs font-medium tabular-nums",
              row.out
                ? "bg-[var(--out-bg)] text-[var(--out-fg)] ring-1 ring-[var(--out-ring)]"
                : "bg-[var(--notout-bg)] text-[var(--notout-fg)] ring-1 ring-[var(--notout-ring)]",
            ].join(" ")}
          >
            {row.runs}
          </span>
        ))}
      </div>
      <p className="text-xs text-[var(--muted)]">
        Recent IPL innings (left → right): tint shows <span className="text-[var(--out-fg)]">out</span> vs{" "}
        <span className="text-[var(--notout-fg)]">not out</span>. Hover a cell for match detail.
      </p>
    </div>
  );
}
