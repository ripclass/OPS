<template>
  <div class="murmur-page">
    <header class="murmur-nav">
      <button class="murmur-brand" type="button" @click="scrollToTop">
        <span class="murmur-brand__word">Murmur</span>
      </button>

      <div class="murmur-actions">
        <template v-if="authState.user">
          <button class="nav-button nav-button--primary" type="button" @click="openConsole()">
            Open console
          </button>
          <button class="nav-button" type="button" @click="handleSignOut">
            Sign out
          </button>
        </template>
        <template v-else>
          <button class="nav-button nav-button--primary" type="button" @click="openConsole()">
            Try
          </button>
          <button class="nav-button" type="button" @click="openAuth('signup')">
            Sign up
          </button>
          <button class="nav-button" type="button" @click="openAuth('signin')">
            Sign in
          </button>
        </template>
      </div>
    </header>

    <main class="murmur-main">
      <section class="opening-shell">
        <div v-if="loading" class="opening-status">Finding where you arrived from.</div>
        <AgentStory
          v-else
          :story="currentStory"
          :global-mode="isGlobal"
          @complete="handleStoryComplete"
        />

        <div v-if="isGlobal" class="carousel-shell">
          <CarouselDots
            :total="globalStories.length"
            :active-index="activeGlobalIndex"
            @select="handleDotSelect"
          />
        </div>

        <Transition name="brand-fade">
          <div v-if="brandVisible" id="about" class="title-reveal">
            <div class="title-reveal__wordmark">MURMUR</div>
            <p class="title-reveal__subtitle">South Asia behavioral intelligence</p>
          </div>
        </Transition>
      </section>

      <section class="content-section">
        <AgentFeed :posts="AGENT_FEED_POSTS" />
      </section>

      <section id="research" class="content-section">
        <WhatItKnows :items="WHAT_IT_KNOWS" />
      </section>

      <section class="content-section">
        <WhatItDoes :paragraphs="WHAT_IT_DOES" />
      </section>

      <section class="content-section">
        <WhoItsFor
          :intro="WHO_ITS_FOR_INTRO"
          :lines="WHO_ITS_FOR_LINES"
          :outro="WHO_ITS_FOR_OUTRO"
        />
      </section>

      <section class="content-section">
        <ScenarioInput @submit="handleScenarioSubmit" @request-access="openAuth('signup')" />
      </section>

      <section id="privacy" class="content-section content-section--privacy">
        <p class="privacy-note">
          No tracking. No surveillance pixels. Scenario submissions are reviewed manually.
        </p>
      </section>

      <section class="content-section">
        <LegitimacyFooter :lines="LEGITIMACY_LINES" />
      </section>
    </main>

    <transition name="modal-fade">
      <div v-if="authModalOpen" class="auth-modal" @click.self="closeAuth">
        <div class="auth-modal__dialog">
          <button class="auth-modal__close" type="button" @click="closeAuth">x</button>
          <LandingAccessPanel
            :initial-mode="accessMode"
            :redirect-path="redirectPath"
            @authenticated="handleAuthenticated"
          />
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import LandingAccessPanel from '../components/LandingAccessPanel.vue'
import AgentFeed from '../components/landing/AgentFeed.vue'
import AgentStory from '../components/landing/AgentStory.vue'
import CarouselDots from '../components/landing/CarouselDots.vue'
import LegitimacyFooter from '../components/landing/LegitimacyFooter.vue'
import ScenarioInput from '../components/landing/ScenarioInput.vue'
import WhatItDoes from '../components/landing/WhatItDoes.vue'
import WhatItKnows from '../components/landing/WhatItKnows.vue'
import WhoItsFor from '../components/landing/WhoItsFor.vue'
import {
  AGENT_FEED_POSTS,
  AGENT_STORIES,
  GLOBAL_ROTATION_ORDER,
  LEGITIMACY_LINES,
  WHAT_IT_DOES,
  WHAT_IT_KNOWS,
  WHO_ITS_FOR_INTRO,
  WHO_ITS_FOR_LINES,
  WHO_ITS_FOR_OUTRO,
} from '../content/agentStories'
import { useGeolocation } from '../composables/useGeolocation'
import { authState, signOut } from '../store/auth'

