<template>
  <div class="demo-intake">
    <header class="demo-intake__nav">
      <button class="demo-intake__brand" type="button" @click="router.push('/')">Murmur</button>
      <button
        v-if="authState.user"
        class="demo-intake__action demo-intake__action--dark"
        type="button"
        @click="router.push('/console')"
      >
        Open console
      </button>
      <button
        v-else
        class="demo-intake__action"
        type="button"
        @click="router.push({ path: '/', query: { auth: 'signin', redirect: '/console' } })"
      >
        Login
      </button>
    </header>

    <main v-if="!loading" class="demo-intake__body">
      <section class="demo-intake__status">
        <div class="demo-intake__eyebrow">System Status</div>
        <h1 class="demo-intake__title">System Ready</h1>
        <p class="demo-intake__lead">System is ready to use</p>
        <p class="demo-intake__detail">{{ currentPack.intake.readinessLine }}</p>

        <div class="demo-intake__steps">
          <div class="demo-intake__steps-label">Workflow Steps</div>
          <article
            v-for="step in DEMO_WORKFLOW_STEPS"
            :key="step.number"
            class="demo-intake__step"
          >
            <div class="demo-intake__step-number">{{ step.number }}</div>
            <div>
              <h2 class="demo-intake__step-title">{{ step.title }}</h2>
              <p class="demo-intake__step-description">{{ step.description }}</p>
            </div>
          </article>
        </div>
      </section>

      <section class="demo-intake__console">
        <div class="demo-intake__section">
          <div class="demo-intake__section-header">
            <span>01 / Reality Seeds</span>
            <span>PDF</span>
          </div>
          <div class="demo-intake__seed-row">
            <div class="demo-intake__seed-left">
              <span class="demo-intake__seed-icon">DOC</span>
              <span>{{ currentPack.intake.seedLabel }}</span>
            </div>
            <span class="demo-intake__seed-action">↓</span>
          </div>
        </div>

        <div class="demo-intake__divider">
          <span>Input Parameters</span>
        </div>

        <form class="demo-intake__section" @submit.prevent="startDemo">
          <div class="demo-intake__section-header">
            <span>&gt;_ 02 / Simulation Requirement</span>
            <span>{{ currentPack.countryLabel }} demo pack</span>
          </div>

          <div class="demo-intake__input-shell">
            <textarea
              v-model.trim="scenarioDraft"
              class="demo-intake__textarea"
              rows="4"
              :placeholder="currentPack.intake.defaultScenario"
            />
            <div class="demo-intake__engine">Engine: Murmur-v0.1</div>
          </div>

          <button class="demo-intake__cta" type="submit">
            <span>Try Now</span>
            <span>-></span>
          </button>
        </form>

        <div class="demo-intake__disclaimer">
          <span class="demo-intake__disclaimer-icon">!</span>
          <span>This page is a static demo only. Deep interaction with agents is not connected to the live engine.</span>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authState } from '../../store/auth'
import { DEMO_WORKFLOW_STEPS } from '../../content/demoFlowPacks'
import { setDemoScenario } from '../../store/demoFlow'
import { useDemoRoute } from '../../composables/useDemoRoute'

const route = useRoute()
const router = useRouter()
const { loading, currentPack, demoQuery, scenario } = useDemoRoute(route, router, 'demo')
const scenarioDraft = ref('')

watch(
  scenario,
  value => {
    scenarioDraft.value = value
  },
  { immediate: true }
)

const startDemo = () => {
  const nextScenario = scenarioDraft.value.trim()
  if (!nextScenario) {
    return
  }

  setDemoScenario(nextScenario)
  router.push({
    path: '/demo/graph',
    query: {
      ...demoQuery.value,
      scenario: nextScenario,
    },
  })
}
</script>

<style scoped>
.demo-intake {
  min-height: 100vh;
  background: #fff;
  color: #050505;
  font-family: var(--murmur-font-ui, 'Lato', system-ui, sans-serif);
}

.demo-intake__nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 30px;
  border-bottom: 1px solid #efefef;
}

