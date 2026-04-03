<template>
  <div class="landing-page">
    <header class="landing-nav">
      <div class="landing-brand">
        <img class="landing-brand__logo" :src="heroImageUrl" alt="OPS" />
        <span class="landing-brand__text">OPS</span>
      </div>

      <nav class="landing-links">
        <a href="#how-it-works">How It Works</a>
        <a href="#use-cases">Use Cases</a>
        <a href="#readiness">Readiness</a>
      </nav>

      <div class="landing-actions">
        <button
          v-if="authState.user"
          class="nav-button nav-button--primary"
          type="button"
          @click="openConsole"
        >
          Open Console
        </button>
        <template v-else>
          <button class="nav-button nav-button--primary" type="button" @click="openConsole">
            Try
          </button>
          <button class="nav-button" type="button" @click="openAuth('signup')">
            Sign up
          </button>
          <button class="nav-button" type="button" @click="openAuth('signin')">
            Sign in
          </button>
        </template>

        <button
          v-if="authState.user"
          class="nav-button"
          type="button"
          @click="handleSignOut"
        >
          Sign out
        </button>

        <a
          href="https://github.com/ripclass/OPS"
          target="_blank"
          rel="noreferrer"
          class="nav-button nav-button--ghost"
        >
          GitHub
        </a>
      </div>
    </header>

    <main class="landing-main">
      <section class="hero">
        <div class="hero-copy">
          <div class="hero-eyebrow">South Asia-grounded scenario simulation</div>
          <h1 class="hero-title">
            Rehearse how populations, institutions, and narratives react before the event goes live.
          </h1>
          <p class="hero-description">
            OPS turns scenario briefs, policy drafts, news material, and field evidence into a
            simulated public sphere across Bangladesh, India, Pakistan, Nepal, and Sri Lanka.
            Model likely reaction pathways before the street, the feed, or the market moves.
          </p>

          <div class="hero-buttons">
            <button class="hero-button hero-button--primary" type="button" @click="openConsole">
              Try Live Console
            </button>
            <button class="hero-button" type="button" @click="openAuth('signup')">
              Get Access
            </button>
          </div>

          <div class="hero-trust">
            <div class="trust-item">
              <span class="trust-item__value">5-step</span>
              <span class="trust-item__label">world simulation workflow</span>
            </div>
            <div class="trust-item">
              <span class="trust-item__value">South Asia</span>
              <span class="trust-item__label">country and segment priors</span>
            </div>
            <div class="trust-item">
              <span class="trust-item__value">Report + Live Q&A</span>
              <span class="trust-item__label">post-run interrogation</span>
            </div>
          </div>
        </div>

        <div class="hero-visual">
          <div class="hero-visual__frame">
            <div class="hero-visual__badge">OPS Console</div>
            <div class="hero-visual__terminal">
              <div class="terminal-line">
                <span class="terminal-label">Scenario</span>
                <span class="terminal-text">Rice prices increase 40% before Eid in Dhaka.</span>
              </div>
              <div class="terminal-line">
                <span class="terminal-label">Population</span>
                <span class="terminal-text">Urban working, middle class, migration-linked families</span>
              </div>
              <div class="terminal-line">
                <span class="terminal-label">Primary Shift</span>
                <span class="terminal-text">Economic anxiety -> anger -> rumor amplification</span>
              </div>
              <div class="terminal-divider"></div>
              <div class="terminal-grid">
                <div class="terminal-card">
                  <div class="terminal-card__title">Graph</div>
                  <div class="terminal-card__copy">Actors, institutions, grievances, locations</div>
                </div>
                <div class="terminal-card">
                  <div class="terminal-card__title">Population</div>
                  <div class="terminal-card__copy">Country priors, segment weighting, institutional seeds</div>
                </div>
                <div class="terminal-card">
                  <div class="terminal-card__title">Simulation</div>
                  <div class="terminal-card__copy">Multi-round cascades, memory, amplification</div>
                </div>
                <div class="terminal-card">
                  <div class="terminal-card__title">Report</div>
                  <div class="terminal-card__copy">Evidence-backed forecast and live interview layer</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="how-it-works" class="section">
        <div class="section-heading">
          <div class="section-eyebrow">Predict in 5 Steps</div>
          <h2>Built for structured simulation, not generic chatbot output.</h2>
        </div>

        <div class="steps-grid">
          <article class="step-card" v-for="step in steps" :key="step.number">
            <div class="step-card__number">{{ step.number }}</div>
            <h3>{{ step.title }}</h3>
            <p>{{ step.description }}</p>
          </article>
        </div>
      </section>

      <section id="use-cases" class="section">
        <div class="section-heading">
          <div class="section-eyebrow">Built for high-context work</div>
          <h2>OPS is strongest where decisions meet public uncertainty.</h2>
        </div>

        <div class="use-case-grid">
          <article class="use-case-card" v-for="useCase in useCases" :key="useCase.title">
            <div class="use-case-card__label">{{ useCase.label }}</div>
            <h3>{{ useCase.title }}</h3>
            <p>{{ useCase.description }}</p>
          </article>
        </div>
      </section>

      <section id="readiness" class="section section--narrow">
        <div class="readiness-card">
          <div class="section-eyebrow">Launch stance</div>
          <h2>Private, paid, and high-context.</h2>
          <p>
            OPS is designed for teams who need scenario rehearsal, narrative stress-testing, and
            population-specific foresight. It is not positioned as a consumer toy or a certainty engine.
          </p>
          <div class="readiness-actions">
            <button class="hero-button hero-button--primary" type="button" @click="openConsole">
              Try the Console
            </button>
            <button class="hero-button" type="button" @click="openAuth('signup')">
              Request Access
            </button>
          </div>
        </div>
      </section>
    </main>

    <transition name="modal-fade">
      <div v-if="authModalOpen" class="auth-modal" @click.self="closeAuth">
        <div class="auth-modal__dialog">
          <button class="auth-modal__close" type="button" @click="closeAuth">
            ×
          </button>
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
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import LandingAccessPanel from '../components/LandingAccessPanel.vue'
import { authState, signOut } from '../store/auth'

