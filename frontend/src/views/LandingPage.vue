<template>
  <div class="murmur-page">
    <header class="murmur-nav">
      <button class="murmur-brand" type="button" @click="scrollToTop">
        <span class="murmur-brand__word">Murmur</span>
      </button>

      <nav class="murmur-nav__links" aria-label="Primary">
        <a href="#console">Get Started</a>
        <a href="#videos">Videos</a>
        <a href="#introduction">Introduction</a>
        <a href="#about-us">About US</a>
      </nav>

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
          <button class="nav-button" type="button" @click="openAuth('signin')">
            Login
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

      </section>

      <section id="introduction" class="content-section content-section--intro">
        <MurmurIntro
          kicker="South Asia-grounded scenario simulation"
          title="Rehearse how populations, institutions, and narratives react before the event goes live."
          summary="Murmur turns scenario briefs, policy drafts, news material, and field evidence into a simulated public sphere across Bangladesh, India, Pakistan, Nepal, and Sri Lanka."
          detail="Model likely reaction pathways before the street, the feed, or the market moves."
        />
      </section>

      <section class="content-section content-section--wide">
        <WhatItDoes :paragraphs="WHAT_IT_DOES" />
      </section>

      <section class="content-section content-section--wide content-section--audience">
        <WhoItsFor
          :intro="WHO_ITS_FOR_INTRO"
          :lines="WHO_ITS_FOR_LINES"
          :outro="WHO_ITS_FOR_OUTRO"
        />
      </section>

      <section id="research" class="content-section content-section--wide content-section--knowledge">
        <WhatItKnows :items="WHAT_IT_KNOWS" />
      </section>

      <section class="content-section content-section--wide content-section--scenario">
        <ScenarioInput
          :is-authenticated="Boolean(authState.user)"
          @submit="handleScenarioSubmit"
        />
      </section>

      <section id="privacy" class="content-section content-section--wide content-section--privacy">
        <p class="privacy-note">
          No tracking. No surveillance pixels. Scenario submissions are reviewed manually.
        </p>
      </section>

      <section class="content-section content-section--wide content-section--footer">
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
import AgentStory from '../components/landing/AgentStory.vue'
import CarouselDots from '../components/landing/CarouselDots.vue'
import LegitimacyFooter from '../components/landing/LegitimacyFooter.vue'
import MurmurIntro from '../components/landing/MurmurIntro.vue'
import ScenarioInput from '../components/landing/ScenarioInput.vue'
import WhatItDoes from '../components/landing/WhatItDoes.vue'
import WhatItKnows from '../components/landing/WhatItKnows.vue'
import WhoItsFor from '../components/landing/WhoItsFor.vue'
import {
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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=DM+Serif+Display:ital@0;1&family=IBM+Plex+Mono:wght@400;500&family=Lato:wght@300;400;900&family=Noto+Sans+Arabic:wght@400;500&family=Noto+Sans+Bengali:wght@400;500&family=Noto+Sans+Devanagari:wght@400;500&family=Noto+Sans+Sinhala:wght@400;500&family=Noto+Sans+Tamil:wght@400;500&family=Outfit:wght@700;800&family=Permanent+Marker&family=Special+Elite&display=swap');

.murmur-page {
  --murmur-bg-primary: #ffffff;
  --murmur-bg-card: #f6f5f2;
  --murmur-bg-input: #fcfcfb;
  --murmur-text-primary: #2a241d;
  --murmur-text-heading: #100d0a;
  --murmur-text-muted: #85796e;
  --murmur-text-agent-name: #756a60;
  --murmur-accent: #8d392c;
  --murmur-accent-subtle: rgba(141, 57, 44, 0.1);
  --murmur-border: #ddd8d0;
  --murmur-link: #5a7692;
  --murmur-font-serif: 'DM Serif Display', 'Source Serif 4', serif;
  --murmur-font-body: 'DM Sans', 'Source Sans 3', sans-serif;
  --murmur-font-mono: 'IBM Plex Mono', 'JetBrains Mono', monospace;
  --murmur-font-hand: 'Permanent Marker', cursive;
  --murmur-font-display: 'Outfit', 'DM Sans', sans-serif;
  --murmur-font-ui: 'Lato', sans-serif;
  --murmur-font-type: 'Special Elite', 'IBM Plex Mono', monospace;
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
  position: relative;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  max-width: 978px;
  margin: 0 auto;
  padding: 12px 10px 0;
}

.murmur-brand {
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
  padding: 0;
}

.murmur-brand__word {
  color: #050505;
  font-family: var(--murmur-font-display);
  font-size: 24px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.murmur-nav__links {
  position: absolute;
  left: 398px;
  top: 20px;
  display: flex;
  gap: 13px;
}

.murmur-nav__links a {
  color: #000;
  font-family: var(--murmur-font-ui);
  font-size: 10px;
  font-weight: 300;
  line-height: 1;
  text-decoration: none;
}

.murmur-nav__links a:first-child {
  font-weight: 900;
}

.murmur-actions {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.nav-button {
  min-width: 52px;
  border: 0;
  border-radius: 6px;
  background: #f6f6f6;
  color: #000;
  font-family: var(--murmur-font-ui);
  font-size: 10px;
  font-weight: 900;
  padding: 9px 14px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.nav-button:hover {
  background: #ececec;
}

.nav-button--primary {
  background: #111;
  color: #fff;
}

.murmur-main {
  max-width: 978px;
  margin: 0 auto;
  padding: 36px 0 40px;
}

.opening-shell {
  min-height: 1020px;
  padding-top: 0;
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
  margin-top: 24px;
}

.content-section {
  max-width: 680px;
  margin: 0 auto;
  padding-top: 96px;
}

.content-section--intro {
  max-width: 978px;
  padding-top: 58px;
}

.content-section--wide {
  max-width: 978px;
}

.content-section--audience {
  padding-top: 168px;
}

.content-section--knowledge {
  padding-top: 152px;
}

.content-section--scenario {
  padding-top: 152px;
}

.content-section--privacy {
  padding-top: 42px;
}

.content-section--footer {
  padding-top: 72px;
}

.privacy-note {
  margin: 0;
  color: #050505;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 16px;
  line-height: 1.3;
}

.auth-modal {
  position: fixed;
  inset: 0;
  z-index: 40;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(21, 17, 12, 0.28);
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
    padding: 16px 20px 0;
  }

  .murmur-nav__links {
    display: none;
  }

  .murmur-main {
    padding: 28px 20px 32px;
  }

  .opening-shell {
    min-height: 0;
  }

  .content-section {
    padding-top: 80px;
  }
}
</style>