const router = useRouter()
const route = useRoute()
const { countryKey, loading } = useGeolocation()

const activeGlobalIndex = ref(0)
const brandVisible = ref(false)
let brandTimer = null
let rotationTimer = null

const globalStories = GLOBAL_ROTATION_ORDER.map(key => AGENT_STORIES[key])
const isGlobal = computed(() => countryKey.value === 'global')

const currentStory = computed(() => {
  if (isGlobal.value) {
    return globalStories[activeGlobalIndex.value]
  }
  return AGENT_STORIES[countryKey.value] || AGENT_STORIES.bangladesh
})

const authModalOpen = computed(() => Boolean(route.query.auth))
const accessMode = computed(() => (route.query.auth === 'signup' ? 'signup' : 'signin'))
const redirectPath = computed(() => (
  typeof route.query.redirect === 'string' && route.query.redirect
    ? route.query.redirect
    : '/console'
))

const clearBrandTimer = () => {
  if (brandTimer) {
    window.clearTimeout(brandTimer)
    brandTimer = null
  }
}

const clearRotationTimer = () => {
  if (rotationTimer) {
    window.clearInterval(rotationTimer)
    rotationTimer = null
  }
}

const resetCarousel = () => {
  clearRotationTimer()
  if (!isGlobal.value || typeof window === 'undefined') {
    return
  }
  rotationTimer = window.setInterval(() => {
    activeGlobalIndex.value = (activeGlobalIndex.value + 1) % globalStories.length
  }, 20000)
}

watch(
  countryKey,
  () => {
    activeGlobalIndex.value = 0
    brandVisible.value = false
    clearBrandTimer()
    resetCarousel()
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  clearBrandTimer()
  clearRotationTimer()
})

const mergeQuery = (patch = {}) => {
  const next = { ...route.query, ...patch }
  Object.keys(next).forEach(key => {
    if (next[key] === undefined || next[key] === null || next[key] === '') {
      delete next[key]
    }
  })
  return next
}

const buildConsolePath = (scenario = '') => {
  if (!scenario) {
    return '/console'
  }
  return `/console?scenario=${encodeURIComponent(scenario)}`
}

const openAuth = (mode, redirect = redirectPath.value) => {
  router.replace({
    name: 'Home',
    query: mergeQuery({
      auth: mode,
      redirect,
    }),
  })
}

const closeAuth = () => {
  router.replace({
    name: 'Home',
    query: mergeQuery({
      auth: undefined,
      redirect: undefined,
    }),
  })
}

const openConsole = (scenario = '') => {
  const redirect = buildConsolePath(scenario)
  if (authState.user) {
    router.push(redirect)
    return
  }
  openAuth('signin', redirect)
}

const handleScenarioSubmit = (scenario) => {
  if (authState.user) {
    router.push(buildConsolePath(scenario))
    return
  }
  openAuth('signup', buildConsolePath(scenario))
}

const handleAuthenticated = () => {
  const redirect = redirectPath.value
  closeAuth()
  if (redirect && redirect !== '/') {
    router.push(redirect)
  }
}

const handleStoryComplete = () => {
  if (brandVisible.value || typeof window === 'undefined') {
    brandVisible.value = true
    return
  }

  clearBrandTimer()
  brandTimer = window.setTimeout(() => {
    brandVisible.value = true
  }, 1000)
}

const handleDotSelect = (index) => {
  activeGlobalIndex.value = index
  resetCarousel()
}

