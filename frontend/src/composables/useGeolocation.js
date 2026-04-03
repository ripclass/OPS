import { computed, onMounted, ref } from 'vue'
import { COUNTRY_MAP } from '../content/agentStories'

async function detectCountryCode() {
  if (typeof window === 'undefined') {
    return 'GLOBAL'
  }

  const params = new URLSearchParams(window.location.search)
  const override = params.get('country')
  if (override) {
    return override.trim().toUpperCase()
  }

  try {
    const geoResponse = await fetch('/api/geo', {
      headers: {
        Accept: 'application/json',
      },
    })
    if (geoResponse.ok) {
      const payload = await geoResponse.json()
      const code = String(payload?.country || '').trim().toUpperCase()
      if (code) {
        return code
      }
    }
  } catch {
    // fall through to public country API
  }

  try {
    const response = await fetch('https://ipapi.co/country/')
    const code = (await response.text()).trim().toUpperCase()
    if (code) {
      return code
    }
  } catch {
    // ignore
  }

  return 'GLOBAL'
}

export function useGeolocation() {
  const countryCode = ref('GLOBAL')
  const countryKey = computed(() => COUNTRY_MAP[countryCode.value] || 'global')
  const loading = ref(true)

  onMounted(async () => {
    countryCode.value = await detectCountryCode()
    loading.value = false
  })

  return {
    countryCode,
    countryKey,
    loading,
  }
}
