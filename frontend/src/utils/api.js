import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  config => {
    if (config.url && config.url.startsWith('http')) {
      console.error('[API] BLOCKED absolute URL:', config.url)
      return Promise.reject(new Error('Blocked direct backend request: ' + config.url))
    }
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
      console.log('[API Token] OK', config.method, config.url)
    } else {
      console.warn('[API Token] MISSING', config.method, config.url)
    }
    return config
  },
  error => Promise.reject(error)
)

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      console.error('[API] 401 on:', error.config?.url, '- redirecting to login')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api