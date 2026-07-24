import { useCallback, useMemo, useState } from 'react'
import { resolveMediaUrl, searchMovies } from '../api'
import heroImage from '../assets/search-hero.jpg'
import MovieDetailModal from './MovieDetailModal'

const PAGE_SIZE_OPTIONS = [10, 20, 30, 40, 50]

function sortByReleaseDate(movies) {
  return [...movies].sort((a, b) => {
    const dateA = a.open_date || `${a.production_year || 0}-01-01`
    const dateB = b.open_date || `${b.production_year || 0}-01-01`
    return dateB.localeCompare(dateA)
  })
}

function buildOpenYears(startYear = 1950) {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let year = currentYear; year >= startYear; year -= 1) {
    years.push(String(year))
  }
  return years
}

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

const EMPTY_FORM = {
  title: '',
  director: '',
  openYear: '',
}

const EMPTY_RESULT = {
  status: 'idle',
  items: [],
  total: 0,
  page: 1,
  pageSize: 10,
  error: '',
}

export default function SearchSection() {
  const openYears = useMemo(() => buildOpenYears(), [])
  const [form, setForm] = useState(EMPTY_FORM)
  const [pageSize, setPageSize] = useState(10)
  const [result, setResult] = useState(EMPTY_RESULT)
  const [selectedMovieCode, setSelectedMovieCode] = useState(null)
  const [lastQuery, setLastQuery] = useState(null)

  const closeModal = useCallback(() => setSelectedMovieCode(null), [])
  const totalPages = Math.max(1, Math.ceil((result.total || 0) / (result.pageSize || pageSize)))
  const pageItems = useMemo(
    () => buildPageItems(result.page || 1, totalPages),
    [result.page, totalPages],
  )

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const runSearch = async ({ title, director, openDate, page, size }) => {
    setResult((prev) => ({
      ...prev,
      status: 'loading',
      error: '',
      items: [],
      page,
      pageSize: size,
    }))
    try {
      const data = await searchMovies({
        title,
        director,
        openDate,
        page,
        pageSize: size,
      })
      setResult({
        status: 'success',
        items: sortByReleaseDate(data.items || []),
        total: data.total || 0,
        page: data.page || page,
        pageSize: data.page_size || size,
        error: '',
      })
    } catch (error) {
      setResult({
        status: 'error',
        items: [],
        total: 0,
        page: 1,
        pageSize: size,
        error: error.message || '검색에 실패했습니다.',
      })
    }
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    const title = form.title.trim()
    const director = form.director.trim()
    const openDate = form.openYear

    if (!title && !director && !openDate) {
      setResult({
        ...EMPTY_RESULT,
        pageSize,
        status: 'error',
        error: '제목, 감독명, 개봉연도 중 하나 이상을 입력하세요.',
      })
      return
    }

    const query = { title, director, openDate }
    setLastQuery(query)
    await runSearch({ ...query, page: 1, size: pageSize })
  }

  const handleReset = () => {
    setForm(EMPTY_FORM)
    setPageSize(10)
    setLastQuery(null)
    setResult(EMPTY_RESULT)
    setSelectedMovieCode(null)
  }

  const handlePageSizeChange = async (event) => {
    const nextSize = Number(event.target.value)
    setPageSize(nextSize)
    if (!lastQuery || result.status !== 'success') return
    await runSearch({ ...lastQuery, page: 1, size: nextSize })
  }

  const handlePageChange = async (nextPage) => {
    if (!lastQuery || nextPage < 1 || nextPage > totalPages || nextPage === result.page) return
    await runSearch({ ...lastQuery, page: nextPage, size: result.pageSize || pageSize })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const rangeStart = result.total === 0 ? 0 : (result.page - 1) * result.pageSize + 1
  const rangeEnd = Math.min(result.total, result.page * result.pageSize)

  return (
    <section className="search-page">
      <div className="search-hero" style={{ backgroundImage: `url(${heroImage})` }}>
        <div className="search-hero__content">
          <p className="search-hero__eyebrow">DISCOVER YOUR NEXT FILM</p>
          <h1>기억 속 영화를<br />다시 만나는 곳</h1>
          <p>바람과 함께 사라진 기억을 다시 찾아드립니다.</p>
        </div>
      </div>

      <div className="search-page__body">
        <form className="search-form" onSubmit={handleSubmit}>
          <div className="search-form__heading">
            <span aria-hidden="true">⌕</span>
            <div>
              <strong>영화 찾기</strong>
              <small>하나 이상의 조건을 입력하세요</small>
            </div>
          </div>
          <label className="search-field search-field--title">
            <span>영화 제목</span>
            <input
              type="search"
              name="title"
              value={form.title}
              onChange={handleChange}
              placeholder="어떤 영화를 찾고 계신가요?"
              autoComplete="off"
            />
          </label>
          <label className="search-field">
            <span>감독명</span>
            <input
              type="text"
              name="director"
              value={form.director}
              onChange={handleChange}
              placeholder="예: 봉준호"
              autoComplete="off"
            />
          </label>
          <label className="search-field">
            <span>개봉연도</span>
            <select name="openYear" value={form.openYear} onChange={handleChange}>
              <option value="">전체 연도</option>
              {openYears.map((year) => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </label>
          <div className="search-actions">
            <button className="btn btn--primary" type="submit" disabled={result.status === 'loading'}>
              {result.status === 'loading' ? '검색 중…' : '검색하기'}
            </button>
            <button className="btn btn--ghost" type="button" onClick={handleReset}>
              초기화
            </button>
          </div>
        </form>

        {result.status === 'idle' && (
          <div className="search-empty">
            <span aria-hidden="true">🎬</span>
            <strong>찾고 싶은 영화를 검색해 보세요</strong>
            <p>검색 결과에서 포스터와 주요 정보를 한눈에 확인할 수 있습니다.</p>
          </div>
        )}
        {result.status === 'loading' && (
          <div className="state-message" role="status">영화와 포스터를 불러오는 중…</div>
        )}
        {result.status === 'error' && (
          <div className="state-message state-message--error" role="alert">{result.error}</div>
        )}
        {result.status === 'success' && result.items.length === 0 && (
          <div className="state-message">검색 결과가 없습니다.</div>
        )}

        {result.status === 'success' && result.items.length > 0 && (
          <div className="search-results">
            <div className="search-results__head">
              <div>
                <h2>검색 결과</h2>
                <p>
                  전체 {result.total}편 · {rangeStart}-{rangeEnd} 표시
                </p>
              </div>
              <label className="search-page-size">
                <span>페이지당</span>
                <select
                  value={result.pageSize || pageSize}
                  onChange={handlePageSizeChange}
                  aria-label="페이지당 결과 수"
                >
                  {PAGE_SIZE_OPTIONS.map((size) => (
                    <option key={size} value={size}>{size}개</option>
                  ))}
                </select>
              </label>
            </div>

            <ul className="search-results__list">
              {result.items.map((movie) => (
                <li key={movie.movie_code}>
                  <button
                    type="button"
                    className="search-result-item"
                    onClick={() => setSelectedMovieCode(movie.movie_code)}
                    aria-label={`${movie.movie_name} 상세 정보 보기`}
                  >
                    <span className="search-result-item__poster">
                      <span className="search-result-item__no-image">No image</span>
                      {movie.poster_url && (
                        <img
                          src={resolveMediaUrl(movie.poster_url)}
                          alt={`${movie.movie_name} 포스터`}
                          loading="lazy"
                          onError={(event) => event.currentTarget.remove()}
                        />
                      )}
                    </span>
                    <span className="search-result-item__body">
                      <strong>{movie.movie_name}</strong>
                      {movie.movie_name_english && <small>{movie.movie_name_english}</small>}
                      <span className="search-result-item__facts">
                        {[movie.production_year, movie.genre, movie.movie_type]
                          .filter(Boolean)
                          .join(' · ') || '영화 정보 없음'}
                      </span>
                      <span className="search-result-item__director">
                        감독 {movie.director_name || '정보 없음'}
                      </span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>

            {totalPages > 1 && (
              <nav className="search-pagination" aria-label="검색 결과 페이지">
                <button
                  type="button"
                  className="search-pagination__nav"
                  onClick={() => handlePageChange(result.page - 1)}
                  disabled={result.page <= 1 || result.status === 'loading'}
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
                          item === result.page
                            ? 'search-pagination__page is-active'
                            : 'search-pagination__page'
                        }
                        onClick={() => handlePageChange(item)}
                        aria-current={item === result.page ? 'page' : undefined}
                        disabled={result.status === 'loading'}
                      >
                        {item}
                      </button>
                    )
                  ))}
                </div>
                <button
                  type="button"
                  className="search-pagination__nav"
                  onClick={() => handlePageChange(result.page + 1)}
                  disabled={result.page >= totalPages || result.status === 'loading'}
                >
                  다음
                </button>
              </nav>
            )}
          </div>
        )}
      </div>

      {selectedMovieCode && (
        <MovieDetailModal movieCode={selectedMovieCode} onClose={closeModal} />
      )}
    </section>
  )
}
