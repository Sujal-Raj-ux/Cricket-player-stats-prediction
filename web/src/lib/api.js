const raw = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

/** @type {string} */
export const API_BASE = typeof raw === "string" ? raw.trim().replace(/\/$/, "") : String(raw);

export function getApiBase() {
  return API_BASE;
}

/** True if the build still points at localhost (common if VITE_API_URL was not set on the host that ran `npm run build`). */
export function isLocalhostApiUrl() {
  return /127\.0\.0\.1|localhost/i.test(API_BASE);
}

/** @param {Response} res */
async function errorDetail(res) {
  try {
    const j = await res.json();
    const d = j?.detail;
    if (typeof d === "string") return d;
    if (d != null) return JSON.stringify(d);
  } catch {
    /* ignore */
  }
  return "";
}

/** @returns {Promise<object[]>} */
export async function fetchPlayerList() {
  const res = await fetch(`${API_BASE}/api/players`);
  if (!res.ok) {
    const extra = await errorDetail(res);
    throw new Error(extra || `Players request failed (${res.status})`);
  }
  const data = await res.json();
  return data.players ?? [];
}

/** @returns {Promise<object>} */
export async function fetchPlayerDashboard(playerId) {
  const res = await fetch(`${API_BASE}/api/players/${encodeURIComponent(playerId)}/dashboard`);
  if (!res.ok) {
    const extra = await errorDetail(res);
    throw new Error(extra || `Dashboard request failed (${res.status})`);
  }
  return res.json();
}
