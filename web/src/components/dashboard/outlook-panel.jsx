/** @param {{ playerName: string, prediction: object | null, predictionLoading: boolean, predictionError: string | null, latestActual: number | null }} props */
export function OutlookPanel({
  playerName,
  prediction,
  predictionLoading,
  predictionError,
  latestActual,
}) {
  const predicted = prediction?.predicted_runs;
  const hasForecast = predicted != null && Number.isFinite(predicted);

  const errorText =
    predictionError == null || predictionError === ""
      ? null
      : typeof predictionError === "string"
        ? predictionError
        : JSON.stringify(predictionError);

  let headline = "Run outlook";
  let sub =
    "Your latest IPL row in the dataset is used to estimate likely runs in a similar situation.";

  if (predictionLoading) {
    headline = "Generating outlook…";
    sub = "Loading match history and requesting a forecast.";
  } else if (errorText) {
    headline = "Outlook unavailable";
    sub = errorText;
  } else if (hasForecast) {
    const rounded = Math.round(predicted * 10) / 10;
    headline = `Projected next outing: ~${rounded} runs`;
    sub = `Based on rolling form and match context for ${playerName}.`;
    if (latestActual != null) {
      sub += ` Last row in data (actual): ${latestActual} runs.`;
    }
    sub += " Treat as a guide.";
  }

  return (
    <section className="elevated-panel relative overflow-hidden rounded-3xl border border-[var(--border)] bg-gradient-to-br from-[var(--surface)] via-[var(--surface-elevated)] to-[var(--surface-deep)] p-8 md:p-10">
      <div className="pointer-events-none absolute -left-20 top-0 h-72 w-72 rounded-full bg-[var(--glow-strong)] opacity-30 blur-3xl" />
      <div className="pointer-events-none absolute -right-10 bottom-0 h-56 w-56 rounded-full bg-[var(--glow-hero)] opacity-35 blur-3xl" />
      <div className="relative flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
        <div className="max-w-xl space-y-3">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--accent)]">
            Next IPL outlook
          </p>
          <h2 className="font-[family-name:var(--font-display)] text-3xl font-semibold leading-tight text-[var(--foreground)] md:text-4xl">
            {headline}
          </h2>
          <p className="text-base leading-relaxed text-[var(--muted)]">{sub}</p>
        </div>
        <div className="flex shrink-0 flex-col items-start gap-3 md:items-end">
          <div className="rounded-2xl border border-dashed border-[var(--border-strong)] bg-[var(--surface-elevated)] px-5 py-4 text-left md:text-right">
            <p className="text-xs uppercase tracking-wider text-[var(--muted)]">Model signal</p>
            <p className="mt-1 font-[family-name:var(--font-display)] text-2xl font-medium text-[var(--foreground)] tabular-nums">
              {predictionLoading ? "…" : hasForecast ? Math.round(predicted * 10) / 10 : "—"}
            </p>
            <p className="mt-1 max-w-[min(100%,18rem)] break-words text-sm text-[var(--muted)]">
              {predictionLoading
                ? "Inferring…"
                : errorText
                  ? errorText.length > 120
                    ? `${errorText.slice(0, 117)}…`
                    : errorText
                  : hasForecast
                    ? "Estimated runs"
                    : "No forecast yet — check that your backend is running."}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
