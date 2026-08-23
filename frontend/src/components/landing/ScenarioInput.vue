<template>
  <section ref="targetRef" class="scenario-shell" :class="{ 'scenario-shell--visible': isVisible }">
    <div class="scenario-label">RUN A SCENARIO</div>

    <div class="scenario-top">
      <h2 class="scenario-title" v-html="decoratedTitle" />

      <div class="scenario-standfirst">
        <p class="scenario-standfirst__lead" v-html="decoratedLead" />
        <p class="scenario-standfirst__detail">This runs the public Murmur demo end to end. No account needed.</p>
      </div>
    </div>

    <div class="scenario-scribble">before it leaves your desk</div>

    <form class="scenario-console" aria-label="Landing demo handoff" @submit.prevent="handleSubmit">
      <div class="scenario-console__section scenario-console__section--brief">
        <div class="scenario-console__header">
          <span class="scenario-console__label">&gt;_ 01 / Scenario Brief</span>
          <span class="scenario-console__meta">Public demo</span>
        </div>

        <div class="scenario-input-wrapper">
          <textarea
            v-model.trim="scenario"
            class="scenario-input"
            rows="6"
            aria-label="Scenario brief"
            :placeholder="placeholder"
            :readonly="running"
          />
          <div class="scenario-engine-badge">Engine: Murmur / OASIS</div>
        </div>

        <p v-if="statusLine" class="scenario-status" role="status" aria-live="polite">
          <span class="scenario-status__dot" />
          <span>{{ statusLine }}</span>
        </p>

        <div v-if="revealedSeedDocs.length" class="scenario-seeds">
          <div class="scenario-seeds__header">
            <span class="scenario-seeds__label">Reality seeds</span>
            <span class="scenario-seeds__count">{{ revealedSeedDocs.length }} of {{ seedDocs.length }} attached</span>
          </div>
          <ul class="scenario-seeds__list">
            <li v-for="doc in revealedSeedDocs" :key="doc.name" class="scenario-seed">
              <span class="scenario-seed__kind">{{ doc.kind }}</span>
              <span class="scenario-seed__body">
                <span class="scenario-seed__name">{{ doc.name }}</span>
                <span class="scenario-seed__note">{{ doc.note }}</span>
              </span>
              <span class="scenario-seed__tick">attached</span>
            </li>
          </ul>
        </div>
      </div>

      <div class="scenario-console__divider">
        <span>What the run does</span>
      </div>

      <div class="scenario-console__section scenario-console__section--steps">
        <ol class="scenario-steps">
          <li v-for="step in RUN_STEPS" :key="step.number" class="scenario-step">
            <span class="scenario-step__number">{{ step.number }}</span>
            <span class="scenario-step__title">{{ step.title }}</span>
          </li>
        </ol>

        <button class="scenario-primary" type="submit" :disabled="running">
          <span>{{ ctaLabel }}</span>
          <span class="scenario-primary__arrow">-&gt;</span>
        </button>

        <p class="scenario-note">Starts at step 01 of 05. Nothing else to fill in.</p>
      </div>
    </form>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'
import { DEMO_DEFAULT_PACK_KEY, getDemoPack } from '../../content/demoFlowPacks'
import { getSeedDocsForPack } from '../../content/demoSeedDocs'

const emit = defineEmits(['submit'])

// The parent resolves these from the visitor's country pack. The defaults are
// the default pack's own brief and seeds, so the theater still consumes
// something real if the binding is ever missing.
const props = defineProps({
  sampleBrief: {
    type: String,
    default: () => getDemoPack(DEMO_DEFAULT_PACK_KEY).intake.defaultScenario,
  },
  seedDocs: {
    type: Array,
    default: () => getSeedDocsForPack(DEMO_DEFAULT_PACK_KEY),
  },
})

// Named for what the visitor will watch happen, so the button is not a leap in
// the dark and the panel cannot be mistaken for the demo's own intake form.
const RUN_STEPS = [
  { number: '01', title: 'Scenario graph' },
  { number: '02', title: 'Population' },
  { number: '03', title: 'Cascade' },
  { number: '04', title: 'Report' },
  { number: '05', title: 'Interview' },
]

