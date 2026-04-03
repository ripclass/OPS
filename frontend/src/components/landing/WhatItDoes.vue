<template>
  <section ref="targetRef" class="does-shell" :class="{ 'does-shell--visible': isVisible }">
    <div class="does-label">WHAT IT DOES</div>

    <div class="does-top">
      <h2 class="does-title" v-html="decoratedTitle" />
      <div class="does-standfirst">
        <p class="does-standfirst__lead" v-html="decoratedLead" />
        <p class="does-standfirst__detail" v-html="decoratedDetail" />
      </div>
    </div>

    <div class="does-strip">
      <article class="does-column">
        <div class="does-column__eyebrow">YOU GIVE IT</div>

        <figure class="does-illustration" aria-label="What it does illustration">
          <img src="/landing/what-it-does-illustration-cutout.png" alt="" />
        </figure>

        <p class="does-column__copy">{{ inputCopy }}</p>
      </article>

      <article class="does-column does-column--center">
        <div class="does-column__eyebrow">MURMUR RUNS</div>

        <ul class="does-note-list" aria-label="Murmur simulation mechanism">
          <li v-for="item in mechanismItems" :key="item.label" class="does-note-item">
            <div class="does-note-item__label">{{ item.label }}</div>
            <p class="does-note-item__detail">{{ item.detail }}</p>
          </li>
        </ul>

        <div class="does-scribble">who shares / who absorbs / who goes quiet</div>

        <p class="does-column__copy">{{ runCopy }}</p>
      </article>

      <article class="does-column">
        <div class="does-column__eyebrow">IT RETURNS</div>

        <ul class="does-note-list" aria-label="Murmur outputs">
          <li v-for="item in outputItems" :key="item.label" class="does-note-item">
            <div class="does-note-item__label">{{ item.label }}</div>
            <p class="does-note-item__detail">{{ item.detail }}</p>
          </li>
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

const mechanismItems = [
  {
    label: 'Country priors',
    detail: 'Local conditions, class structure, language, and trust baselines.',
  },
  {
    label: 'Specific agents',
    detail: 'Named people with income sources, dialects, fears, and social position.',
  },
  {
    label: 'Institutional seeds',
    detail: 'Parties, media, ministries, unions, clinics, and community voices.',
  },
  {
    label: 'Cascade simulation',
    detail: 'Who hears it first, who passes it on, and where it accelerates.',
  },
  {
    label: 'Memory + silence',
    detail: 'What gets spoken, what stays hidden, and what behavior changes quietly.',
  },
]

const outputItems = [
  {
    label: 'Likely reactions',
    detail: 'The first emotional and practical responses the scenario triggers.',
  },
  {
    label: 'Segment splits',
    detail: 'How workers, students, migrants, and officials react differently.',
  },
  {
    label: 'Amplifier paths',
    detail: 'Which people, networks, and channels drive wider spread.',
  },
  {
    label: 'Silent absorption',
    detail: 'Who changes behavior without posting, protesting, or declaring anything.',
  },
  {
    label: 'Report + rehearsal',
    detail: 'A readable forecast plus a structured way to test the scenario again.',
  },
]

const decorate = (text, target, replacement) => text.replace(target, replacement)

const decoratedTitle = computed(() => decorate(
  'It turns a scenario into a living public sphere before reality catches up.',
  'scenario',
  '<span class="does-circle">scenario</span>'
))

const decoratedLead = computed(() => decorate(
  'Murmur takes a scenario brief and runs it through specific people, not averages.',
  'Murmur',
  '<span class="does-circle does-circle--brand">Murmur</span>'
))

const decoratedDetail = computed(() => decorate(
  decorate(
    'You are not looking at sentiment. You are looking at behavior under pressure.',
    'sentiment',
    '<span class="does-circle does-circle--small">sentiment</span>'
  ),
  'behavior under pressure',
  '<span class="does-underline">behavior under pressure</span>'
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
  position: relative;
  display: inline-block;
  margin-bottom: 18px;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.11em;
  text-transform: uppercase;
}

.does-column__eyebrow::after {
  content: '';
  position: absolute;
  left: -0.08em;
  right: -0.08em;
  bottom: -0.28em;
  border-bottom: 3px solid #0048ff;
  border-radius: 999px;
  transform: rotate(-1.5deg);
  pointer-events: none;
}

.does-illustration {
  margin: 2px 0 18px;
}

.does-illustration img {
  display: block;
  width: min(100%, 300px);
  height: auto;
}

.does-column__copy {
  margin: 0;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 16px;
  line-height: 1.5;
}

.does-note-list {
  margin: 0 0 18px;
  padding: 0;
  list-style: none;
}

.does-note-item {
  position: relative;
  margin: 0 0 14px;
  padding-left: 16px;
}

.does-note-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.48em;
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: #0048ff;
}

.does-note-item__label {
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 15px;
  font-weight: 900;
  letter-spacing: 0.03em;
}

.does-note-item__detail {
  margin: 4px 0 0;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 14px;
  line-height: 1.35;
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

:deep(.does-circle),
:deep(.does-underline) {
  position: relative;
  display: inline-block;
}

:deep(.does-underline::after) {
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

:deep(.does-circle::before),
:deep(.does-circle::after) {
  content: '';
  position: absolute;
  pointer-events: none;
  border-radius: 999px;
}

:deep(.does-circle::before) {
  inset: -0.14em -0.18em -0.08em -0.18em;
  border: 2px solid rgba(0, 72, 255, 0.9);
  transform: rotate(-5deg);
}

:deep(.does-circle::after) {
  inset: -0.08em -0.12em -0.14em -0.14em;
  border: 2px solid rgba(0, 72, 255, 0.72);
  transform: rotate(4deg);
}

:deep(.does-circle--small::before) {
  inset: -0.12em -0.16em -0.08em -0.16em;
}

:deep(.does-circle--small::after) {
  inset: -0.08em -0.12em -0.12em -0.12em;
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
