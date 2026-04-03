<template>
  <section ref="targetRef" class="does-shell" :class="{ 'does-shell--visible': isVisible }">
    <div class="does-label">WHAT IT DOES</div>

    <div class="does-top">
      <h2 class="does-title" v-html="decoratedTitle" />
      <div class="does-standfirst">
        <p class="does-standfirst__lead">
          Murmur takes a scenario brief and runs it through specific people, not averages.
        </p>
        <p class="does-standfirst__detail">
          You are not looking at sentiment. You are looking at behavior under pressure.
        </p>
      </div>
    </div>

    <div class="does-strip">
      <article class="does-column">
        <div class="does-column__eyebrow">YOU GIVE IT</div>

        <div class="does-sample">
          <p>Rice rises 40% before Eid in Dhaka.</p>
          <p>What happens in low-income households,</p>
          <p>student networks, and rumor chains?</p>
        </div>

        <p class="does-column__copy">{{ inputCopy }}</p>
      </article>

      <article class="does-column does-column--center">
        <div class="does-column__eyebrow">MURMUR RUNS</div>

        <ul class="does-mechanism" aria-label="Murmur simulation mechanism">
          <li>country priors</li>
          <li>specific agents</li>
          <li>institutional seeds</li>
          <li>cascade simulation</li>
          <li>memory + silence</li>
        </ul>

        <div class="does-scribble">who shares / who absorbs / who goes quiet</div>

        <p class="does-column__copy">{{ runCopy }}</p>
      </article>

      <article class="does-column">
        <div class="does-column__eyebrow">IT RETURNS</div>

        <ul class="does-output" aria-label="Murmur outputs">
          <li>likely reactions</li>
          <li>segment splits</li>
          <li>amplifier paths</li>
          <li>silent absorption</li>
          <li>report + scenario rehearsal</li>
        </ul>

        <p class="does-column__copy">{{ outputCopy }}</p>
        <p class="does-column__closing">{{ closingCopy }}</p>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

const props = defineProps({
  paragraphs: {
    type: Array,
    required: true,
  },
})

const { targetRef, isVisible } = useRevealOnScroll()

const inputCopy = computed(() => props.paragraphs[0] || '')
const runCopy = computed(() => [props.paragraphs[1], props.paragraphs[2]].filter(Boolean).join(' '))
const outputCopy = computed(() => props.paragraphs[3] || '')
const closingCopy = computed(() => props.paragraphs[4] || '')

const decoratedTitle = computed(() => (
  'It turns a scenario into a <span class="does-title__underline">living public sphere</span> before reality catches up.'
))
</script>

<style scoped>
.does-shell {
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.does-shell--visible {
  opacity: 1;
  transform: translateY(0);
}

.does-label {
  margin-bottom: 20px;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.does-top {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(260px, 0.8fr);
  gap: 36px;
  align-items: start;
}

.does-title {
  margin: 0;
  color: #050505;
  font-family: var(--murmur-font-display);
  font-size: clamp(40px, 5.2vw, 68px);
  font-weight: 800;
  line-height: 0.95;
  letter-spacing: -0.035em;
  text-wrap: balance;
}

.does-standfirst {
  padding-top: 8px;
}

.does-standfirst__lead,
.does-standfirst__detail {
  margin: 0;
  color: #050505;
}

.does-standfirst__lead {
  font-family: var(--murmur-font-ui);
  font-size: 24px;
  line-height: 1.24;
}

.does-standfirst__detail {
  margin-top: 18px;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 18px;
  line-height: 1.3;
}

.does-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 28px;
  margin-top: 42px;
  padding-top: 22px;
  border-top: 1px solid rgba(5, 5, 5, 0.12);
}

.does-column {
  position: relative;
  padding-right: 10px;
}

.does-column:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 0;
  right: -14px;
  bottom: 0;
  width: 1px;
  background: rgba(5, 5, 5, 0.08);
}

.does-column__eyebrow {
  margin-bottom: 18px;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.11em;
  text-transform: uppercase;
}

.does-sample {
  margin-bottom: 18px;
  padding: 14px 16px 12px;
  border: 1px solid rgba(5, 5, 5, 0.12);
  background: rgba(255, 255, 255, 0.6);
}

.does-sample p {
  margin: 0;
  color: #050505;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 15px;
  line-height: 1.18;
}

.does-sample p + p {
  margin-top: 6px;
}

.does-column__copy {
  margin: 0;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 16px;
  line-height: 1.5;
}

.does-mechanism,
.does-output {
  margin: 0 0 18px;
  padding: 0;
  list-style: none;
}

.does-mechanism li,
.does-output li {
  margin: 0 0 9px;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 15px;
  font-weight: 900;
  letter-spacing: 0.03em;
  text-transform: lowercase;
}

.does-scribble {
  margin: 6px 0 18px;
  color: #0048ff;
  font-family: var(--murmur-font-hand);
  font-size: 24px;
  line-height: 0.82;
  transform: rotate(-2deg);
}

.does-column__closing {
  margin: 16px 0 0;
  color: #050505;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 18px;
  line-height: 1.2;
}

:deep(.does-title__underline) {
  position: relative;
  display: inline-block;
}

:deep(.does-title__underline::after) {
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

@media (max-width: 960px) {
  .does-top {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .does-standfirst {
    padding-top: 0;
  }

  .does-strip {
    grid-template-columns: 1fr;
    gap: 26px;
  }

  .does-column {
    padding-right: 0;
  }

  .does-column:not(:last-child)::after {
    top: auto;
    left: 0;
    right: 0;
    bottom: -14px;
    width: auto;
    height: 1px;
  }
}

@media (max-width: 640px) {
  .does-standfirst__lead {
    font-size: 20px;
  }

  .does-standfirst__detail,
  .does-column__closing {
    font-size: 16px;
  }

  .does-column__copy {
    font-size: 15px;
  }

  .does-scribble {
    font-size: 20px;
  }
}
</style>
