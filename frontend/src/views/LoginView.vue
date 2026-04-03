<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-meta">OPS Access</div>
      <h1 class="login-title">Sign in to OPS</h1>
      <p class="login-copy">
        This environment is restricted to invited customers and internal operators.
      </p>

      <div v-if="!isSupabaseConfigured" class="login-alert login-alert--error">
        Supabase auth is not configured. Set <code>VITE_SUPABASE_URL</code> and
        <code>VITE_SUPABASE_PUBLISHABLE_KEY</code>.
      </div>

      <form class="login-form" @submit.prevent="handleSubmit">
        <label class="field">
          <span>Email</span>
          <input v-model.trim="form.email" type="email" autocomplete="email" required />
        </label>

        <label class="field">
          <span>Password</span>
          <input v-model="form.password" type="password" autocomplete="current-password" required />
        </label>

        <div v-if="errorMessage" class="login-alert login-alert--error">
          {{ errorMessage }}
        </div>

        <button class="login-button" type="submit" :disabled="submitting || !isSupabaseConfigured">
          <span v-if="submitting">Signing in...</span>
          <span v-else>Sign in</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authState, signInWithPassword } from '../store/auth'
import { isSupabaseConfigured } from '../lib/supabase'

const router = useRouter()
const route = useRoute()

const form = reactive({
  email: '',
  password: '',
})

const submitting = ref(false)
const localError = ref('')

const errorMessage = computed(() => localError.value || authState.error)

const handleSubmit = async () => {
  localError.value = ''
  submitting.value = true
  try {
    await signInWithPassword({
      email: form.email,
      password: form.password,
    })
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    router.replace(redirect)
  } catch (error) {
    localError.value = error?.message || 'Unable to sign in.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  padding: 32px 20px;
}

.login-card {
  width: 100%;
  max-width: 440px;
  border: 1px solid #e5e5e5;
  background: #ffffff;
  padding: 32px;
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.06);
}

.login-meta {
  font-family: var(--ops-font-mono, monospace);
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #f97316;
  margin-bottom: 12px;
}

.login-title {
  margin: 0 0 12px;
  font-size: 32px;
  line-height: 1.15;
  color: #111827;
}

.login-copy {
  margin: 0 0 24px;
  color: #4b5563;
  line-height: 1.6;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: #111827;
  font-size: 14px;
}

.field input {
  border: 1px solid #d1d5db;
  padding: 12px 14px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s ease;
}

.field input:focus {
  border-color: #111827;
}

.login-button {
  border: 1px solid #111827;
  background: #111827;
  color: #ffffff;
  padding: 14px 16px;
  font-weight: 600;
  cursor: pointer;
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-alert {
  border: 1px solid #e5e7eb;
  padding: 12px 14px;
  font-size: 13px;
  line-height: 1.5;
}

.login-alert--error {
  border-color: #fecaca;
  background: #fef2f2;
  color: #991b1b;
}

code {
  font-family: var(--ops-font-mono, monospace);
}
</style>
