import { useCallback, useEffect, useState } from 'react'
import { fetchDirectorDetail, fetchMovieDetail, resolveMediaUrl } from '../api'
import { isFavorite, toggleFavorite } from '../favorites'
import Modal from './Modal'

function textOrFallback(value, fallback = '정보 없음') {
  if (value === null || value === undefined) return fallback
  const text = String(value).trim()
  return text || fallback
}

function joinNames(items, mapper) {
  if (!items?.length) return '정보 없음'
  return items.map(mapper).filter(Boolean).join(', ') || '정보 없음'
}

function DetailSection({ title, children, empty = false }) {
  return (
    <section className="movie-modal__section">
      <h3>{title}</h3>
      {empty ? <p className="movie-modal__empty">정보 없음</p> : children}
    </section>
  )
}

function DirectorDetailView({
  director,
  status,
  error,
  movieTitle,
  onBack,
  onSelectMovie,
}) {
  if (status === 'loading') {
    return <p className="state-message" role="status">감독 정보를 불러오는 중…</p>
  }
  if (status === 'error') {
    return (
      <div className="director-detail">
        <button type="button" className="movie-modal__back" onClick={onBack}>
          ← {movieTitle ? `${movieTitle} 상세로 돌아가기` : '영화 상세로 돌아가기'}
        </button>
        <p className="state-message state-message--error" role="alert">{error}</p>
      </div>
    )
  }
  if (!director) return null

  return (
    <div className="director-detail">
      <button type="button" className="movie-modal__back" onClick={onBack}>
        ← {movieTitle ? `${movieTitle} 상세로 돌아가기` : '영화 상세로 돌아가기'}
      </button>

      <header className="director-detail__header">
        <p className="movie-modal__kicker">
          {director.rep_role_name || '영화인'} · DIRECTOR
        </p>
        <h2 id="movie-modal-title">{director.people_name}</h2>
        {director.people_name_english && (
          <p className="movie-modal__english">{director.people_name_english}</p>
        )}
      </header>

      <DetailSection title="기본 정보">
        <dl className="movie-facts">
          <div>
            <dt>영화인명(국문)</dt>
            <dd>{textOrFallback(director.people_name)}</dd>
          </div>
          <div>
            <dt>영화인명(영문)</dt>
            <dd>{textOrFallback(director.people_name_english)}</dd>
          </div>
          <div>
            <dt>성별</dt>
            <dd>{textOrFallback(director.sex)}</dd>
          </div>
          <div>
            <dt>분야</dt>
            <dd>{textOrFallback(director.rep_role_name)}</dd>
          </div>
          <div>
            <dt>영화인코드</dt>
            <dd>{textOrFallback(director.people_code)}</dd>
          </div>
          <div>
            <dt>관련 URL</dt>
            <dd>
              {director.homepages ? (
                <a href={director.homepages} target="_blank" rel="noreferrer">
                  {director.homepages}
                </a>
              ) : (
                '정보 없음'
              )}
            </dd>
          </div>
        </dl>
      </DetailSection>

      <DetailSection title="참여 영화" empty={!director.filmos?.length}>
        <ul className="movie-modal__list movie-modal__list--dense">
          {director.filmos.map((filmo, index) => {
            const clickable = Boolean(filmo.movie_code)
            const content = (
              <>
                <div>
                  <strong>{filmo.movie_name}</strong>
                  {filmo.movie_part_name && <span>{filmo.movie_part_name}</span>}
                </div>
                {filmo.movie_code && <p>영화코드 {filmo.movie_code}</p>}
              </>
            )
            return (
              <li key={`${filmo.movie_code || filmo.movie_name}-${index}`}>
                {clickable ? (
                  <button
                    type="button"
                    className="director-filmo-button"
                    onClick={() => onSelectMovie(filmo.movie_code)}
                    aria-label={`${filmo.movie_name} 상세 정보 보기`}
                  >
                    {content}
                  </button>
                ) : (
                  content
                )}
              </li>
            )
          })}
        </ul>
      </DetailSection>
    </div>
  )
}

