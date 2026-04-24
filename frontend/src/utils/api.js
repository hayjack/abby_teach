import axios from 'axios'

/**
 * 将 JavaScript Date 对象转换为本地时区的 ISO 字符串
 * 避免前端 Date 对象被 JSON.stringify 转为 UTC 时间导致时差问题
 */
function convertDateToIsoStr(obj) {
  if (obj instanceof Date) {
    // 获取本地时区偏移（分钟）
    const offsetMinutes = -obj.getTimezoneOffset()
    const sign = offsetMinutes >= 0 ? '+' : '-'
    const absOffset = Math.abs(offsetMinutes)
    const hours = Math.floor(absOffset / 60)
    const minutes = absOffset % 60
    const tzStr = `${sign}${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
    
    const yyyy = obj.getFullYear()
    const mm = String(obj.getMonth() + 1).padStart(2, '0')
    const dd = String(obj.getDate()).padStart(2, '0')
    const hh = String(obj.getHours()).padStart(2, '0')
    const mi = String(obj.getMinutes()).padStart(2, '0')
    const ss = String(obj.getSeconds()).padStart(2, '0')
    const ms = String(obj.getMilliseconds()).padStart(3, '0')
    
    return `${yyyy}-${mm}-${dd}T${hh}:${mi}:${ss}.${ms}${tzStr}`
  }
  if (Array.isArray(obj)) {
    return obj.map(item => convertDateToIsoStr(item))
  }
  if (obj && typeof obj === 'object') {
    const result = {}
    for (const key of Object.keys(obj)) {
      result[key] = convertDateToIsoStr(obj[key])
    }
    return result
  }
  return obj
}

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  },
  transformRequest: [(data, headers) => {
    // 在序列化前将 Date 对象转为本地时区 ISO 字符串
    if (data && headers['Content-Type'] === 'application/json') {
      return JSON.stringify(convertDateToIsoStr(data))
    }
    return data
  }]
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
