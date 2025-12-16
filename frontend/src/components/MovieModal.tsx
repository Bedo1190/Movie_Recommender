import { useEffect, useState } from 'react'
import { getMovie, Movie } from '../lib/api'

type Props = {
  movieId: number | null
  onClose: () => void
}

export function MovieModal({ movieId, onClose }: Props) {
  const [movie, setMovie] = useState<Movie | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    async function run() {
      if (movieId == null) return
      setLoading(true)
      setError(null)
      try {
        const data = await getMovie(movieId)
        if (alive) setMovie(data)
      } catch (e: any) {
        if (alive) setError(e?.message || 'Failed to load')
      } finally {
        if (alive) setLoading(false)
      }
    }
    run()
    return () => {
      alive = false
    }
  }, [movieId])

  if (movieId == null) return null

  const poster = movie?.poster_url && movie.poster_url.trim() ? movie.poster_url : ''

  return (
    <div className="modalOverlay" onMouseDown={onClose}>
      <div className="modal" onMouseDown={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
        <div className="modalHeader">
          <div className="modalTitle">{movie?.title || `Movie #${movieId}`}</div>
          <button className="btn" onClick={onClose} type="button">
            Close
          </button>
        </div>

        {loading ? <div className="muted">Loading…</div> : null}
        {error ? <div className="error">{error}</div> : null}

        {movie ? (
          <div className="modalBody">
            <div className="modalPoster">
              {poster ? <img src={poster} alt={movie.title} /> : <div className="posterFallback">No Poster</div>}
            </div>

            <div className="modalInfo">
              <div className="row"><span className="label">Year:</span> {movie.year ?? '—'}</div>
              <div className="row"><span className="label">Genres:</span> {movie.genres || '—'}</div>
              {typeof movie.rating_mean === 'number' ? (
                <div className="row"><span className="label">Rating mean:</span> {movie.rating_mean.toFixed(2)}</div>
              ) : null}
              {movie.overview ? (
                <div className="overview">
                  <div className="label">Overview</div>
                  <div className="muted">{movie.overview}</div>
                </div>
              ) : null}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  )
}
