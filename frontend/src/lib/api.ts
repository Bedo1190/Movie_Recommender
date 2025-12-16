export type Movie = {
  movieId: number
  title: string
  poster_url?: string
  year?: number | null
  genres?: string
  rating_mean?: number
  overview?: string
}

export type GenreItem = {
  id?: number
  name?: string
  // backend's genres.json might be list of strings or objects; we accept both.
  [k: string]: unknown
}

const DEFAULT_BASE = 'http://localhost:8000'

export const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || DEFAULT_BASE

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {})
    },
    ...init
  })

  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`
    try {
      const body = await res.json()
      detail = (body?.detail || body?.message || detail) as string
    } catch {
      // ignore
    }
    throw new Error(detail)
  }

  return (await res.json()) as T
}

export async function getPopular(): Promise<Movie[]> {
  return http<Movie[]>('/movies/popular')
}

export async function getGenres(): Promise<GenreItem[]> {
  return http<GenreItem[]>('/movies/genres')
}

export async function searchMovies(q: string): Promise<Movie[]> {
  const qs = new URLSearchParams({ q }).toString()
  return http<Movie[]>(`/search?${qs}`)
}

export async function getMovie(movieId: number): Promise<Movie> {
  return http<Movie>(`/movies/${movieId}`)
}

export async function recommend(liked_movie_ids: number[], top_k = 10): Promise<Movie[]> {
  return http<Movie[]>('/recommend', {
    method: 'POST',
    body: JSON.stringify({ liked_movie_ids, top_k })
  })
}
