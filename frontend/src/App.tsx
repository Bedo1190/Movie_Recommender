import { useEffect, useMemo, useState } from 'react'
import { getPopular, Movie, recommend, searchMovies } from './lib/api'
import { clearSession, loadLastRecs, loadLiked, saveLastRecs, saveLiked } from './lib/storage'
import { MovieCard } from './components/MovieCard'
import { MovieModal } from './components/MovieModal'

type Tab = 'discover' | 'liked' | 'recs'

export default function App() {
  const [tab, setTab] = useState<Tab>('discover')
  const [popular, setPopular] = useState<Movie[]>([])
  const [searchQ, setSearchQ] = useState('')
  const [searchResults, setSearchResults] = useState<Movie[]>([])
  const [likedIds, setLikedIds] = useState<number[]>(() => loadLiked())
  const [recommendations, setRecommendations] = useState<Movie[]>(() => {
    const last = loadLastRecs()
    return Array.isArray(last) ? (last as Movie[]) : []
  })
  const [topK, setTopK] = useState(10)
  const [loading, setLoading] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [modalMovieId, setModalMovieId] = useState<number | null>(null)

  useEffect(() => {
    let alive = true
    async function run() {
      setLoading('popular')
      setError(null)
      try {
        const data = await getPopular()
        if (alive) setPopular(data)
      } catch (e: any) {
        if (alive) setError(e?.message || 'Failed to load popular movies')
      } finally {
        if (alive) setLoading(null)
      }
    }
    run()
    return () => {
      alive = false
    }
  }, [])

  const likedSet = useMemo(() => new Set(likedIds), [likedIds])

  function toggleLike(movieId: number) {
    setLikedIds((prev) => {
      const next = prev.includes(movieId) ? prev.filter((x) => x !== movieId) : [...prev, movieId]
      saveLiked(next)
      return next
    })
  }

  async function doSearch() {
    const q = searchQ.trim()
    if (!q) {
      setSearchResults([])
      return
    }
    setLoading('search')
    setError(null)
    try {
      const data = await searchMovies(q)
      setSearchResults(data)
    } catch (e: any) {
      setError(e?.message || 'Search failed')
    } finally {
      setLoading(null)
    }
  }

  async function doRecommend() {
    if (likedIds.length === 0) {
      setError('First, like a few movies (at least 1).')
      setTab('discover')
      return
    }

    setLoading('recs')
    setError(null)
    try {
      const data = await recommend(likedIds, topK)
      setRecommendations(data)
      saveLastRecs(data)
      setTab('recs')
    } catch (e: any) {
      setError(e?.message || 'Recommendation request failed')
    } finally {
      setLoading(null)
    }
  }

  function resetSession() {
    clearSession()
    setLikedIds([])
    setRecommendations([])
    setSearchResults([])
    setSearchQ('')
    setError(null)
    setTab('discover')
  }

  const discoverList = searchQ.trim() ? searchResults : popular

  return (
    <div className="page">
      <header className="header">
        <div>
          <div className="h1">Movie Recommender</div>
          <div className="muted">No accounts • Session-based • Like movies → get recommendations</div>
        </div>

        <div className="headerRight">
          <div className="pill">Liked: <b>{likedIds.length}</b></div>
          <button className="btn" onClick={resetSession} type="button" title="Clears sessionStorage">
            Reset session
          </button>
        </div>
      </header>

      <nav className="tabs">
        <button className={tab === 'discover' ? 'tab tab--active' : 'tab'} onClick={() => setTab('discover')} type="button">
          Discover
        </button>
        <button className={tab === 'liked' ? 'tab tab--active' : 'tab'} onClick={() => setTab('liked')} type="button">
          Liked
        </button>
        <button className={tab === 'recs' ? 'tab tab--active' : 'tab'} onClick={() => setTab('recs')} type="button">
          Recommendations
        </button>
      </nav>

      {error ? <div className="error">{error}</div> : null}

      <section className="panel">
        <div className="panelTop">
          <div className="panelTitle">
            {tab === 'discover' ? 'Discover movies' : tab === 'liked' ? 'Your liked movies' : 'Recommendations'}
          </div>

          <div className="panelActions">
            <label className="field">
              <span className="fieldLabel">Top-K</span>
              <input
                className="input"
                type="number"
                min={1}
                max={50}
                value={topK}
                onChange={(e) => setTopK(Math.max(1, Math.min(50, Number(e.target.value) || 10)))}
              />
            </label>

            <button className="btn btn--primary" onClick={doRecommend} type="button" disabled={loading !== null}>
              {loading === 'recs' ? 'Recommending…' : 'Recommend'}
            </button>
          </div>
        </div>

        {tab === 'discover' ? (
          <>
            <div className="searchRow">
              <input
                className="input input--search"
                value={searchQ}
                onChange={(e) => setSearchQ(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') doSearch()
                }}
                placeholder="Search movies by title… (backend: /search?q=...)"
              />
              <button className="btn" onClick={doSearch} type="button" disabled={loading !== null}>
                {loading === 'search' ? 'Searching…' : 'Search'}
              </button>
              <button
                className="btn"
                onClick={() => {
                  setSearchQ('')
                  setSearchResults([])
                }}
                type="button"
                disabled={loading !== null}
              >
                Clear
              </button>
            </div>

            <div className="grid">
              {(discoverList || []).map((m) => (
                <MovieCard
                  key={m.movieId}
                  movie={m}
                  isLiked={likedSet.has(m.movieId)}
                  onToggleLike={toggleLike}
                  onOpenDetails={setModalMovieId}
                />
              ))}
            </div>

            {loading === 'popular' ? <div className="muted">Loading popular…</div> : null}
            {searchQ.trim() && discoverList.length === 0 && loading !== 'search' ? (
              <div className="muted">No search results.</div>
            ) : null}
          </>
        ) : null}

        {tab === 'liked' ? <LikedView likedIds={likedIds} likedSet={likedSet} onToggleLike={toggleLike} onOpenDetails={setModalMovieId} /> : null}

        {tab === 'recs' ? (
          <>
            {recommendations.length === 0 ? (
              <div className="muted">No recommendations yet. Like a few movies and click Recommend.</div>
            ) : (
              <div className="grid">
                {recommendations.map((m) => (
                  <MovieCard
                    key={m.movieId}
                    movie={m}
                    isLiked={likedSet.has(m.movieId)}
                    onToggleLike={toggleLike}
                    onOpenDetails={setModalMovieId}
                  />
                ))}
              </div>
            )}
          </>
        ) : null}
      </section>

      <footer className="footer muted">
        API base: <code>{String((import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000')}</code>
        <span className="dot">•</span>
        Endpoints used: <code>/movies/popular</code>, <code>/search</code>, <code>/recommend</code>, <code>/movies/:id</code>
      </footer>

      <MovieModal movieId={modalMovieId} onClose={() => setModalMovieId(null)} />
    </div>
  )
}

import { getMovie } from './lib/api'

function LikedView({
  likedIds,
  likedSet,
  onToggleLike,
  onOpenDetails
}: {
  likedIds: number[]
  likedSet: Set<number>
  onToggleLike: (id: number) => void
  onOpenDetails: (id: number) => void
}) {
  const [movies, setMovies] = useState<Movie[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true

    async function run() {
      setError(null)
      if (likedIds.length === 0) {
        setMovies([])
        return
      }
      setLoading(true)
      try {
        const list = await Promise.all(likedIds.map((id) => getMovie(id).catch(() => null)))
        const clean = list.filter(Boolean) as Movie[]
        if (alive) setMovies(clean)
      } catch (e: any) {
        if (alive) setError(e?.message || 'Failed to load liked movies')
      } finally {
        if (alive) setLoading(false)
      }
    }

    run()
    return () => {
      alive = false
    }
  }, [likedIds])

  if (likedIds.length === 0) return <div className="muted">You haven't liked any movies yet.</div>

  return (
    <>
      {error ? <div className="error">{error}</div> : null}
      {loading ? <div className="muted">Loading liked movies…</div> : null}

      <div className="grid">
        {movies.map((m) => (
          <MovieCard
            key={m.movieId}
            movie={m}
            isLiked={likedSet.has(m.movieId)}
            onToggleLike={onToggleLike}
            onOpenDetails={onOpenDetails}
          />
        ))}
      </div>
    </>
  )
}
