<template>
  <aside class="access-card">
    <div class="access-meta">OPS Access</div>
    <h2 class="access-title">Sign in or create an account</h2>
    <p class="access-copy">
      The landing stays public. Scenario runs and reports stay behind authentication.
    </p>

    <div v-if="authState.user" class="signed-in-state">
      <div class="signed-in-label">Signed in</div>
      <div class="signed-in-email">{{ authState.user.email }}</div>
      <div class="signed-in-actions">
        <button class="access-button access-button--primary" type="button" @click="handleContinue">
          Continue into OPS
        </button>
        <button class="access-button access-button--ghost" type="button" @click="handleSignOut">
          Sign out
        </button>
      </div>
    </div>

    <div v-else class="access-form-shell">
      <div class="access-tabs">
        <button
          class="access-tab"
          :class="{ 'access-tab--active': mode === 'signin' }"
          type="button"
          @click="mode = 'signin'"
        >
          Sign in
        </button>
        <button
          class="access-tab"
          :class="{ 'access-tab--active': mode === 'signup' }"
          type="button"
          @click="mode = 'signup'"
        >
          Sign up
        </button>
      </div>

      <form class="access-form" @submit.prevent="handleSubmit">
        <label class="access-field">
          <span>Email</span>
          <input v-model.trim="form.email" type="email" autocomplete="email" required />
        </label>

        <label class="access-field">
          <span>Password</span>
          <input
            v-model="form.password"
            type="password"
            autocomplete="current-password"
            minlength="8"
            required
          />
        </label>

        <div v-if="message" class="access-alert access-alert--success">
          {{ message }}
        </div>

        <div v-if="errorMessage" class="access-alert access-alert--error">
          {{ errorMessage }}
        </div>

        <button
          class="access-button access-button--primary"
          type="submit"
          :disabled="submitting || !isSupabaseConfigured"
        >
          <span v-if="submitting">
            {{ mode === 'signin' ? 'Signing in...' : 'Creating account...' }}
          </span>
          <span v-else>
            {{ mode === 'signin' ? 'Sign in' : 'Create account' }}
          </span>
        </button>
      </form>

      <div v-if="!isSupabaseConfigured" class="access-note access-note--error">
        Supabase auth is not configured for the frontend.
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { authState, signInWithPassword, signOut, signUpWithPassword } from '../store/auth'
import { isSupabaseConfigured } from '../lib/supabase'

const props = defineProps({
  initialMode: {
    type: String,
    default: 'signin',
  },
  redirectPath: {
    type: String,
    default: '/',
  },
})

const emit = defineEmits(['authenticated'])

const router = useRouter()
const mode = ref(props.initialMode === 'signup' ? 'signup' : 'signin')
const submitting = ref(false)
const localError = ref('')
const message = ref('')

const form = reactive({
  email: '',
  password: '',
})

watch(
  () => props.initialMode,
  value => {
    mode.value = value === 'signup' ? 'signup' : 'signin'
  }
)

const errorMessage = computed(() => localError.value || authState.error)

const clearMessages = () => {
  localError.value = ''
  message.value = ''
}

const handleContinue = () => {
  emit('authenticated')
  if (props.redirectPath && props.redirectPath !== '/') {
    router.push(props.redirectPath)
  }
}

const handleSignOut = async () => {
  clearMessages()
  await signOut()
}

const handleSubmit = async () => {
  clearMessages()
  submitting.value = true
  try {
    if (mode.value === 'signin') {
      await signInWithPassword({
        email: form.email,
        password: form.password,
      })
      emit('authenticated')
      if (props.redirectPath && props.redirectPath !== '/') {
        await router.push(props.redirectPath)
      } else {
        message.value = 'Signed in. You can continue from the landing page.'
      }
      return
    }

    const result = await signUpWithPassword({
      email: form.email,
      password: form.password,
    })

    if (result?.session) {
      emit('authenticated')
      message.value = 'Account created. You can continue into OPS.'
      return
    }

    message.value = 'Account created. Check your email if confirmation is enabled.'
  } catch (error) {
    localError.value = error?.message || 'Unable to continue.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.access-card {
  width: min(100%, 390px);
  border: 1px solid rgba(17, 24, 39, 0.1);
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 24px 70px rgba(17, 24, 39, 0.08);
  padding: 28px;
  z-index: 1;
}

.access-meta {
  font-family: var(--ops-font-mono, monospace);
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #c94b22;
  margin-bottom: 12px;
}

.access-title {
  margin: 0 0 12px;
  font-size: 30px;
  line-height: 1.15;
  color: #111827;
}

.access-copy {
  margin: 0 0 20px;
  color: #4b5563;
  line-height: 1.6;
}

.access-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 18px;
}

.access-tab {
  flex: 1;
  border: 1px solid rgba(17, 24, 39, 0.1);
  background: #ffffff;
  color: #6b7280;
  padding: 10px 12px;
  cursor: pointer;
}

.access-tab--active {
  border-color: #111827;
  color: #111827;
}

.access-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.access-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: #111827;
  font-size: 14px;
}

.access-field input {
  border: 1px solid #d1d5db;
  padding: 12px 14px;
  font-size: 14px;
  outline: none;
}

.access-field input:focus {
  border-color: #111827;
}

.access-button {
  border: 1px solid #111827;
  padding: 13px 14px;
  font-weight: 600;
  cursor: pointer;
}

.access-button--primary {
  background: #111827;
  color: #ffffff;
}

.access-button--ghost {
  background: #ffffff;
  color: #111827;
}

.access-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.access-alert {
  border: 1px solid #e5e7eb;
  padding: 12px 14px;
  font-size: 13px;
  line-height: 1.5;
}

.access-alert--error {
  border-color: #fecaca;
  background: #fef2f2;
  color: #991b1b;
}

.access-alert--success {
  border-color: #bfdbfe;
  background: #eff6ff;
  color: #1d4ed8;
}

.access-note {
  margin-top: 12px;
  font-size: 13px;
}

.access-note--error {
  color: #991b1b;
}

.signed-in-state {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.signed-in-label {
  font-family: var(--ops-font-mono, monospace);
  font-size: 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #6b7280;
}

.signed-in-email {
  font-size: 16px;
  color: #111827;
  word-break: break-word;
}

.signed-in-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

@media (max-width: 640px) {
  .access-card {
    width: 100%;
    padding: 22px;
  }

  .access-title {
    font-size: 24px;
  }
}
</style>
