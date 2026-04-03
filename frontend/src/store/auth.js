import { computed, reactive } from 'vue'
import { supabase, isSupabaseConfigured } from '../lib/supabase'

const state = reactive({
  initialized: false,
  loading: false,
  session: null,
  user: null,
  error: '',
})

let initPromise = null
let authListenerBound = false

function applySession(session) {
  state.session = session || null
  state.user = session?.user || null
}

function bindAuthListener() {
  if (!supabase || authListenerBound) {
    return
  }
  supabase.auth.onAuthStateChange((_event, session) => {
    applySession(session)
    state.initialized = true
  })
  authListenerBound = true
}

export async function initAuth() {
  if (!isSupabaseConfigured) {
    state.initialized = true
    state.error = 'Supabase auth is not configured.'
    return
  }

  if (!initPromise) {
    bindAuthListener()
    initPromise = supabase.auth.getSession()
      .then(({ data, error }) => {
        if (error) {
          state.error = error.message
          applySession(null)
          return
        }
        applySession(data.session)
      })
      .finally(() => {
        state.initialized = true
      })
  }

  await initPromise
}

export async function signInWithPassword({ email, password }) {
  if (!supabase) {
    throw new Error('Supabase auth is not configured.')
  }

  state.loading = true
  state.error = ''
  try {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) {
      throw error
    }
    applySession(data.session)
    return data
  } finally {
    state.loading = false
  }
}

export async function signUpWithPassword({ email, password }) {
  if (!supabase) {
    throw new Error('Supabase auth is not configured.')
  }

  state.loading = true
  state.error = ''
  try {
    const { data, error } = await supabase.auth.signUp({ email, password })
    if (error) {
      throw error
    }
    applySession(data.session)
    return data
  } finally {
    state.loading = false
  }
}

export async function signOut() {
  if (!supabase) {
    applySession(null)
    return
  }

  await supabase.auth.signOut()
  applySession(null)
}

export async function getAccessToken() {
  await initAuth()
  return state.session?.access_token || null
}

export const authState = state
export const isAuthenticated = computed(() => Boolean(state.user))
