import { useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'
import type { Movie } from '../lib/types'
import MovieCard from '../components/MovieCard'
import SectionHeader from '../components/SectionHeader'

export default function Recommendations(props: {
  likedIds: number[]
  onUnlike: (movieId: number) => void
}) {
  const [topK, setTopK] = useState(10)
  const [recs, setRecs] = useState<Movie[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [modelStatus, setModelStatus] = useState<string>('')

  const canRecommend = useMemo(() => props.likedIds.length > 0, [props.likedIds.length])

  useEffect(() => {
    api
      .health()
      .then((r) => setModelStatus(r.model_status))
      .catch(() => setModelStatus('Unknown'))
  }, [])

  async function runRecommend() {
    setError(null)
    setLoading(true)
    try {
      const result = await api.recommend(props.likedIds, topK)
      setRecs(result)
    } catch (e: any) {
      setError(String(e?.message || e))
      setRecs([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <SectionHeader
        title="2) Get recommendations"
        right={<span className="pill">Model: {modelStatus || '—'}</span>}
      />

      <div className="row" style={{ marginBottom: 12 }}>
        <label className="pill">
          Top K:&nbsp;
          <input
            style={{ width: 64, background: 'transparent', border: 'none', color: 'inherit', outline: 'none' }}
            type="number"
            min={1}
            max={50}
            value={topK}
            onChange={(e) => setTopK(Math.max(1, Math.min(50, Number(e.target.value) || 10)))}
          />
        </label>
        <button className="btn primary" disabled={!canRecommend || loading} onClick={runRecommend}>
          {loading ? 'Recommending…' : 'Recommend'}
        </button>
        {!canRecommend ? <span className="small">Select at least 1 movie.</span> : null}
      </div>

      {error ? <p className="error">{error}</p> : null}

      {recs.length ? (
        <div className="movies">
          {recs.map((m) => (
            <MovieCard
              key={m.movieId}
              movie={m}
              actionLabel="Like"
              onAction={() => {
                // If user likes a recommendation, we simply add it to liked list by pretending it was selected.
                // But since this component doesn't own state, we offer a shortcut: remove from liked instead.
                // (Your team can extend with an onLike callback if you want.)
                alert('If you want: we can add an “Add to liked” flow here.')
              }}
              secondaryLabel={props.likedIds.includes(m.movieId) ? 'Remove from liked' : undefined}
              onSecondary={props.likedIds.includes(m.movieId) ? () => props.onUnlike(m.movieId) : undefined}
            />
          ))}
        </div>
      ) : (
        <p className="small">No recommendations yet.</p>
      )}
    </div>
  )
}
