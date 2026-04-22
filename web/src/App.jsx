import { PlayerDashboard } from "@/components/dashboard/player-dashboard";

export default function App() {
  return (
    <div className="flex min-h-full flex-col bg-[var(--background)] font-sans text-[var(--foreground)]">
      <header className="relative border-b border-[var(--border)] bg-[var(--surface)]/75 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div className="min-w-0">
            <p className="font-[family-name:var(--font-display)] text-lg font-semibold tracking-tight text-[var(--foreground)]">
              IPL outlook lab
            </p>
            <p className="truncate text-xs text-[var(--muted)]">Batting form · history · model outlook</p>
          </div>
        </div>
      </header>

      <div className="relative flex-1">
        <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(ellipse_90%_55%_at_50%_-25%,var(--glow-hero),transparent)]" />
        <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(ellipse_70%_40%_at_100%_0%,var(--glow-blue),transparent)] opacity-90" />
        <main className="relative mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8 lg:py-14">
          <PlayerDashboard />
        </main>
      </div>

      <footer className="relative mt-auto border-t border-[var(--border)] bg-[var(--surface-deep)] px-4 py-8 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-6xl text-sm text-[var(--muted)]">
          <p>Fan-built demo — not affiliated with the IPL or its franchises.</p>
        </div>
      </footer>
    </div>
  );
}
