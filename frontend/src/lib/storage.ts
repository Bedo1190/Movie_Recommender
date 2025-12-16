const LIKED_KEY = 'mr_liked_movie_ids_v1'
const RECS_KEY = 'mr_last_recs_v1'

export function loadLiked(): number[] {
  try {
    const raw = sessionStorage.getItem(LIKED_KEY)
    if (!raw) return []
    const ids = JSON.parse(raw) as unknown
    if (!Array.isArray(ids)) return []
    return ids.map((n) => Number(n)).filter((n) => Number.isFinite(n))
  } catch {
    return []
  }
}

export function saveLiked(ids: number[]): void {
  sessionStorage.setItem(LIKED_KEY, JSON.stringify(Array.from(new Set(ids))))
}

export function loadLastRecs(): unknown {
  try {
    const raw = sessionStorage.getItem(RECS_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function saveLastRecs(recs: unknown): void {
  sessionStorage.setItem(RECS_KEY, JSON.stringify(recs))
}

export function clearSession(): void {
  sessionStorage.removeItem(LIKED_KEY)
  sessionStorage.removeItem(RECS_KEY)
}