const placeholder = "Tell us what you're about to announce. We'll show you what happens next."
const scenario = ref('')
const { targetRef, isVisible } = useRevealOnScroll()

// The run has to be seen receiving its inputs before it advances, otherwise the
// jump to step 01 looks like nothing was consumed. These three refs drive that
// short intake sequence.
const running = ref(false)
const statusLine = ref('')
const revealedCount = ref(0)

const TYPE_TICK_MS = 28
const TYPE_DURATION_MS = 1200
const SEED_STAGGER_MS = 160
const SEED_SETTLE_MS = 350
const PREFILLED_SETTLE_MS = 300
const REDUCED_MOTION_HOLD_MS = 400

const revealedSeedDocs = computed(() => (props.seedDocs || []).slice(0, revealedCount.value))

// An empty box is not a dead end: the run falls back to the sample brief for
// whichever country pack the visitor resolves to.
const ctaLabel = computed(() => {
  if (running.value) {
    return 'Reading inputs'
  }
  return scenario.value ? 'Run this brief' : 'Run the sample brief'
})

// Every timer is tracked so navigating away mid-theater cannot fire a callback
// against a torn-down component.
const timers = []
let typeTimer = null

const schedule = (fn, delay) => {
  const id = window.setTimeout(fn, delay)
  timers.push(id)
  return id
}

const clearAllTimers = () => {
  timers.splice(0).forEach((id) => window.clearTimeout(id))
  if (typeTimer !== null) {
    window.clearInterval(typeTimer)
    typeTimer = null
  }
}

onBeforeUnmount(clearAllTimers)

const prefersReducedMotion = () => (
  typeof window !== 'undefined'
  && typeof window.matchMedia === 'function'
  && window.matchMedia('(prefers-reduced-motion: reduce)').matches
)

const wait = (ms) => new Promise((resolve) => {
  schedule(resolve, ms)
})

// Batches characters per tick so a long brief lands in the same ~1.2s a short
// one does, instead of crawling.
const typeInto = (text, durationMs) => new Promise((resolve) => {
  const total = text.length
  if (!total) {
    resolve()
    return
  }

  const ticks = Math.max(1, Math.round(durationMs / TYPE_TICK_MS))
  const perTick = Math.max(1, Math.ceil(total / ticks))
  let index = 0

  scenario.value = ''
  typeTimer = window.setInterval(() => {
    index = Math.min(total, index + perTick)
    scenario.value = text.slice(0, index)
    if (index >= total) {
      window.clearInterval(typeTimer)
      typeTimer = null
      resolve()
    }
  }, TYPE_TICK_MS)
})

const revealSeeds = (staggerMs) => new Promise((resolve) => {
  const docs = props.seedDocs || []
  revealedCount.value = 0
  if (!docs.length) {
    resolve()
    return
  }

  docs.forEach((_, index) => {
    schedule(() => {
      revealedCount.value = index + 1
    }, staggerMs * (index + 1))
  })
  schedule(resolve, staggerMs * docs.length + 120)
})

const decorate = (text, target, replacement) => text.replace(target, replacement)

const decoratedTitle = computed(() => decorate(
  "Tell us what you're about to announce.",
  'announce',
  '<span class="scenario-circle">announce</span>'
))

const decoratedLead = computed(() => decorate(
  "We'll show you what happens next.",
  'what happens next',
  '<span class="scenario-underline">what happens next</span>'
))

