import { useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'
import type { Movie } from '../lib/types'
import MovieCard from '../components/MovieCard'
import SectionHeader from '../components/SectionHeader'

export default function PickMovies(props: {
  likedIds: number[]
  onLike: (m: Movie) => void
  onUnlike: (movieId: number) => void
}) {
  const [popular, setPopular] = useState<Movie[]>([])
  const [searchQ, setSearchQ] = useState('')
  const [searchResults, setSearchResults] = useState<Movie[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const likedSet = useMemo(() => new Set(props.likedIds), [props.likedIds])

  useEffect(() => {
    let mounted = true
    setLoading(true)
    api
      .popular()
      .then((r) => {
        if (mounted) setPopular(r)
      })
      .catch((e) => {
        if (mounted) setError(String(e.message || e))
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })
    return () => {
      mounted = false
    }
  }, [])

  useEffect(() => {
    if (!searchQ.trim()) {
      setSearchResults([])
      return
    }
    const t = setTimeout(() => {
      api
        .search(searchQ.trim())
        .then(setSearchResults)
        .catch((e) => setError(String(e.message || e)))
    }, 250)
    return () => clearTimeout(t)
  }, [searchQ])

  function renderList(list: Movie[]) {
    return (
      <div className="movies">
        {list.map((m) => {
          const liked = likedSet.has(m.movieId)
          return (
            <MovieCard
              key={m.movieId}
              movie={m}
              actionLabel={liked ? 'Liked ✓' : 'Like'}
              onAction={() => (liked ? props.onUnlike(m.movieId) : props.onLike(m))}
              secondaryLabel={liked ? 'Remove' : undefined}
              onSecondary={liked ? () => props.onUnlike(m.movieId) : undefined}
            />
          )
        })}
      </div>
    )
  }

  return (
    <div className="card">
      <SectionHeader
        title="1) Pick movies you like"
        right={<span className="pill">Liked: {props.likedIds.length}</span>}
      />

      <div className="row" style={{ marginBottom: 12 }}>
        <input
          className="input"
          placeholder="Search movies (title contains…)"
          value={searchQ}
          onChange={(e) => setSearchQ(e.target.value)}
        />
        <span className="small">Tip: start typing → top 10 results</span>
      </div>

      {error ? <p className="error">{error}</p> : null}
      {loading ? <p className="small">Loading popular movies…</p> : null}

      {searchQ.trim() ? (
        <>
          <h2>Search results</h2>
          {searchResults.length ? renderList(searchResults) : <p className="small">No results</p>}
        </>
      ) : (
        <>
          <h2>Popular (Top 100)</h2>
          {popular.length ? renderList(popular) : <p className="small">No popular list found.</p>}
        </>
      )}
    </div>
  )
}