export default function MovieDetailModal({ movieCode, onClose }) {
  const [activeMovieCode, setActiveMovieCode] = useState(movieCode)
  const [view, setView] = useState('movie')
  const [state, setState] = useState({ status: 'loading', data: null, error: '' })
  const [directorState, setDirectorState] = useState({
    status: 'idle',
    data: null,
    error: '',
  })
  const [favorite, setFavorite] = useState(() => isFavorite(movieCode))

  useEffect(() => {
    setActiveMovieCode(movieCode)
    setView('movie')
  }, [movieCode])

  useEffect(() => {
    let active = true
    setState({ status: 'loading', data: null, error: '' })
    setFavorite(isFavorite(activeMovieCode))
    fetchMovieDetail(activeMovieCode)
      .then((data) => {
        if (active) setState({ status: 'success', data, error: '' })
      })
      .catch((error) => {
        if (active) {
          setState({
            status: 'error',
            data: null,
            error: error.message || '상세 조회에 실패했습니다.',
          })
        }
      })
    return () => {
      active = false
    }
  }, [activeMovieCode])

  const movie = state.data

  const handleFavoriteToggle = () => {
    if (!movie) return
    setFavorite(toggleFavorite(movie))
  }

  const openDirector = useCallback(
    async (directorName) => {
      const name = (directorName || '').trim()
      if (!name) return
      setView('director')
      setDirectorState({ status: 'loading', data: null, error: '' })
      try {
        const data = await fetchDirectorDetail({
          name,
          movieName: movie?.movie_name,
        })
        setDirectorState({ status: 'success', data, error: '' })
      } catch (error) {
        setDirectorState({
          status: 'error',
          data: null,
          error: error.message || '감독 정보를 불러오지 못했습니다.',
        })
      }
    },
    [movie?.movie_name],
  )

  const backToMovie = () => {
    setView('movie')
    setDirectorState({ status: 'idle', data: null, error: '' })
  }

  const openMovieFromFilmo = (nextMovieCode) => {
    if (!nextMovieCode) return
    setActiveMovieCode(nextMovieCode)
    setView('movie')
    setDirectorState({ status: 'idle', data: null, error: '' })
  }

  const labelledBy =
    view === 'director' ? 'movie-modal-title' : 'movie-modal-title'

  return (
    <Modal labelledBy={labelledBy} onClose={onClose} className="movie-modal">
      {view === 'director' ? (
        <DirectorDetailView
          director={directorState.data}
          status={directorState.status}
          error={directorState.error}
          movieTitle={movie?.movie_name}
          onBack={backToMovie}
          onSelectMovie={openMovieFromFilmo}
        />
      ) : (
        <>
          {state.status === 'loading' && (
            <p className="state-message" role="status">상세 정보를 불러오는 중…</p>
          )}
          {state.status === 'error' && (
            <p className="state-message state-message--error" role="alert">
              {state.error}
            </p>
          )}

          {movie && (
            <>
              <div className="movie-modal__hero">
                <div className="movie-modal__poster">
                  <span className="movie-modal__no-image">No image</span>
                  {movie.poster_url && (
                    <img
                      src={resolveMediaUrl(movie.poster_url)}
                      alt={`${movie.movie_name} 포스터`}
                      onError={(event) => event.currentTarget.remove()}
                    />
                  )}
                </div>

                <header className="movie-modal__header">
                  <p className="movie-modal__kicker">
                    {[movie.production_year, movie.movie_type]
                      .filter(Boolean)
                      .join(' · ') || '영화 상세'}
                  </p>
                  <h2 id="movie-modal-title">{movie.movie_name}</h2>
                  {movie.movie_name_english && (
                    <p className="movie-modal__english">{movie.movie_name_english}</p>
                  )}
                  <div className="movie-modal__summary">
                    {movie.open_date && <span>개봉 {movie.open_date}</span>}
                    {movie.show_time_minutes && (
                      <span>{movie.show_time_minutes}분</span>
                    )}
                    {movie.genre_names?.length > 0 && (
                      <span>{movie.genre_names.join(' · ')}</span>
                    )}
                  </div>
                  <p className="movie-modal__director">
                    감독{' '}
                    {movie.directors?.length
                      ? movie.directors.map((director, index) => (
                          <span key={`${director.name}-${index}`}>
                            {index > 0 && ', '}
                            <button
                              type="button"
                              className="movie-modal__director-link"
                              onClick={() => openDirector(director.name)}
                            >
                              {director.name}
                            </button>
                          </span>
                        ))
                      : '정보 없음'}
                  </p>
                  <button
                    type="button"
                    className={
                      favorite
                        ? 'movie-modal__favorite is-active'
                        : 'movie-modal__favorite'
                    }
                    onClick={handleFavoriteToggle}
                    aria-pressed={favorite}
                  >
                    <span aria-hidden="true">{favorite ? '★' : '☆'}</span>
                    {favorite ? '즐겨찾기 해제' : '즐겨찾기 추가'}
                  </button>
                </header>
              </div>

              <DetailSection title="기본 정보">
                <dl className="movie-facts">
                  <div>
                    <dt>영화명(국문)</dt>
                    <dd>{textOrFallback(movie.movie_name)}</dd>
                  </div>
                  <div>
                    <dt>영화명(영문)</dt>
                    <dd>{textOrFallback(movie.movie_name_english)}</dd>
                  </div>
                  <div>
                    <dt>제작연도</dt>
                    <dd>{textOrFallback(movie.production_year)}</dd>
                  </div>
                  <div>
                    <dt>상영시간</dt>
                    <dd>
                      {movie.show_time_minutes
                        ? `${movie.show_time_minutes}분`
                        : '정보 없음'}
                    </dd>
                  </div>
                  <div>
                    <dt>개봉일</dt>
                    <dd>{textOrFallback(movie.open_date)}</dd>
                  </div>
                  <div>
                    <dt>제작상태</dt>
                    <dd>{textOrFallback(movie.production_status)}</dd>
                  </div>
                  <div>
                    <dt>영화유형</dt>
                    <dd>{textOrFallback(movie.movie_type)}</dd>
                  </div>
                  <div>
                    <dt>제작국가</dt>
                    <dd>{joinNames(movie.nation_names, (name) => name)}</dd>
                  </div>
                  <div>
                    <dt>장르</dt>
                    <dd>{joinNames(movie.genre_names, (name) => name)}</dd>
                  </div>
                </dl>
              </DetailSection>

              <DetailSection title="감독" empty={!movie.directors?.length}>
                <ul className="movie-modal__list">
                  {movie.directors.map((director, index) => (
                    <li key={`${director.name}-${index}`}>
                      <button
                        type="button"
                        className="movie-modal__director-card"
                        onClick={() => openDirector(director.name)}
                        aria-label={`${director.name} 감독 상세 보기`}
                      >
                        <strong>{director.name}</strong>
                        {director.name_english && (
                          <span>{director.name_english}</span>
                        )}
                      </button>
                    </li>
                  ))}
                </ul>
              </DetailSection>

              <DetailSection title="배우" empty={!movie.actors?.length}>
                <ul className="movie-modal__list movie-modal__list--dense">
                  {movie.actors.map((actor, index) => (
                    <li key={`${actor.name}-${index}`}>
                      <div>
                        <strong>{actor.name}</strong>
                        {actor.name_english && <span>{actor.name_english}</span>}
                      </div>
                      {(actor.cast_name || actor.cast_name_english) && (
                        <p>
                          배역 {actor.cast_name || '정보 없음'}
                          {actor.cast_name_english
                            ? ` / ${actor.cast_name_english}`
                            : ''}
                        </p>
                      )}
                    </li>
                  ))}
                </ul>
              </DetailSection>

              <DetailSection title="상영 정보" empty={!movie.show_types?.length}>
                <ul className="movie-modal__list">
                  {movie.show_types.map((showType, index) => (
                    <li
                      key={`${showType.group_name}-${showType.type_name}-${index}`}
                    >
                      <strong>{showType.type_name || '상영형태 미상'}</strong>
                      {showType.group_name && <span>{showType.group_name}</span>}
                    </li>
                  ))}
                </ul>
              </DetailSection>

              <DetailSection title="심의 정보" empty={!movie.audits?.length}>
                <ul className="movie-modal__list">
                  {movie.audits.map((audit, index) => (
                    <li key={`${audit.audit_number}-${index}`}>
                      <strong>
                        {textOrFallback(audit.watch_grade_name, '관람등급 미상')}
                      </strong>
                      <span>
                        심의번호 {textOrFallback(audit.audit_number)}
                      </span>
                    </li>
                  ))}
                </ul>
              </DetailSection>

              <DetailSection title="참여 영화사" empty={!movie.companies?.length}>
                <ul className="movie-modal__list movie-modal__list--dense">
                  {movie.companies.map((company, index) => (
                    <li
                      key={`${company.company_code || company.company_name}-${index}`}
                    >
                      <div>
                        <strong>{company.company_name}</strong>
                        {company.company_name_english && (
                          <span>{company.company_name_english}</span>
                        )}
                      </div>
                      <p>
                        {[
                          company.company_part_name,
                          company.company_code
                            ? `코드 ${company.company_code}`
                            : null,
                        ]
                          .filter(Boolean)
                          .join(' · ') || '분야 정보 없음'}
                      </p>
                    </li>
                  ))}
                </ul>
              </DetailSection>

              <DetailSection title="스태프" empty={!movie.staffs?.length}>
                <ul className="movie-modal__list movie-modal__list--dense">
                  {movie.staffs.map((staff, index) => (
                    <li key={`${staff.name}-${staff.role_name}-${index}`}>
                      <div>
                        <strong>{staff.name}</strong>
                        {staff.name_english && <span>{staff.name_english}</span>}
                      </div>
                      <p>
                        {textOrFallback(staff.role_name, '역할 정보 없음')}
                      </p>
                    </li>
                  ))}
                </ul>
              </DetailSection>
            </>
          )}
        </>
      )}
    </Modal>
  )
}
