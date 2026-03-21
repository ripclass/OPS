/**
 * Temporarily store the files to be uploaded and related requirements.
 * Used for immediate redirection to the Process page upon clicking to start the engine from the home page, where API calls will be made.
 */
import { reactive } from 'vue'
import { createDefaultOpsConfig, normalizeOpsConfig } from '../utils/opsRunDesign'

const STORAGE_KEY = 'ops-pending-upload-v2'

const loadPersistedState = () => {
  if (typeof window === 'undefined') {
    return {
      simulationRequirement: '',
      sourceUrls: [],
      isPending: false,
      opsConfig: createDefaultOpsConfig(),
    }
  }

  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY)
    if (!raw) {
      return {
        simulationRequirement: '',
        sourceUrls: [],
        isPending: false,
        opsConfig: createDefaultOpsConfig(),
      }
    }

    const parsed = JSON.parse(raw)
    return {
      simulationRequirement: parsed.simulationRequirement || '',
      sourceUrls: Array.isArray(parsed.sourceUrls) ? parsed.sourceUrls.map((value) => String(value || '').trim()).filter(Boolean) : [],
      isPending: !!parsed.isPending,
      opsConfig: normalizeOpsConfig(parsed.opsConfig),
    }
  } catch (error) {
    console.warn('Failed to load pending OPS state:', error)
    return {
      simulationRequirement: '',
      sourceUrls: [],
      isPending: false,
      opsConfig: createDefaultOpsConfig(),
    }
  }
}

const persistState = (state) => {
  if (typeof window === 'undefined') return

  try {
    window.sessionStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        simulationRequirement: state.simulationRequirement,
        sourceUrls: state.sourceUrls,
        isPending: state.isPending,
        opsConfig: state.opsConfig,
      })
    )
  } catch (error) {
    console.warn('Failed to persist pending OPS state:', error)
  }
}

const persisted = loadPersistedState()

const state = reactive({
  files: [],
  simulationRequirement: persisted.simulationRequirement,
  sourceUrls: persisted.sourceUrls,
  isPending: persisted.isPending,
  opsConfig: persisted.opsConfig,
})

export function setPendingUpload(files, requirement, opsConfig = createDefaultOpsConfig(), sourceUrls = []) {
  state.files = files
  state.simulationRequirement = requirement
  state.sourceUrls = Array.isArray(sourceUrls) ? sourceUrls.map((value) => String(value || '').trim()).filter(Boolean) : []
  state.isPending = true
  state.opsConfig = normalizeOpsConfig(opsConfig)
  persistState(state)
}

export function setPendingOpsConfig(config) {
  state.opsConfig = normalizeOpsConfig(config)
  persistState(state)
}

export function updatePendingOpsConfig(patch) {
  state.opsConfig = normalizeOpsConfig({
    ...state.opsConfig,
    ...(patch || {}),
  })
  persistState(state)
}

export function getPendingUpload() {
  return {
    files: state.files,
    simulationRequirement: state.simulationRequirement,
    sourceUrls: [...state.sourceUrls],
    isPending: state.isPending,
    opsConfig: normalizeOpsConfig(state.opsConfig),
  }
}

export function clearPendingUpload(options = {}) {
  const { preserveOpsConfig = false } = options
  state.files = []
  state.simulationRequirement = ''
  state.sourceUrls = []
  state.isPending = false
  state.opsConfig = preserveOpsConfig ? normalizeOpsConfig(state.opsConfig) : createDefaultOpsConfig()
  persistState(state)
}

export default state