const handleSubmit = async () => {
  if (running.value) {
    return
  }

  const typed = scenario.value.trim()
  const reduced = prefersReducedMotion()
  running.value = true

  if (!typed && props.sampleBrief) {
    statusLine.value = 'Loading the sample brief'
    if (reduced) {
      scenario.value = props.sampleBrief
    } else {
      await typeInto(props.sampleBrief, TYPE_DURATION_MS)
    }
  }

  statusLine.value = 'Attaching reality seeds'

  if (reduced) {
    revealedCount.value = (props.seedDocs || []).length
    await wait(REDUCED_MOTION_HOLD_MS)
  } else {
    await revealSeeds(SEED_STAGGER_MS)
    statusLine.value = 'Handing the run its inputs'
    await wait(typed ? PREFILLED_SETTLE_MS : SEED_SETTLE_MS)
  }

  // running stays set on purpose. The parent navigates away from here, and
  // holding the guard stops a second run being fired during the route change.
  emit('submit', scenario.value.trim())
}
</script>

<style scoped>
.scenario-shell {
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.scenario-shell--visible {
  opacity: 1;
  transform: translateY(0);
}

.scenario-label {
  margin-bottom: 20px;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.scenario-top {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(260px, 0.78fr);
  gap: 36px;
  align-items: start;
}

.scenario-title {
  margin: 0;
  color: #050505;
  font-family: var(--murmur-font-display);
  font-size: clamp(40px, 5.4vw, 68px);
  font-weight: 800;
  line-height: 0.95;
  letter-spacing: -0.035em;
  text-wrap: balance;
}

.scenario-standfirst {
  padding-top: 8px;
}

.scenario-standfirst__lead,
.scenario-standfirst__detail {
  margin: 0;
  color: #050505;
}

.scenario-standfirst__lead {
  font-family: var(--murmur-font-ui);
  font-size: 22px;
  line-height: 1.34;
}

.scenario-standfirst__detail {
  margin-top: 14px;
  font-family: "Mom´sTypewriter", var(--murmur-font-type);
  font-size: 13px;
  line-height: 1.45;
}

.scenario-scribble {
  margin: 26px 0 18px auto;
  width: fit-content;
  color: #0048ff;
  font-family: var(--murmur-font-hand);
  font-size: clamp(34px, 4.2vw, 52px);
  line-height: 0.92;
  transform: rotate(-3deg);
}

.scenario-console {
  border: 1px solid #d7d7d7;
  background: #fff;
}

.scenario-console__section {
  padding: 24px 28px 0;
}

.scenario-console__section--brief {
  padding-bottom: 4px;
}

.scenario-console__section--steps {
  padding-bottom: 28px;
}

.scenario-console__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.scenario-console__label,
.scenario-console__meta,
.scenario-console__divider {
  color: #6d6d6d;
  font-family: "Mom´sTypewriter", var(--murmur-font-type);
}

.scenario-console__label,
.scenario-console__meta {
  font-size: 12px;
}

.scenario-console__divider {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin: 26px 0 0;
  font-size: 12px;
}

.scenario-console__divider::before,
.scenario-console__divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #ebebeb;
}

.scenario-input-wrapper {
  position: relative;
  margin-top: 18px;
  border: 1px solid #dcdcdc;
  background: #fcfcfc;
}

.scenario-input {
  width: 100%;
  min-height: 180px;
  border: none;
  resize: vertical;
  padding: 24px 22px 46px;
  background: transparent;
  color: #050505;
  font-family: "Mom´sTypewriter", var(--murmur-font-type);
  font-size: 20px;
  line-height: 1.52;
}

.scenario-input:focus {
  outline: none;
}

.scenario-engine-badge {
  position: absolute;
  right: 16px;
  bottom: 14px;
  color: #ababab;
  font-family: "Mom´sTypewriter", var(--murmur-font-type);
  font-size: 12px;
}

.scenario-status {
  display: flex;
  align-items: center;
  gap: 9px;
  margin: 12px 0 0;
  color: #0048ff;
  font-family: "Mom´sTypewriter", var(--murmur-font-type);
  font-size: 12px;
}

.scenario-status__dot {
  width: 7px;
  height: 7px;
  background: #0048ff;
  animation: scenario-status-pulse 0.9s ease-in-out infinite;
}

@keyframes scenario-status-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.25; }
}

.scenario-seeds {
  margin-top: 14px;
  border-top: 1px solid #ebebeb;
  padding-top: 12px;
}

