export const FAVORITES_STORAGE_KEY = 'movie-finder:favorites:v1'
export const FAVORITES_CHANGED_EVENT = 'movie-finder:favorites-changed'

function readStoredFavorites() {
  if (typeof window === 'undefined') return []

  try {
    const parsed = JSON.parse(window.localStorage.getItem(FAVORITES_STORAGE_KEY) || '[]')
    return Array.isArray(parsed) ? parsed.filter((item) => item?.movie_code) : []
  } catch {
    return []
  }
}

function writeStoredFavorites(items) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(FAVORITES_STORAGE_KEY, JSON.stringify(items))
  window.dispatchEvent(new CustomEvent(FAVORITES_CHANGED_EVENT, { detail: items }))
}

export function getFavorites() {
  return readStoredFavorites().sort((a, b) =>
    String(b.saved_at || '').localeCompare(String(a.saved_at || '')),
  )
}

export function isFavorite(movieCode) {
  return readStoredFavorites().some((item) => item.movie_code === movieCode)
}

export function addFavorite(movie) {
  if (!movie?.movie_code) return getFavorites()

  const favorite = {
    movie_code: movie.movie_code,
    movie_name: movie.movie_name || '제목 정보 없음',
    movie_name_english: movie.movie_name_english || null,
    poster_url: movie.poster_url || null,
    production_year: movie.production_year || null,
    open_date: movie.open_date || null,
    movie_type: movie.movie_type || null,
    genre_names: Array.isArray(movie.genre_names) ? movie.genre_names : [],
    director_names: Array.isArray(movie.directors)
      ? movie.directors.map((director) => director.name).filter(Boolean)
      : [],
    saved_at: new Date().toISOString(),
  }

  const remaining = readStoredFavorites().filter(
    (item) => item.movie_code !== favorite.movie_code,
  )
  const next = [favorite, ...remaining]
  writeStoredFavorites(next)
  return next
}

export function removeFavorite(movieCode) {
  const next = readStoredFavorites().filter((item) => item.movie_code !== movieCode)
  writeStoredFavorites(next)
  return next
}

export function toggleFavorite(movie) {
  if (isFavorite(movie?.movie_code)) {
    removeFavorite(movie.movie_code)
    return false
  }
  addFavorite(movie)
  return true
}