const router = useRouter()
const route = useRoute()
const heroImageUrl = new URL('../assets/logo/ops_logo_left.png', import.meta.url).href

const steps = [
  {
    number: '01',
    title: 'Graph Construction',
    description: 'Extract actors, institutions, locations, grievances, and memory anchors from source material.',
  },
  {
    number: '02',
    title: 'Population Setup',
    description: 'Weight segments, generate personas, and configure institutional seed voices for the world.',
  },
  {
    number: '03',
    title: 'Start Simulation',
    description: 'Run multi-agent cascades with memory updates, rumor spread, and temporal continuity.',
  },
  {
    number: '04',
    title: 'Report Generation',
    description: 'Produce structured findings grounded in evidence from the simulated environment.',
  },
  {
    number: '05',
    title: 'Deep Interaction',
    description: 'Interview simulated people or question the report agent about what moved the outcome.',
  },
]

const useCases = [
  {
    label: 'Policy / Government',
    title: 'Policy reaction forecasting',
    description: 'Stress-test public response before an announcement, price change, or institutional move.',
  },
  {
    label: 'Enterprise / Crisis',
    title: 'Narrative and crisis rehearsal',
    description: 'Model how a controversy, product shock, or reputational event moves through media and communities.',
  },
  {
    label: 'Research / Strategy',
    title: 'Population response analysis',
    description: 'Compare how segments react differently across class, geography, and institutional trust.',
  },
]

const authModalOpen = computed(() => Boolean(route.query.auth))
const accessMode = computed(() => (route.query.auth === 'signup' ? 'signup' : 'signin'))
const redirectPath = computed(() => (
  typeof route.query.redirect === 'string' && route.query.redirect
    ? route.query.redirect
    : '/console'
))

const mergeQuery = (patch = {}) => {
  const next = { ...route.query, ...patch }
  Object.keys(next).forEach(key => {
    if (next[key] === undefined || next[key] === null || next[key] === '') {
      delete next[key]
    }
  })
  return next
}

