import { lazy, Suspense, useEffect, useMemo, useRef, useState } from "react";
import { fetchPlayerDashboard, fetchPlayerList, getApiBase, isLocalhostApiUrl } from "@/lib/api";
import { PLAYERS } from "@/lib/mock-data";
import { OutlookPanel } from "./outlook-panel";
import { OutcomesStrip } from "./outcomes-strip";
import { StatCards } from "./stat-cards";

const RunsTrendChart = lazy(() =>
  import("./runs-trend-chart").then((m) => ({ default: m.RunsTrendChart })),
);

const chartFallback = (
  <div className="flex h-[320px] items-center justify-center rounded-xl border border-dashed border-[var(--border)] bg-[var(--surface-elevated)] text-sm text-[var(--muted)]">
    Loading chart…
  </div>
);

export function PlayerDashboard() {
  const [mode, setMode] = useState("loading");
  const [players, setPlayers] = useState([]);
  const [playerId, setPlayerId] = useState("");
  const [dashboard, setDashboard] = useState(null);
  const [dashLoading, setDashLoading] = useState(false);
  const [dashError, setDashError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);
  const searchWrapRef = useRef(null);
  const [listNotice, setListNotice] = useState(/** @type {{ type: "fallback"; message: string } | null} */ (null));

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const list = await fetchPlayerList();
        if (cancelled) return;
        if (list.length === 0) {
          setPlayers([]);
          setPlayerId("");
          setListNotice(null);
          setMode("empty");
          return;
        }
        setListNotice(null);
        setPlayers(list);
        setPlayerId(list[0].id);
        setMode("api");
      } catch (e) {
        if (cancelled) return;
        const msg = e instanceof Error ? e.message : "Could not load players";
        setListNotice({ type: "fallback", message: msg });
        setPlayers(PLAYERS);
        setPlayerId(PLAYERS[0]?.id ?? "");
        setMode("mock");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (mode !== "api" || !playerId) return;
    let cancelled = false;
    setDashLoading(true);
    setDashError(null);
    (async () => {
      try {
        const d = await fetchPlayerDashboard(playerId);
        if (!cancelled) {
          setDashboard(d);
          setDashLoading(false);
        }
      } catch (e) {
        if (!cancelled) {
          setDashboard(null);
          setDashError(e instanceof Error ? e.message : "Dashboard failed");
          setDashLoading(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [mode, playerId]);

  useEffect(() => {
    const p = players.find((x) => x.id === playerId);
    if (p?.name) setSearchQuery(p.name);
  }, [playerId, players]);

  useEffect(() => {
    function onDocDown(e) {
      if (searchWrapRef.current && !searchWrapRef.current.contains(e.target)) {
        setSearchOpen(false);
      }
    }
    document.addEventListener("mousedown", onDocDown);
    return () => document.removeEventListener("mousedown", onDocDown);
  }, []);

  const filteredPlayers = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return players.slice(0, 40);
    return players
      .filter((p) => {
        const hay = `${p.name} ${p.team ?? ""}`.toLowerCase();
        return hay.includes(q);
      })
      .slice(0, 40);
  }, [players, searchQuery]);

  const player = useMemo(() => {
    if (mode === "api" && dashboard?.player && dashboard.innings) {
      return {
        id: dashboard.player.id,
        name: dashboard.player.name,
        team: dashboard.player.team ?? "IPL dataset",
        format: "IPL",
        innings: dashboard.innings,
      };
    }
    if (mode === "mock") {
      return players.find((p) => p.id === playerId) ?? players[0];
    }
    const stub = players.find((p) => p.id === playerId) ?? players[0];
    if (!stub) return null;
    return { ...stub, format: "IPL", innings: stub.innings ?? [] };
  }, [mode, dashboard, players, playerId]);

  if (mode === "loading") {
    return (
      <p className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 text-[var(--muted)]">
        Loading players…
      </p>
    );
  }

  if (mode === "empty") {
    return (
      <div className="elevated-panel space-y-4 rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-8 md:p-10">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--accent)]">No data</p>
        <h2 className="font-[family-name:var(--font-display)] text-2xl font-semibold text-[var(--foreground)] md:text-3xl">
          No players returned from the API
        </h2>
        <p className="max-w-xl text-[var(--muted)]">
          The backend is up but the player list is empty. Load rows into{" "}
          <code className="rounded bg-[var(--surface-elevated)] px-1.5 py-0.5 text-sm text-[var(--foreground)]">
            ipl_ml_features
          </code>{" "}
          (for example{" "}
          <code className="text-sm">python scripts/import_csv_to_supabase.py</code>) or ensure{" "}
          <code className="text-sm">data/ipl_ml_features.csv</code> exists if you use CSV mode.
        </p>
        <p className="text-sm text-[var(--muted)]">
          API base:{" "}
          <code className="rounded bg-[var(--surface-elevated)] px-1.5 py-0.5 text-[var(--foreground)]">
            {getApiBase()}
          </code>
        </p>
      </div>
    );
  }

  if (!player) {
    return (
      <p className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 text-[var(--muted)]">
        Loading players…
      </p>
    );
  }

  const prediction = dashboard?.prediction ?? null;
  const predictionErr = dashboard?.prediction_error ?? dashError;
  const latestActual =
    dashboard?.latest_context?.actual_runs != null ? Number(dashboard.latest_context.actual_runs) : null;

  return (
    <div className="space-y-10">
      {listNotice?.type === "fallback" ? (
        <div
          className="rounded-2xl border border-[var(--border-strong)] bg-[var(--surface-elevated)] px-4 py-3 text-sm text-[var(--foreground)] shadow-[var(--elev-shadow)]"
          role="status"
        >
          <p className="font-medium text-[var(--accent-dim)]">Using demo data</p>
          <p className="mt-1 text-[var(--muted)]">
            Could not load <code className="text-xs text-[var(--foreground)]">{getApiBase()}/api/players</code>
            — {listNotice.message}.{" "}
            {typeof window !== "undefined" &&
            isLocalhostApiUrl() &&
            !/^(localhost|127\.0\.0\.1)$/i.test(window.location.hostname) ? (
              <span className="block font-medium text-[var(--foreground)]">
                This site is not on localhost, but the UI was built to call 127.0.0.1. In Render (or your host) set
                environment variable <code className="text-xs">VITE_API_URL</code> to your public API (https://…onrender.com)
                and <strong>redeploy</strong> the static site. Then set <code className="text-xs">CORS_ORIGINS</code> on the API
                to this page&apos;s origin.
              </span>
            ) : (
              <>
                Check that the API is running, <code className="text-xs">CORS_ORIGINS</code> includes this site, and{" "}
                <code className="text-xs">VITE_API_URL</code> is correct for the build that was deployed.
              </>
            )}
          </p>
        </div>
      ) : null}

      <header className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--accent)]">
            IPL · T20 form
            {mode === "api" ? " · live API" : " · offline mock"}
          </p>
          <h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold tracking-tight text-[var(--foreground)] sm:text-4xl md:text-5xl">
            Player insights
          </h1>
          {mode !== "api" ? (
            <p className="max-w-2xl text-base text-[var(--muted)]">
              Start your backend and set VITE_API_URL so this app can load real players — sample batters shown for now.
            </p>
          ) : null}
        </div>
        <div ref={searchWrapRef} className="relative flex w-full max-w-md flex-col gap-2 sm:flex-row sm:items-start">
          <label className="text-sm text-[var(--muted)] sm:pt-3" htmlFor="player-search">
            Batter
          </label>
          <div className="relative min-w-0 flex-1">
            <input
              id="player-search"
              type="search"
              autoComplete="off"
              placeholder="Search player name…"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setSearchOpen(true);
              }}
              onFocus={() => setSearchOpen(true)}
              onKeyDown={(e) => {
                if (e.key === "Escape") setSearchOpen(false);
              }}
              className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-elevated)] px-4 py-3 text-sm font-medium text-[var(--foreground)] outline-none ring-[var(--accent)] placeholder:text-[var(--muted)] focus:ring-2"
            />
            {searchOpen && (
              <ul
                className="elevated-panel absolute z-50 mt-1 max-h-72 w-full overflow-auto rounded-xl border border-[var(--border)] bg-[var(--surface)] py-1 text-sm shadow-lg"
                role="listbox"
              >
                {filteredPlayers.length === 0 ? (
                  <li className="px-4 py-3 text-[var(--muted)]">No players match.</li>
                ) : (
                  filteredPlayers.map((p) => (
                    <li key={p.id} role="option" aria-selected={p.id === playerId}>
                      <button
                        type="button"
                        className="flex w-full flex-col items-start gap-0.5 px-4 py-2.5 text-left hover:bg-[var(--surface-elevated)]"
                        onMouseDown={(e) => e.preventDefault()}
                        onClick={() => {
                          setPlayerId(p.id);
                          setSearchQuery(p.name);
                          setSearchOpen(false);
                        }}
                      >
                        <span className="font-medium text-[var(--foreground)]">{p.name}</span>
                        {p.team ? <span className="text-xs text-[var(--muted)]">{p.team}</span> : null}
                      </button>
                    </li>
                  ))
                )}
              </ul>
            )}
          </div>
        </div>
      </header>

      <OutlookPanel
        playerName={player.name}
        prediction={prediction}
        predictionLoading={mode === "api" && dashLoading}
        predictionError={mode === "api" ? predictionErr : "Connect your backend to enable run outlooks."}
        latestActual={latestActual}
      />

      <StatCards player={player} />

      <section className="grid gap-6 lg:grid-cols-3">
        <div className="elevated-panel rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-6 lg:col-span-2">
          <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
            <div>
              <h3 className="font-[family-name:var(--font-display)] text-xl font-semibold text-[var(--foreground)]">
                Runs by innings
              </h3>
              <p className="text-sm text-[var(--muted)]">
                Gold line = runs per innings; blue = 10-innings rolling average; dashed gold = sample average in
                this slice.
              </p>
            </div>
            <span className="rounded-full bg-[var(--chip)] px-3 py-1 text-xs font-medium text-[var(--chip-fg)]">
              {player.team}
            </span>
          </div>
          {mode === "api" && dashLoading ? (
            chartFallback
          ) : (
            <Suspense fallback={chartFallback}>
              <RunsTrendChart innings={player.innings} />
            </Suspense>
          )}
        </div>
        <div className="elevated-panel rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-6">
          <h3 className="font-[family-name:var(--font-display)] text-xl font-semibold text-[var(--foreground)]">
            Outcomes
          </h3>
          <p className="mt-1 text-sm text-[var(--muted)]">Recent IPL innings (synthetic out / not out for chart tint).</p>
          <div className="mt-6">
            <OutcomesStrip innings={player.innings} />
          </div>
        </div>
      </section>
    </div>
  );
}
