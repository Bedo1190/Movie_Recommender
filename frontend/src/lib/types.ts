export type Movie = {
  movieId: number
  title?: string
  poster_url?: string
  year?: number | null
  genres?: string
  rating_mean?: number
}

export type Genre = {
  id?: number
  name: string
}