const handleSignOut = async () => {
  await signOut()
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=DM+Serif+Display:ital@0;1&family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+Arabic:wght@400;500&family=Noto+Sans+Bengali:wght@400;500&family=Noto+Sans+Devanagari:wght@400;500&family=Noto+Sans+Sinhala:wght@400;500&family=Noto+Sans+Tamil:wght@400;500&display=swap');

.murmur-page {
  --murmur-bg-primary: #08080c;
  --murmur-bg-card: #0f0f16;
  --murmur-bg-input: #12121a;
  --murmur-text-primary: #d4d4d8;
  --murmur-text-heading: #e8e8ec;
  --murmur-text-muted: #52525b;
  --murmur-text-agent-name: #a1a1aa;
  --murmur-accent: #c0392b;
  --murmur-accent-subtle: rgba(192, 57, 43, 0.13);
  --murmur-border: #1a1a24;
  --murmur-link: #8b9dc3;
  --murmur-font-serif: 'DM Serif Display', 'Source Serif 4', serif;
  --murmur-font-body: 'DM Sans', 'Source Sans 3', sans-serif;
  --murmur-font-mono: 'IBM Plex Mono', 'JetBrains Mono', monospace;
  --murmur-font-script-bengali: 'Noto Sans Bengali', sans-serif;
  --murmur-font-script-devanagari: 'Noto Sans Devanagari', sans-serif;
  --murmur-font-script-arabic: 'Noto Sans Arabic', sans-serif;
  --murmur-font-script-tamil: 'Noto Sans Tamil', sans-serif;
  --murmur-font-script-sinhala: 'Noto Sans Sinhala', sans-serif;
  min-height: 100vh;
  background: var(--murmur-bg-primary);
  color: var(--murmur-text-primary);
  font-family: var(--murmur-font-body);
}

.murmur-nav {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 32px;
  background: rgba(8, 8, 12, 0.92);
  backdrop-filter: blur(18px);
}

.murmur-brand {
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
  padding: 0;
}

.murmur-brand__word {
  color: var(--murmur-text-heading);
  font-family: var(--murmur-font-serif);
  font-size: 24px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.murmur-actions {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.nav-button {
  border: 1px solid var(--murmur-border);
  background: transparent;
  color: var(--murmur-text-heading);
  padding: 11px 16px;
  cursor: pointer;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}

.nav-button:hover {
  border-color: #303041;
  background: rgba(255, 255, 255, 0.02);
}

.nav-button--primary {
  border-color: rgba(232, 232, 236, 0.2);
}

.murmur-main {
  max-width: 680px;
  margin: 0 auto;
  padding: 88px 24px 40px;
}

.opening-shell {
  min-height: 74vh;
}

.opening-status {
  color: var(--murmur-text-muted);
  font-family: var(--murmur-font-mono);
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.carousel-shell {
  display: flex;
  justify-content: center;
  margin-top: 34px;
}

.title-reveal {
  margin-top: 72px;
}

.title-reveal__wordmark {
  color: var(--murmur-accent);
  font-family: var(--murmur-font-serif);
  font-size: clamp(52px, 10vw, 84px);
  line-height: 0.95;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.title-reveal__subtitle {
  margin: 14px 0 0;
  color: var(--murmur-text-heading);
  font-size: 20px;
  line-height: 1.7;
}

.content-section {
  padding-top: 120px;
}

.content-section--privacy {
  padding-top: 88px;
}

.privacy-note {
  margin: 0;
  color: var(--murmur-text-muted);
  font-size: 14px;
  line-height: 1.8;
}

.auth-modal {
  position: fixed;
  inset: 0;
  z-index: 40;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(8, 8, 12, 0.84);
  backdrop-filter: blur(18px);
}

.auth-modal__dialog {
  position: relative;
  width: min(100%, 420px);
}

.auth-modal__close {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
  border: none;
  background: transparent;
  color: var(--murmur-text-muted);
  font-size: 28px;
  cursor: pointer;
}

.brand-fade-enter-active,
.brand-fade-leave-active,
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.6s ease;
}

.brand-fade-enter-from,
.brand-fade-leave-to,
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .murmur-nav {
    padding: 18px 20px;
  }

  .murmur-main {
    padding: 64px 20px 32px;
  }

  .content-section {
    padding-top: 80px;
  }
}
</style>
