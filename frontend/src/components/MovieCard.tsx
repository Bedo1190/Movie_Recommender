import { Movie } from '../lib/api'

type Props = {
  movie: Movie
  isLiked: boolean
  onToggleLike: (movieId: number) => void
  onOpenDetails?: (movieId: number) => void
  compact?: boolean
}

export function MovieCard({ movie, isLiked, onToggleLike, onOpenDetails, compact }: Props) {
  const poster = movie.poster_url && movie.poster_url.trim() ? movie.poster_url : ''

  return (
    <div className={compact ? 'card card--compact' : 'card'}>
      <button
        className="poster"
        onClick={() => onOpenDetails?.(movie.movieId)}
        title="Details"
        type="button"
      >
        {poster ? (
          <img src={poster} alt={movie.title} loading="lazy" />
        ) : (
          <div className="posterFallback">No Poster</div>
        )}
      </button>

      <div className="cardBody">
        <div className="titleRow">
          <div className="title" title={movie.title}>
            {movie.title}
          </div>
          <div className="meta">{movie.year ?? ''}</div>
        </div>

        {movie.genres ? <div className="genres">{movie.genres}</div> : null}

        <div className="actions">
          <button
            className={isLiked ? 'btn btn--liked' : 'btn'}
            onClick={() => onToggleLike(movie.movieId)}
            type="button"
          >
            {isLiked ? 'Liked ✓' : 'Like'}
          </button>

          {typeof movie.rating_mean === 'number' && Number.isFinite(movie.rating_mean) ? (
            <div className="rating" title="Mean rating">
              ★ {movie.rating_mean.toFixed(2)}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}
