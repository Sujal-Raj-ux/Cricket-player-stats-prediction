export function meanRuns(innings) {
  if (innings.length === 0) return 0;
  return innings.reduce((s, i) => s + i.runs, 0) / innings.length;
}

/** @param {number} window - e.g. 5 or 10 */
export function rollingAverageRuns(innings, window) {
  return innings.map((_, idx) => {
    const start = Math.max(0, idx - window + 1);
    const slice = innings.slice(start, idx + 1);
    return meanRuns(slice);
  });
}

export function dismissalRate(innings) {
  if (innings.length === 0) return 0;
  const outs = innings.filter((i) => i.out).length;
  return outs / innings.length;
}

export function strikeRate100(innings) {
  if (innings.length === 0) return 0;
  const totalRuns = innings.reduce((s, i) => s + i.runs, 0);
  const totalBalls = innings.reduce((s, i) => s + i.ballsFaced, 0);
  if (totalBalls === 0) return 0;
  return (totalRuns / totalBalls) * 100;
}

export function lastNInningsSummary(player, n) {
  const slice = player.innings.slice(-n);
  return {
    avgRuns: meanRuns(slice),
    outs: slice.filter((i) => i.out).length,
    notOuts: slice.filter((i) => !i.out).length,
    strikeRate: strikeRate100(slice),
  };
}
