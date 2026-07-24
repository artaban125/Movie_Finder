import { Link } from 'react-router-dom'

export default function IntroSection() {
  return (
    <section className="section intro">
      <div className="intro__hero">
        <p className="intro__kicker">영화 검색 · 박스오피스</p>
        <h1 className="intro__brand">Movie Finder</h1>
        <p className="intro__lead">
          제목·감독·개봉연도로 영화를 검색하고, 박스오피스 Top 10과 상세 정보를
          한곳에서 살펴보세요.
        </p>
        <div className="intro__actions">
          <Link className="btn btn--primary" to="/search">
            영화 검색하기
          </Link>
          <Link className="btn btn--ghost" to="/box-office">
            박스오피스 보기
          </Link>
        </div>
      </div>

      <div className="intro__panels">
        <article className="intro-panel">
          <h2>서비스 소개</h2>
          <p>
            Movie Finder는 기억이 흐릿한 영화도 다양한 조건으로 쉽게 찾을 수 있게
            돕는 웹서비스입니다. 공공데이터 기반의 영화 정보와 박스오피스를
            FastAPI가 가공해 React 화면에 제공합니다.
          </p>
        </article>

        <article className="intro-panel">
          <h2>주요 기능</h2>
          <ul>
            <li>박스오피스 Top 10 캐러셀</li>
            <li>영화 제목 · 감독명 · 개봉연도 검색</li>
            <li>검색 결과 및 상세 정보 팝업 조회</li>
          </ul>
        </article>

        <article className="intro-panel">
          <h2>검색 사용 방법</h2>
          <ol>
            <li>검색 메뉴로 이동합니다.</li>
            <li>제목, 감독명, 개봉연도 중 하나 이상을 입력합니다.</li>
            <li>검색 결과 항목을 클릭하면 상세 정보가 팝업으로 열립니다.</li>
          </ol>
        </article>
      </div>
    </section>
  )
}
