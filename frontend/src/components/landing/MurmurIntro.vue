<template>
  <section ref="targetRef" class="intro-shell" :class="{ 'intro-shell--visible': isVisible }">
    <div class="intro-kicker" v-html="decoratedKicker" />

    <div class="intro-grid">
      <div class="intro-lead">
        <h2 class="intro-title" v-html="decoratedTitle" />
      </div>

      <div class="intro-copy">
        <p class="intro-summary" v-html="decoratedSummary" />
        <p class="intro-detail" v-html="decoratedDetail" />
      </div>
    </div>
    <div class="intro-proof">
      <div class="intro-proof__rail" aria-label="Murmur proof strip">
        <span class="intro-proof__item">NOT A POLL</span>
        <span class="intro-proof__item">NOT SOCIAL LISTENING</span>
        <span class="intro-proof__item">NOT A DEMOGRAPHIC AVERAGE</span>
      </div>
      <p class="intro-proof__line">
        A Murmur simulation is a synthetic public sphere built from scenario material,
        country priors, institutional seeds, and behaviorally specific agents.
      </p>
      <div class="intro-proof__note">who absorbs / who shares / who goes silent</div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

const props = defineProps({
  kicker: {
    type: String,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  summary: {
    type: String,
    required: true,
  },
  detail: {
    type: String,
    required: true,
  },
})

const { targetRef, isVisible } = useRevealOnScroll()

const decorate = (text, target, replacement) => text.replace(target, replacement)

const decoratedKicker = computed(() => decorate(
  props.kicker,
  'scenario simulation',
  '<span class="intro-underline">scenario simulation</span>'
))

const decoratedTitle = computed(() => decorate(
  decorate(
    props.title,
    'populations',
    '<span class="intro-circle">populations</span>'
  ),
  'narratives react',
  '<span class="intro-underline intro-underline--tight">narratives react</span>'
))

const decoratedSummary = computed(() => decorate(
  props.summary,
  'simulated public sphere',
  '<span class="intro-underline intro-underline--summary">simulated public sphere</span>'
))

const decoratedDetail = computed(() => decorate(
  props.detail,
  'market moves.',
  '<span class="intro-circle intro-circle--small">market moves.</span>'
))
</script>

<style scoped>
.intro-shell {
  position: relative;
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.intro-shell--visible {
  opacity: 1;
  transform: translateY(0);
}

.intro-kicker {
  margin-bottom: 18px;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 18px;
  font-weight: 400;
  line-height: 1.1;
}

.intro-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(260px, 0.85fr);
  gap: 38px;
  align-items: start;
}

.intro-title {
  margin: 0;
  color: #050505;
  font-family: var(--murmur-font-display);
  font-size: clamp(42px, 6vw, 72px);
  font-weight: 800;
  line-height: 0.94;
  letter-spacing: -0.035em;
  text-wrap: balance;
}

.intro-copy {
  padding-top: 10px;
}

.intro-summary,
.intro-detail {
  margin: 0;
  color: #050505;
}

.intro-summary {
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 24px;
  line-height: 1.28;
}

.intro-detail {
  font-family: var(--murmur-font-ui);
  margin-top: 20px;
  font-size: 17px;
  line-height: 1.5;
}

.intro-proof {
  margin-top: 34px;
  padding-top: 18px;
  border-top: 1px solid rgba(5, 5, 5, 0.12);
}

.intro-proof__rail {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 18px;
  align-items: center;
}

.intro-proof__item {
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.intro-proof__item:not(:last-child)::after {
  content: '';
  display: inline-block;
  width: 34px;
  margin-left: 18px;
  vertical-align: middle;
  border-bottom: 1px solid rgba(5, 5, 5, 0.2);
}

.intro-proof__line {
  max-width: 760px;
  margin: 18px 0 0;
  color: #050505;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 18px;
  line-height: 1.36;
}

.intro-proof__note {
  margin-top: 18px;
  color: #0048ff;
  font-family: var(--murmur-font-hand);
  font-size: 24px;
  line-height: 0.84;
  text-align: right;
}

:deep(.intro-underline),
:deep(.intro-circle) {
  position: relative;
  display: inline-block;
}

:deep(.intro-underline::after) {
  content: '';
  position: absolute;
  left: -0.08em;
  right: -0.08em;
  bottom: -0.08em;
  border-bottom: 3px solid #0048ff;
  border-radius: 999px;
  transform: rotate(-1.5deg);
  pointer-events: none;
}

:deep(.intro-underline--tight::after) {
  left: -0.04em;
  right: -0.04em;
  bottom: -0.05em;
}

:deep(.intro-underline--summary::after) {
  bottom: -0.09em;
}

:deep(.intro-circle::before),
:deep(.intro-circle::after) {
  content: '';
  position: absolute;
  pointer-events: none;
  border-radius: 999px;
}

:deep(.intro-circle::before) {
  inset: -0.12em -0.18em -0.06em -0.18em;
  border: 2px solid rgba(0, 72, 255, 0.9);
  transform: rotate(-5deg);
}

:deep(.intro-circle::after) {
  inset: -0.06em -0.12em -0.12em -0.14em;
  border: 2px solid rgba(0, 72, 255, 0.7);
  transform: rotate(4deg);
}

:deep(.intro-circle--small::before) {
  inset: -0.12em -0.18em -0.08em -0.18em;
}

:deep(.intro-circle--small::after) {
  inset: -0.07em -0.14em -0.12em -0.14em;
}

@media (max-width: 900px) {
  .intro-grid {
    grid-template-columns: 1fr;
    gap: 18px;
  }

  .intro-copy {
    padding-top: 0;
  }

  .intro-summary {
    font-size: 21px;
  }

  .intro-detail {
    font-size: 16px;
  }

  .intro-proof {
    margin-top: 28px;
  }

  .intro-proof__rail {
    gap: 10px 14px;
  }

  .intro-proof__item {
    font-size: 11px;
  }

  .intro-proof__item:not(:last-child)::after {
    width: 24px;
    margin-left: 14px;
  }

  .intro-proof__line {
    font-size: 16px;
  }

  .intro-proof__note {
    font-size: 21px;
    text-align: left;
  }

}
</style>
