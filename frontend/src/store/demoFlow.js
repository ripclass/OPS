import { computed, reactive } from 'vue'
import { getDemoPackByCountryCode, resolveDemoPackKey } from '../content/demoFlowPacks'
import { detectCountryCode } from '../composables/useGeolocation'

const STORAGE_KEY = 'murmur_demo_flow_v1'

const state = reactive({
  initialized: false,
  countryCode: 'BD',
  scenario: '',
  currentStep: 'demo',
  simulationStarted: false,
  simulationCompleted: false,
})

function normalizeCountryCode(value) {
  const normalized = String(value || '').trim().toUpperCase()
  return normalized || 'BD'
}

function getStorage() {
  if (typeof window === 'undefined') {
    return null
  }

  return window.sessionStorage
}

function persist() {
  const storage = getStorage()
  if (!storage) {
    return
  }

  storage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      countryCode: state.countryCode,
      scenario: state.scenario,
      currentStep: state.currentStep,
      simulationStarted: state.simulationStarted,
      simulationCompleted: state.simulationCompleted,
    })
  )
}

function hydrate() {
  const storage = getStorage()
  if (!storage) {
    return
  }

  const raw = storage.getItem(STORAGE_KEY)
  if (!raw) {
    return
  }

  try {
    const parsed = JSON.parse(raw)
    state.countryCode = normalizeCountryCode(parsed.countryCode)
    state.scenario = String(parsed.scenario || '').trim()
    state.currentStep = String(parsed.currentStep || 'demo')
    state.simulationStarted = Boolean(parsed.simulationStarted)
    state.simulationCompleted = Boolean(parsed.simulationCompleted)
  } catch {
    storage.removeItem(STORAGE_KEY)
  }
}

export async function initializeDemoFlow({ scenario, country } = {}) {
  if (!state.initialized) {
    hydrate()
  }

  let nextCountryCode = country
    ? normalizeCountryCode(country)
    : normalizeCountryCode(state.countryCode)

  if (!country && !state.initialized) {
    nextCountryCode = normalizeCountryCode(await detectCountryCode())
  }

  const pack = getDemoPackByCountryCode(nextCountryCode)
  const nextScenario = String(scenario || state.scenario || pack.intake.defaultScenario).trim()

  state.countryCode = nextCountryCode
  state.scenario = nextScenario || pack.intake.defaultScenario
  state.initialized = true
  persist()

  return pack
}

export function setDemoScenario(scenario) {
  state.scenario = String(scenario || '').trim()
  persist()
}

export function setDemoCountry(countryCode) {
  state.countryCode = normalizeCountryCode(countryCode)
  persist()
}

export function setDemoCurrentStep(step) {
  state.currentStep = String(step || 'demo')
  persist()
}

export function setSimulationState({ started, completed } = {}) {
  if (typeof started === 'boolean') {
    state.simulationStarted = started
  }
  if (typeof completed === 'boolean') {
    state.simulationCompleted = completed
  }
  persist()
}

export function resetSimulationState() {
  state.simulationStarted = false
  state.simulationCompleted = false
  persist()
}

export function buildDemoQuery(overrides = {}) {
  return {
    country: overrides.country || state.countryCode,
    scenario: typeof overrides.scenario === 'string' ? overrides.scenario : state.scenario,
  }
}

export const demoState = state
export const currentDemoPackKey = computed(() => resolveDemoPackKey(state.countryCode))
export const currentDemoPack = computed(() => getDemoPackByCountryCode(state.countryCode))
