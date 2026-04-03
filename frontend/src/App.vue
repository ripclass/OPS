<template>
  <div class="app-shell">
    <button
      v-if="showSessionBar"
      class="session-bar"
      type="button"
      @click="handleSignOut"
    >
      <span class="session-bar__email">{{ authState.user?.email }}</span>
      <span class="session-bar__action">Sign out</span>
    </button>
    <router-view />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authState, signOut } from './store/auth'

const route = useRoute()
const router = useRouter()

const showSessionBar = computed(() => !['Login', 'Home'].includes(String(route.name)) && Boolean(authState.user))

const handleSignOut = async () => {
  await signOut()
  router.replace('/login')
}
</script>

<style>
#app {
  font-family: var(--ops-font-display);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--ops-ink);
}

.app-shell {
  min-height: 100vh;
}

.session-bar {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 1000;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border: 1px solid rgba(17, 24, 39, 0.12);
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 16px 40px rgba(17, 24, 39, 0.08);
  cursor: pointer;
}

.session-bar__email {
  font-size: 13px;
  color: #111827;
}

.session-bar__action {
  font-family: var(--ops-font-mono, monospace);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #f97316;
}
</style>
