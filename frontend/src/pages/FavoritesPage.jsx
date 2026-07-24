import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { resolveMediaUrl } from '../api'
import MovieDetailModal from '../components/MovieDetailModal'
import {
  FAVORITES_CHANGED_EVENT,
  FAVORITES_STORAGE_KEY,
  getFavorites,
  removeFavorite,
} from '../favorites'

const PAGE_SIZE_OPTIONS = [10, 20, 30, 40, 50]

function buildPageItems(currentPage, totalPages) {
  if (totalPages <= 7) {
    return Array.from({ length: totalPages }, (_, index) => index + 1)
  }

  const pages = new Set([1, totalPages, currentPage - 1, currentPage, currentPage + 1])
  if (currentPage <= 3) {
    pages.add(2)
    pages.add(3)
    pages.add(4)
  }
  if (currentPage >= totalPages - 2) {
    pages.add(totalPages - 3)
    pages.add(totalPages - 2)
    pages.add(totalPages - 1)
  }

  const sorted = [...pages].filter((page) => page >= 1 && page <= totalPages).sort((a, b) => a - b)
  const items = []
  for (const page of sorted) {
    const previous = items[items.length - 1]
    if (typeof previous === 'number' && page - previous > 1) {
      items.push('…')
    }
    items.push(page)
  }
  return items
}

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState(() => getFavorites())
  const [selectedMovieCode, setSelectedMovieCode] = useState(null)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)

  useEffect(() => {
    const refresh = () => setFavorites(getFavorites())
    const handleStorage = (event) => {
      if (event.key === FAVORITES_STORAGE_KEY) refresh()
    }

    window.addEventListener(FAVORITES_CHANGED_EVENT, refresh)
    window.addEventListener('storage', handleStorage)
    return () => {
      window.removeEventListener(FAVORITES_CHANGED_EVENT, refresh)
      window.removeEventListener('storage', handleStorage)
    }
  }, [])

  const total = favorites.length
  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  useEffect(() => {
    if (page > totalPages) setPage(totalPages)
  }, [page, totalPages])

  const pageItems = useMemo(() => buildPageItems(page, totalPages), [page, totalPages])
  const pagedFavorites = useMemo(() => {
    const start = (page - 1) * pageSize
    return favorites.slice(start, start + pageSize)
  }, [favorites, page, pageSize])

  const rangeStart = total === 0 ? 0 : (page - 1) * pageSize + 1
  const rangeEnd = Math.min(total, page * pageSize)

  const closeModal = useCallback(() => setSelectedMovieCode(null), [])

  const handleRemove = (movieCode) => {
    setFavorites(removeFavorite(movieCode))
  }

  const handlePageSizeChange = (event) => {
    setPageSize(Number(event.target.value))
    setPage(1)
  }

  const handlePageChange = (nextPage) => {
    if (nextPage < 1 || nextPage > totalPages || nextPage === page) return
    setPage(nextPage)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <section className="favorites-page">
      <header className="favorites-page__header">
        <p className="favorites-page__eyebrow">MY COLLECTION</p>
        <h1>즐겨찾기</h1>
        <p>다시 보고 싶은 영화를 한곳에 모아보세요.</p>
      </header>

      {favorites.length === 0 ? (
        <div className="favorites-empty">
          <span aria-hidden="true">☆</span>
          <h2>저장한 영화가 없습니다</h2>
          <p>영화 상세 화면에서 즐겨찾기에 추가할 수 있습니다.</p>
          <Link className="btn btn--primary" to="/search">영화 검색하기</Link>
        </div>
      ) : (
        <>
          <div className="favorites-page__summary">
            <div>
              <h2>저장한 영화</h2>
              <p>
                전체 {total}편 · {rangeStart}-{rangeEnd} 표시
              </p>
            </div>
            <label className="search-page-size">
              <span>페이지당</span>
              <select
                value={pageSize}
                onChange={handlePageSizeChange}
                aria-label="페이지당 결과 수"
              >
                {PAGE_SIZE_OPTIONS.map((size) => (
                  <option key={size} value={size}>{size}개</option>
                ))}
              </select>
            </label>
          </div>

          <ul className="favorites-grid">
            {pagedFavorites.map((movie) => (
              <li key={movie.movie_code} className="favorite-card">
                <button
                  type="button"
                  className="favorite-card__movie"
                  onClick={() => setSelectedMovieCode(movie.movie_code)}
                  aria-label={`${movie.movie_name} 상세 정보 보기`}
                >
                  <span className="favorite-card__poster">
                    <span className="favorite-card__no-image">No image</span>
                    {movie.poster_url && (
                      <img
                        src={resolveMediaUrl(movie.poster_url)}
                        alt={`${movie.movie_name} 포스터`}
                        loading="lazy"
                        onError={(event) => event.currentTarget.remove()}
                      />
                    )}
                  </span>
                  <span className="favorite-card__body">
                    <strong>{movie.movie_name}</strong>
                    {movie.movie_name_english && <small>{movie.movie_name_english}</small>}
                    <span>
                      {[
                        movie.production_year,
                        ...(movie.genre_names || []).slice(0, 2),
                      ]
                        .filter(Boolean)
                        .join(' · ') || '영화 정보 없음'}
                    </span>
                    {(movie.director_names || []).length > 0 && (
                      <span>감독 {movie.director_names.join(', ')}</span>
                    )}
                  </span>
                </button>
                <button
                  type="button"
                  className="favorite-card__remove"
                  onClick={() => handleRemove(movie.movie_code)}
                  aria-label={`${movie.movie_name} 즐겨찾기에서 삭제`}
                >
                  삭제
                </button>
              </li>
            ))}
          </ul>

          {totalPages > 1 && (
            <nav className="search-pagination" aria-label="즐겨찾기 페이지">
              <button
                type="button"
                className="search-pagination__nav"
                onClick={() => handlePageChange(page - 1)}
                disabled={page <= 1}
              >
                이전
              </button>
              <div className="search-pagination__pages">
                {pageItems.map((item, index) => (
                  item === '…' ? (
                    <span key={`ellipsis-${index}`} className="search-pagination__ellipsis">…</span>
                  ) : (
                    <button
                      key={item}
                      type="button"
                      className={
                        item === page
                          ? 'search-pagination__page is-active'
                          : 'search-pagination__page'
                      }
                      onClick={() => handlePageChange(item)}
                      aria-current={item === page ? 'page' : undefined}
                    >
                      {item}
                    </button>
                  )
                ))}
              </div>
              <button
                type="button"
                className="search-pagination__nav"
                onClick={() => handlePageChange(page + 1)}
                disabled={page >= totalPages}
              >
                다음
              </button>
            </nav>
          )}
        </>
      )}

      {selectedMovieCode && (
        <MovieDetailModal movieCode={selectedMovieCode} onClose={closeModal} />
      )}
    </section>
  )
}
