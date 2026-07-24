import { useEffect, useState } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { checkHealth } from './api'
import Header from './components/Header'
import BoxOfficePage from './pages/BoxOfficePage'
import FavoritesPage from './pages/FavoritesPage'
import HomePage from './pages/HomePage'
import SearchPage from './pages/SearchPage'

export default function App() {
  const [connectionStatus, setConnectionStatus] = useState('checking')

  useEffect(() => {
    checkHealth()
      .then(() => setConnectionStatus('ok'))
      .catch(() => setConnectionStatus('fail'))
  }, [])

  return (
    <div className="app-shell">
      <Header connectionStatus={connectionStatus} />
      <main className="app-main">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/box-office" element={<BoxOfficePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/favorites" element={<FavoritesPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}
