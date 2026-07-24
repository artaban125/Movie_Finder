// ---------------------------------------------------------------
// 백엔드(FastAPI) 호출 함수 모음
// 화면은 여기 함수만 부른다. 주소가 바뀌면 BASE_URL 한 줄만 수정.
// ---------------------------------------------------------------
const BASE_URL = 'http://127.0.0.1:8000'

export function resolveMediaUrl(path) {
  if (!path) return ''
  if (/^https?:\/\//i.test(path)) return path
  return `${BASE_URL}${path.startsWith('/') ? path : `/${path}`}`
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, options)
  if (!res.ok) {
    let detail = `요청 실패 (${res.status})`
    try {
      const body = await res.json()
      if (typeof body.detail === 'string') detail = body.detail
    } catch {
      // JSON이 아니면 기본 메시지 사용
    }
    throw new Error(detail)
  }
  return res.json()
}

/** 백엔드가 살아있는지 확인 (연결 테스트용) */
export async function checkHealth() {
  return request('/health')
}

/** 어제/주간 박스오피스 Top 10 조회 */
export async function fetchBoxOffice({ period = 'daily', targetDate } = {}) {
  const params = new URLSearchParams()
  params.set('period', period)
  if (targetDate) params.set('target_date', targetDate)
  return request(`/api/box-office?${params.toString()}`)
}

/**
 * 영화 검색
 * @param {{ title?: string, director?: string, openDate?: string, page?: number, pageSize?: number }} filters
 */
export async function searchMovies({
  title,
  director,
  openDate,
  page = 1,
  pageSize = 10,
} = {}) {
  const params = new URLSearchParams()
  if (title) params.set('title', title)
  if (director) params.set('director', director)
  if (openDate) params.set('open_date', openDate)
  params.set('page', String(page))
  params.set('page_size', String(pageSize))
  const query = params.toString()
  if (!title && !director && !openDate) throw new Error('검색 조건을 입력하세요.')
  return request(`/api/movies/search?${query}`)
}

/** 영화 상세 조회 */
export async function fetchMovieDetail(movieCode) {
  if (!movieCode) throw new Error('영화코드가 필요합니다.')
  return request(`/api/movies/${encodeURIComponent(movieCode)}`)
}

/**
 * 감독명으로 영화인 목록에서 감독 코드를 찾아 상세를 조회한다.
 * @param {{ name: string, movieName?: string }} params
 */
export async function fetchDirectorDetail({ name, movieName } = {}) {
  const directorName = (name || '').trim()
  if (!directorName) throw new Error('감독명이 필요합니다.')
  const params = new URLSearchParams()
  params.set('name', directorName)
  if (movieName) params.set('movie_name', movieName)
  return request(`/api/directors?${params.toString()}`)
}

/** 영화인코드로 상세 조회 */
export async function fetchPeopleDetail(peopleCode) {
  if (!peopleCode) throw new Error('영화인코드가 필요합니다.')
  return request(`/api/people/${encodeURIComponent(peopleCode)}`)
}
