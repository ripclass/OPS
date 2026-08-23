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
          />
          <div class="scenario-engine-badge">Engine: Murmur / OASIS</div>
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

        <button class="scenario-primary" type="submit">
          <span>{{ ctaLabel }}</span>
          <span class="scenario-primary__arrow">-&gt;</span>
        </button>

        <p class="scenario-note">Starts at step 01 of 05. Nothing else to fill in.</p>
      </div>
    </form>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

const emit = defineEmits(['submit'])

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

// An empty box is not a dead end: the run falls back to the sample brief for
// whichever country pack the visitor resolves to.
const ctaLabel = computed(() => (scenario.value ? 'Run this brief' : 'Run the sample brief'))

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

const handleSubmit = () => {
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
