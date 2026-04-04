<template>
  <section ref="targetRef" class="scenario-shell" :class="{ 'scenario-shell--visible': isVisible }">
    <div class="scenario-label">RUN A SCENARIO</div>

    <div class="scenario-top">
      <h2 class="scenario-title" v-html="decoratedTitle" />

      <div class="scenario-standfirst">
        <p class="scenario-standfirst__lead" v-html="decoratedLead" />
        <p class="scenario-standfirst__detail">This opens the public Murmur demo flow.</p>
      </div>
    </div>

    <div class="scenario-scribble">before it leaves your desk</div>

    <form class="scenario-console" aria-label="Landing demo handoff" @submit.prevent="handleSubmit">
      <div class="scenario-console__section">
        <div class="scenario-console__header">
          <span class="scenario-console__label">01 / Reality Seeds</span>
          <span class="scenario-console__meta">Static demo intake</span>
        </div>

        <div class="scenario-seed-row" aria-hidden="true">
          <div class="scenario-seed-row__left">
            <span class="scenario-seed-row__icon">DOC</span>
            <span class="scenario-seed-row__name">Bangladesh Rice Price Shock Brief.pdf</span>
          </div>
          <span class="scenario-seed-row__action">DL</span>
        </div>
      </div>

      <div class="scenario-console__divider">
        <span>Input Parameters</span>
      </div>

      <div class="scenario-console__section scenario-console__section--brief">
        <div class="scenario-console__header">
          <span class="scenario-console__label">&gt;_ 02 / Scenario Brief</span>
          <span class="scenario-console__meta">Public demo handoff</span>
        </div>

        <div class="scenario-input-wrapper">
          <textarea
            v-model.trim="scenario"
            class="scenario-input"
            rows="6"
            :placeholder="placeholder"
          />
          <div class="scenario-engine-badge">Engine: OPS / OASIS</div>
        </div>

        <button class="scenario-primary" type="submit">
          <span>Run scenario</span>
          <span class="scenario-primary__arrow">-&gt;</span>
        </button>
      </div>
    </form>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

const emit = defineEmits(['submit'])

const placeholder = "Tell us what you're about to announce. We'll show you what happens next."
const scenario = ref('')
const { targetRef, isVisible } = useRevealOnScroll()

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
  if (!scenario.value) {
    return
  }

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

.scenario-seed-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 18px;
  padding: 16px 18px;
  border: 1px solid #e6e6e6;
  background: #fafafa;
}

.scenario-seed-row__left {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: "Mom´sTypewriter", var(--murmur-font-type);
  font-size: 15px;
}

.scenario-seed-row__icon,
.scenario-seed-row__action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  min-height: 28px;
  border: 1px solid #dedede;
  font-size: 11px;
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

.scenario-primary {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20px;
  padding: 20px 22px;
  border: 1px solid #e2e2e2;
  background: #fff;
  color: #050505;
  font-size: 28px;
  font-weight: 800;
  cursor: pointer;
}

.scenario-primary__arrow {
  font-size: 22px;
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
</style>
