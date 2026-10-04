import { useCallback, useEffect, useState } from 'react'
import { api } from './api'
import LoginPage from './pages/LoginPage'
import ProfilePage from './pages/ProfilePage'
import RegisterPage from './pages/RegisterPage'

const ROUTES = ['login', 'register', 'profile']

function routeFromHash() {
  const name = window.location.hash.replace('#/', '')
  return ROUTES.includes(name) ? name : 'profile'
}

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [route, setRoute] = useState(routeFromHash)

  const navigate = useCallback((name) => {
    window.location.hash = `#/${name}`
  }, [])

  useEffect(() => {
    const onHash = () => setRoute(routeFromHash())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  // Restore the session after a refresh: the cookie is still there, so /me works.
  useEffect(() => {
    let cancelled = false
    api
      .csrf()
      .then(() => api.me())
      .then((data) => { if (!cancelled) setUser(data) })
      .catch(() => { if (!cancelled) setUser(null) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  // Protected profile: guests go to login, signed-in users skip the auth pages.
  useEffect(() => {
    if (loading) return
    if (!user && route === 'profile') navigate('login')
    if (user && route !== 'profile') navigate('profile')
  }, [loading, user, route, navigate])

  async function handleLogout() {
    try {
      await api.logout()
    } finally {
      setUser(null)
      navigate('login')
    }
  }

  if (loading) {
    return <p className="loading" role="status">Зареждане…</p>
  }

  if (user && route === 'profile') {
    return <ProfilePage user={user} onUserChange={setUser} onLogout={handleLogout} />
  }
  if (!user && route === 'register') {
    return <RegisterPage onLogin={setUser} navigate={navigate} />
  }
  if (!user) {
    return <LoginPage onLogin={setUser} navigate={navigate} />
  }
  return <p className="loading" role="status">Пренасочване…</p>
}
