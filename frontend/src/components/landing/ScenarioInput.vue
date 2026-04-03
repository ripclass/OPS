<template>
  <section ref="targetRef" class="scenario-shell" :class="{ 'scenario-shell--visible': isVisible }">
    <div class="scenario-label">RUN A SCENARIO</div>

    <div class="scenario-top">
      <h2 class="scenario-title" v-html="decoratedTitle" />

      <div class="scenario-standfirst">
        <p class="scenario-standfirst__lead" v-html="decoratedLead" />
        <p class="scenario-standfirst__detail">Private, paid, and reviewed by hand before anything goes live.</p>
      </div>
    </div>

    <div class="scenario-scribble">before it leaves your desk</div>

    <form class="scenario-form" @submit.prevent="handleSubmit">
      <textarea
        v-model.trim="scenario"
        class="scenario-input"
        rows="4"
        :placeholder="placeholder"
      />

      <div class="scenario-actions">
        <button class="scenario-button" type="submit">Run scenario -></button>
        <button class="scenario-link" type="button" @click="$emit('request-access')">
          Or request full platform access for your team ->
        </button>
      </div>
    </form>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

const emit = defineEmits(['submit', 'request-access'])

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

  const value = scenario.value
  scenario.value = ''
  emit('submit', value)
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
  margin-top: 18px;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 18px;
  line-height: 1.24;
}

.scenario-scribble {
  margin: 28px 0 0;
  color: #0048ff;
  font-family: var(--murmur-font-hand);
  font-size: 28px;
  line-height: 0.82;
  text-align: right;
  transform: rotate(-2deg);
}

.scenario-form {
  margin-top: 30px;
  padding-top: 26px;
  border-top: 1px solid rgba(5, 5, 5, 0.12);
}

.scenario-input {
  width: 100%;
  min-height: 188px;
  border: 1px solid rgba(5, 5, 5, 0.16);
  background: #fcfcfb;
  color: #050505;
  padding: 24px 24px 22px;
  resize: vertical;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 20px;
  line-height: 1.42;
}

.scenario-input::placeholder {
  color: rgba(5, 5, 5, 0.46);
}

.scenario-input:focus {
  outline: none;
  border-color: rgba(0, 72, 255, 0.42);
  box-shadow: 0 0 0 4px rgba(0, 72, 255, 0.08);
}

.scenario-actions {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 20px;
  margin-top: 18px;
  flex-wrap: wrap;
}

.scenario-button,
.scenario-link {
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
}

.scenario-button {
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 18px;
  font-weight: 900;
  letter-spacing: 0.02em;
}

.scenario-link {
  color: #5a7692;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 16px;
  line-height: 1.25;
  text-align: right;
}

:deep(.scenario-underline),
:deep(.scenario-circle) {
  position: relative;
  display: inline-block;
}

:deep(.scenario-underline::after) {
  content: '';
  position: absolute;
  left: -0.08em;
  right: -0.08em;
  bottom: -0.08em;
  border-bottom: 4px solid #0048ff;
  border-radius: 999px;
  transform: rotate(-1.5deg);
  pointer-events: none;
}

:deep(.scenario-circle::before),
:deep(.scenario-circle::after) {
  content: '';
  position: absolute;
  pointer-events: none;
  border-radius: 999px;
}

:deep(.scenario-circle::before) {
  inset: -0.16em -0.18em -0.1em -0.18em;
  border: 2px solid rgba(0, 72, 255, 0.9);
  transform: rotate(-5deg);
}

:deep(.scenario-circle::after) {
  inset: -0.08em -0.12em -0.16em -0.14em;
  border: 2px solid rgba(0, 72, 255, 0.72);
  transform: rotate(4deg);
}

@media (max-width: 960px) {
  .scenario-top {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .scenario-standfirst {
    padding-top: 0;
  }
}

@media (max-width: 640px) {
  .scenario-standfirst__lead {
    font-size: 18px;
  }

  .scenario-standfirst__detail,
  .scenario-link {
    font-size: 16px;
  }

  .scenario-input {
    min-height: 160px;
    padding: 20px;
    font-size: 18px;
  }

  .scenario-button {
    font-size: 16px;
  }

  .scenario-scribble {
    text-align: left;
    font-size: 22px;
  }
}
</style>