.scenario-seeds__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.scenario-seeds__label {
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.scenario-seeds__count {
  color: #6d6d6d;
  font-family: "Mom´sTypewriter", var(--murmur-font-type);
  font-size: 12px;
}

.scenario-seeds__list {
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.scenario-seed {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border: 1px solid #d7d7d7;
  background: #fcfcfc;
  animation: scenario-seed-in 0.22s ease-out both;
}

@keyframes scenario-seed-in {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

.scenario-seed__kind {
  flex: none;
  min-width: 44px;
  padding: 3px 6px;
  border: 1px solid #0048ff;
  color: #0048ff;
  font-family: "Mom´sTypewriter", var(--murmur-font-type);
  font-size: 11px;
  letter-spacing: 0.04em;
  text-align: center;
}

.scenario-seed__body {
  display: grid;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.scenario-seed__name {
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 14px;
  font-weight: 700;
  line-height: 1.25;
  overflow-wrap: anywhere;
}

.scenario-seed__note {
  color: #6d6d6d;
  font-family: "Mom´sTypewriter", var(--murmur-font-type);
  font-size: 11px;
  line-height: 1.3;
}

.scenario-seed__tick {
  display: flex;
  align-items: center;
  gap: 7px;
  flex: none;
  color: #6d6d6d;
  font-family: "Mom´sTypewriter", var(--murmur-font-type);
  font-size: 11px;
}

/* Drawn rather than set as a glyph, so no font substitutes an emoji tick. */
.scenario-seed__tick::before {
  content: '';
  width: 5px;
  height: 9px;
  border-right: 2px solid #0048ff;
  border-bottom: 2px solid #0048ff;
  transform: translateY(-1px) rotate(45deg);
}

.scenario-primary:disabled {
  cursor: progress;
  opacity: 0.72;
}

.scenario-primary:disabled:hover {
  background: #111;
  border-color: #111;
}

@media (prefers-reduced-motion: reduce) {
  .scenario-status__dot,
  .scenario-seed {
    animation: none;
  }
}

.scenario-steps {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  margin: 18px 0 0;
  padding: 0;
  list-style: none;
}

.scenario-step {
  display: grid;
  gap: 8px;
  padding-top: 12px;
  border-top: 2px solid #0048ff;
}

.scenario-step__number {
  color: #0048ff;
  font-family: "Mom´sTypewriter", var(--murmur-font-type);
  font-size: 13px;
  line-height: 1;
}

.scenario-step__title {
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 15px;
  font-weight: 900;
  line-height: 1.15;
}

.scenario-primary {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 26px;
  padding: 20px 22px;
  border: 1px solid #111;
  background: #111;
  color: #fff;
  font-family: var(--murmur-font-display);
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.02em;
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.scenario-primary:hover {
  background: #0048ff;
  border-color: #0048ff;
}

.scenario-primary__arrow {
  font-size: 22px;
}

.scenario-note {
  margin: 12px 0 0;
  color: #6d6d6d;
  font-family: "Mom´sTypewriter", var(--murmur-font-type);
  font-size: 12px;
}

:deep(.scenario-circle),
:deep(.scenario-underline) {
  position: relative;
  display: inline-block;
  z-index: 0;
}

:deep(.scenario-circle)::after {
  content: '';
  position: absolute;
  left: -0.12em;
  right: -0.12em;
  top: 0.08em;
  bottom: -0.08em;
  border: 2px solid #0048ff;
  border-radius: 999px;
  transform: rotate(-5deg);
  z-index: -1;
}

:deep(.scenario-underline)::after {
  content: '';
  position: absolute;
  left: -0.04em;
  right: -0.04em;
  bottom: -0.14em;
  height: 0.22em;
  border-bottom: 2px solid #0048ff;
  transform: rotate(-1.2deg);
  z-index: -1;
}

@media (max-width: 980px) {
  .scenario-top {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .scenario-steps {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .scenario-primary {
    font-size: 22px;
  }
}
</style>
