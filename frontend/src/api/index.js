import axios from 'axios'

const configuredBaseURL = import.meta.env.VITE_API_BASE_URL
const resolvedBaseURL = configuredBaseURL || (import.meta.env.DEV ? 'http://localhost:5001' : '')

if (!resolvedBaseURL) {
  console.error('VITE_API_BASE_URL is required for production builds.')
}

// Create an axios instance
const service = axios.create({
  baseURL: resolvedBaseURL,
  timeout: 300000, // Set a timeout of 5 minutes (the actual generation may take longer)
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
service.interceptors.request.use(
  config => {
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor (for error retry mechanism)
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // If the returned status code is not success, throw an error
    if (!res.success && res.success !== undefined) {
      console.error('API Error:', res.error || res.message || 'Unknown error')
      return Promise.reject(new Error(res.error || res.message || 'Error'))
    }
    
    return res
  },
  error => {
    console.error('Response error:', error)
    
    // Handle timeouts
    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      console.error('Request timeout')
    }
    
    // Handle network errors
    if (error.message === 'Network Error') {
      console.error('Network error - please check your connection')
    }
    
    return Promise.reject(error)
  }
)

// Request function with retries
export const requestWithRetry = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      if (i === maxRetries - 1) throw error
      
      console.warn(`Request failed, retrying (${i + 1}/${maxRetries})...`)
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
    }
  }
}

export default service
