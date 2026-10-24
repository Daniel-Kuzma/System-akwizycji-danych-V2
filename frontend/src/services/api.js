import router from '../router'

export const BASE_URL = import.meta.env.VITE_API_URL

export async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem('token')

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const config = {
    ...options,
    headers,
  }

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, config)

    if (response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('role') 
      router.push('/login') 
      throw new Error('Sesja wygasła. Zaloguj się ponownie.')
    }

    return response
  } catch (error) {
    console.error('Błąd komunikacji z backendem:', error)
    throw error
  }
}