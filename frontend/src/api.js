// Thin wrapper around fetch for the Django session + CSRF API.

function getCookie(name) {
  const match = document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${name}=`))
  return match ? decodeURIComponent(match.split('=')[1]) : null
}

export class ApiError extends Error {
  constructor(status, errors) {
    super('Request failed')
    this.status = status
    this.errors = errors || {}
  }
}

async function ensureCsrf() {
  if (!getCookie('csrftoken')) {
    await fetch('/api/auth/csrf/', { credentials: 'same-origin' })
  }
  return getCookie('csrftoken')
}

async function request(method, url, body) {
  const headers = { Accept: 'application/json' }
  const unsafe = !['GET', 'HEAD', 'OPTIONS'].includes(method)

  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (unsafe) headers['X-CSRFToken'] = await ensureCsrf()

  const response = await fetch(url, {
    method,
    headers,
    credentials: 'same-origin',
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (response.status === 204) return null

  let data = null
  try {
    data = await response.json()
  } catch {
    data = null
  }

  if (!response.ok) {
    const errors = data?.errors || {
      detail: [`Server error (${response.status}). Try again.`],
    }
    throw new ApiError(response.status, errors)
  }
  return data
}

export const api = {
  csrf: () => fetch('/api/auth/csrf/', { credentials: 'same-origin' }),
  register: (payload) => request('POST', '/api/auth/register/', payload),
  login: (payload) => request('POST', '/api/auth/login/', payload),
  logout: () => request('POST', '/api/auth/logout/'),
  me: () => request('GET', '/api/auth/me/'),
  updateMe: (payload) => request('PATCH', '/api/auth/me/', payload),
}