const openAuth = (mode) => {
  router.replace({
    name: 'Home',
    query: mergeQuery({
      auth: mode,
      redirect: route.query.redirect || '/console',
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

const openConsole = () => {
  if (authState.user) {
    router.push({ name: 'ConsoleStart' })
    return
  }

  router.replace({
    name: 'Home',
    query: mergeQuery({
      auth: 'signin',
      redirect: '/console',
    }),
  })
}

const handleAuthenticated = () => {
  const redirect = redirectPath.value
  closeAuth()
  if (redirect && redirect !== '/') {
    router.push(redirect)
  }
}

const handleSignOut = async () => {
  await signOut()
}
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 20% 0%, rgba(201, 75, 34, 0.12), transparent 30%),
    radial-gradient(circle at 80% 10%, rgba(77, 124, 255, 0.12), transparent 26%),
    #050608;
  color: #f7f7f3;
}

.landing-nav {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 22px 40px;
  backdrop-filter: blur(18px);
  background: rgba(5, 6, 8, 0.82);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.landing-brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.landing-brand__logo {
  width: 30px;
  height: 30px;
  object-fit: contain;
}

.landing-brand__text {
  font-family: var(--ops-font-mono, monospace);
  font-size: 15px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.landing-links {
  display: inline-flex;
  gap: 28px;
}

.landing-links a {
  color: rgba(247, 247, 243, 0.7);
  text-decoration: none;
  font-size: 14px;
}

.landing-actions {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.nav-button,
.hero-button {
  border: 1px solid rgba(255, 255, 255, 0.16);
  background: transparent;
  color: #f7f7f3;
  padding: 12px 16px;
  text-decoration: none;
  cursor: pointer;
  transition: transform 0.18s ease, background 0.18s ease, border-color 0.18s ease;
}

.nav-button:hover,
.hero-button:hover {
  transform: translateY(-1px);
  border-color: rgba(255, 255, 255, 0.34);
}

.nav-button--primary,
.hero-button--primary {
  background: #f7f7f3;
  color: #050608;
  border-color: #f7f7f3;
}

.nav-button--ghost {
  background: rgba(255, 255, 255, 0.04);
}

.landing-main {
  padding: 0 40px 120px;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
  gap: 42px;
  align-items: center;
  max-width: 1380px;
  margin: 0 auto;
  padding: 78px 0 64px;
}

.hero-copy {
  max-width: 760px;
}

.hero-eyebrow,
.section-eyebrow {
  font-family: var(--ops-font-mono, monospace);
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #f0a37d;
}

.hero-title {
  margin: 18px 0 22px;
  font-size: clamp(48px, 8vw, 88px);
  line-height: 0.98;
  letter-spacing: -0.05em;
  max-width: 820px;
}

.hero-description {
  max-width: 640px;
  font-size: 18px;
  line-height: 1.8;
  color: rgba(247, 247, 243, 0.76);
}

.hero-buttons {
  display: flex;
  gap: 14px;
  margin-top: 30px;
  flex-wrap: wrap;
}

.hero-trust {
  display: flex;
  gap: 18px;
  margin-top: 34px;
  flex-wrap: wrap;
}

.trust-item {
  min-width: 180px;
  padding: 16px 18px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
}

.trust-item__value {
  display: block;
  font-family: var(--ops-font-mono, monospace);
  font-size: 13px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #f7f7f3;
}

.trust-item__label {
  display: block;
  margin-top: 8px;
  font-size: 14px;
  color: rgba(247, 247, 243, 0.64);
  line-height: 1.5;
}

.hero-visual__frame {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.02));
  box-shadow: 0 40px 100px rgba(0, 0, 0, 0.32);
  padding: 22px;
}

.hero-visual__badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding: 6px 10px;
  font-family: var(--ops-font-mono, monospace);
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(247, 247, 243, 0.78);
}

.hero-visual__terminal {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(5, 6, 8, 0.72);
  padding: 18px;
}

.terminal-line {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.terminal-label {
  font-family: var(--ops-font-mono, monospace);
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(247, 247, 243, 0.48);
}

.terminal-text {
  font-size: 15px;
  line-height: 1.65;
  color: rgba(247, 247, 243, 0.84);
}

.terminal-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
  margin: 18px 0;
}

.terminal-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.terminal-card {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
  padding: 14px;
}

.terminal-card__title {
  font-family: var(--ops-font-mono, monospace);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #f7f7f3;
}

.terminal-card__copy {
  margin-top: 8px;
  font-size: 14px;
  line-height: 1.6;
  color: rgba(247, 247, 243, 0.66);
}

.section {
  max-width: 1380px;
  margin: 0 auto;
  padding: 72px 0 0;
}

.section--narrow {
  max-width: 1080px;
}

.section-heading {
  max-width: 720px;
}

.section-heading h2 {
  margin: 14px 0 0;
  font-size: clamp(32px, 4vw, 56px);
  line-height: 1.06;
  letter-spacing: -0.04em;
}

.steps-grid,
.use-case-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-top: 34px;
}

.step-card,
.use-case-card,
.readiness-card {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
  padding: 24px;
}

.step-card__number,
.use-case-card__label {
  font-family: var(--ops-font-mono, monospace);
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #f0a37d;
}

.step-card h3,
.use-case-card h3,
.readiness-card h2 {
  margin: 16px 0 10px;
  font-size: 24px;
}

.step-card p,
.use-case-card p,
.readiness-card p {
  margin: 0;
  font-size: 15px;
  line-height: 1.75;
  color: rgba(247, 247, 243, 0.68);
}

.readiness-actions {
  display: flex;
  gap: 14px;
  margin-top: 26px;
  flex-wrap: wrap;
}

.auth-modal {
  position: fixed;
  inset: 0;
  z-index: 40;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 28px;
  background: rgba(5, 6, 8, 0.74);
  backdrop-filter: blur(16px);
}

.auth-modal__dialog {
  position: relative;
  width: min(100%, 430px);
}

.auth-modal__close {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
  width: 34px;
  height: 34px;
  border: none;
  background: rgba(17, 24, 39, 0.08);
  color: #111827;
  font-size: 24px;
  cursor: pointer;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.18s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

@media (max-width: 1100px) {
  .landing-nav,
  .landing-main {
    padding-left: 24px;
    padding-right: 24px;
  }

  .landing-nav {
    flex-wrap: wrap;
  }

  .hero {
    grid-template-columns: 1fr;
  }

  .steps-grid,
  .use-case-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 760px) {
  .landing-nav {
    align-items: flex-start;
  }

  .landing-links {
    display: none;
  }

  .landing-actions {
    flex-wrap: wrap;
    justify-content: flex-end;
  }

  .hero {
    padding-top: 48px;
  }

  .hero-title {
    font-size: 44px;
  }

  .steps-grid,
  .use-case-grid {
    grid-template-columns: 1fr;
  }
}
</style>
