import { useCallback, useEffect, useState } from 'react'
import { A11y, Autoplay, Navigation } from 'swiper/modules'
import { Swiper, SwiperSlide } from 'swiper/react'
import 'swiper/css'
import 'swiper/css/navigation'

import { fetchBoxOffice, resolveMediaUrl } from '../api'
import MovieDetailModal from './MovieDetailModal'

const PERIODS = [
  { value: 'daily', label: '오늘' },
  { value: 'weekly', label: '주간' },
]

export default function BoxOfficeSection() {
  const [period, setPeriod] = useState('daily')
  const [autoplayDelay, setAutoplayDelay] = useState(2000)
  const [result, setResult] = useState({ status: 'loading', data: null, error: '' })
  const [selectedMovieCode, setSelectedMovieCode] = useState(null)

  useEffect(() => {
    let active = true
    setResult({ status: 'loading', data: null, error: '' })
    fetchBoxOffice({ period })
      .then((data) => {
        if (active) setResult({ status: 'success', data, error: '' })
      })
      .catch((error) => {
        if (active) {
          setResult({ status: 'error', data: null, error: error.message })
        }
      })
    return () => {
      active = false
    }
  }, [period])

  const closeModal = useCallback(() => setSelectedMovieCode(null), [])
  const items = result.data?.items ?? []

  return (
    <section className="section">
      <div className="box-office__header">
        <div className="section__head">
          <h2>박스오피스 Top 10</h2>
        </div>

        <div className="box-office__controls">
          <div className="period-tabs" aria-label="박스오피스 기간">
            {PERIODS.map((item) => (
              <button
                type="button"
                key={item.value}
                className={period === item.value ? 'is-active' : ''}
                onClick={() => setPeriod(item.value)}
                aria-pressed={period === item.value}
              >
                {item.label}
              </button>
            ))}
          </div>
          <label className="speed-control">
            재생 간격
            <select
              value={autoplayDelay}
              onChange={(event) => setAutoplayDelay(Number(event.target.value))}
            >
              <option value={1000}>1초</option>
              <option value={1500}>1.5초</option>
              <option value={2000}>2초</option>
            </select>
          </label>
        </div>
      </div>

      {result.status === 'loading' && (
        <div className="state-message" role="status">박스오피스를 불러오는 중…</div>
      )}
      {result.status === 'error' && (
        <div className="state-message state-message--error" role="alert">{result.error}</div>
      )}
      {result.status === 'success' && items.length === 0 && (
        <div className="state-message">조회된 박스오피스가 없습니다.</div>
      )}

      {items.length > 0 && (
        <Swiper
          key={`${period}-${autoplayDelay}`}
          className="box-office-swiper"
          modules={[A11y, Autoplay, Navigation]}
          slidesPerView={1}
          spaceBetween={16}
          speed={400}
          loop
          navigation
          autoplay={{
            delay: autoplayDelay,
            disableOnInteraction: false,
            pauseOnMouseEnter: true,
          }}
          breakpoints={{
            640: { slidesPerView: 3 },
            1024: { slidesPerView: 5 },
          }}
        >
          {items.map((movie) => (
            <SwiperSlide key={`${movie.movie_code}-${movie.rank}`}>
              <button
                type="button"
                className="movie-card"
                onClick={() => setSelectedMovieCode(movie.movie_code)}
              >
                <span className="movie-card__rank">{movie.rank}</span>
                <span className="movie-card__poster">
                  {movie.poster_url ? (
                    <img
                      src={resolveMediaUrl(movie.poster_url)}
                      alt={`${movie.movie_name} 포스터`}
                      loading="lazy"
                      onError={(event) => event.currentTarget.remove()}
                    />
                  ) : (
                    <span aria-hidden="true">{movie.movie_name.slice(0, 1)}</span>
                  )}
                </span>
                <span className="movie-card__body">
                  <strong>{movie.movie_name}</strong>
                  {movie.movie_name_english && <small>{movie.movie_name_english}</small>}
                  <span className="movie-card__facts">
                    {[movie.production_year, movie.genre, movie.movie_type]
                      .filter(Boolean)
                      .join(' · ') || '영화 정보 없음'}
                  </span>
                  <span className="movie-card__director">
                    감독 {movie.director_name || '정보 없음'}
                  </span>
                </span>
              </button>
            </SwiperSlide>
          ))}
        </Swiper>
      )}

      {selectedMovieCode && (
        <MovieDetailModal movieCode={selectedMovieCode} onClose={closeModal} />
      )}
    </section>
  )
}
