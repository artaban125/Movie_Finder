import { NavLink } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/search', label: '검색' },
  { to: '/box-office', label: '박스오피스' },
  { to: '/favorites', label: '즐겨찾기' },
  { to: '/', label: '소개', end: true },
]

export default function Header({ connectionStatus }) {
  return (
    <header className="site-header">
      <div className="site-header__inner">
        <NavLink to="/" className="brand" end>
          Movie Finder
        </NavLink>
        <nav className="site-nav" aria-label="주요 메뉴">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => (isActive ? 'is-active' : undefined)}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <p
          className={`connection connection--${connectionStatus}`}
          aria-live="polite"
        >
          {connectionStatus === 'checking' && '연결 확인 중'}
          {connectionStatus === 'ok' && '서버 연결됨'}
          {connectionStatus === 'fail' && '서버 연결 실패'}
        </p>
      </div>
    </header>
  )
}