.demo-intake__brand {
  border: none;
  background: none;
  color: #050505;
  font-size: 20px;
  font-weight: 800;
  cursor: pointer;
}

.demo-intake__action {
  padding: 10px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  color: #050505;
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
}

.demo-intake__action--dark {
  background: #111;
  border-color: #111;
  color: #fff;
}

.demo-intake__body {
  display: grid;
  grid-template-columns: minmax(300px, 0.78fr) minmax(560px, 1.22fr);
  gap: 56px;
  padding: 54px 38px 64px;
}

.demo-intake__status {
  padding: 42px 8px 0 4px;
}

.demo-intake__eyebrow,
.demo-intake__steps-label {
  color: #9b9b9b;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 13px;
}

.demo-intake__title {
  margin: 28px 0 16px;
  font-size: clamp(40px, 4.8vw, 62px);
  line-height: 0.96;
  letter-spacing: -0.035em;
}

.demo-intake__lead {
  margin: 0;
  max-width: 360px;
  font-size: 16px;
  line-height: 1.4;
}

.demo-intake__detail {
  margin: 14px 0 0;
  max-width: 390px;
  color: #5b5b5b;
  font-size: 18px;
  line-height: 1.55;
}

.demo-intake__steps {
  margin-top: 64px;
}

.demo-intake__step {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  gap: 12px;
  margin-top: 26px;
}

.demo-intake__step-number {
  color: #b6b6b6;
  font-size: 18px;
  font-weight: 800;
  line-height: 1;
}

.demo-intake__step-title {
  margin: 0;
  font-size: 16px;
  line-height: 1.15;
  font-weight: 800;
}

.demo-intake__step-description {
  margin: 10px 0 0;
  color: #333;
  font-size: 14px;
  line-height: 1.65;
}

.demo-intake__console {
  border: 1px solid #d7d7d7;
  background: #fff;
}

.demo-intake__section {
  padding: 24px 28px 0;
}

.demo-intake__section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #6d6d6d;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 12px;
}

.demo-intake__seed-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20px;
  padding: 18px;
  border: 1px solid #e6e6e6;
  background: #fafafa;
}

.demo-intake__seed-left {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 14px;
}

.demo-intake__seed-icon,
.demo-intake__seed-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  min-height: 28px;
  border: 1px solid #dedede;
  font-size: 11px;
}

.demo-intake__divider {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 32px 0 0;
  color: #bebebe;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 13px;
}

.demo-intake__divider::before,
.demo-intake__divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #ebebeb;
}

.demo-intake__divider::before {
  margin-right: 16px;
}

.demo-intake__divider::after {
  margin-left: 16px;
}

.demo-intake__input-shell {
  position: relative;
  margin-top: 20px;
  border: 1px solid #dcdcdc;
  background: #fcfcfc;
}

.demo-intake__textarea {
  width: 100%;
  min-height: 138px;
  border: none;
  resize: vertical;
  padding: 22px 20px 42px;
  background: transparent;
  color: #050505;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 16px;
  line-height: 1.55;
}

.demo-intake__textarea:focus {
  outline: none;
}

.demo-intake__engine {
  position: absolute;
  right: 18px;
  bottom: 14px;
  color: #ababab;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 12px;
}

.demo-intake__cta {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 22px;
  padding: 18px 20px;
  border: 1px solid #e2e2e2;
  background: #fff;
  color: #050505;
  font-size: 16px;
  font-weight: 800;
  cursor: pointer;
}

.demo-intake__disclaimer {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 26px;
  padding: 14px 20px;
  border-top: 1px solid #ead9a2;
  background: #fffdf3;
  color: #89724a;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 12px;
}

.demo-intake__disclaimer-icon {
  display: inline-flex;
  width: 18px;
  height: 18px;
  align-items: center;
  justify-content: center;
  border: 1px solid currentColor;
}

@media (max-width: 1120px) {
  .demo-intake__body {
    grid-template-columns: 1fr;
  }

  .demo-intake__status {
    padding-top: 12px;
  }
}
</style>
