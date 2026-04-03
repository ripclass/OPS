<template>
  <section ref="targetRef" class="audience-shell" :class="{ 'audience-shell--visible': isVisible }">
    <div class="audience-label">WHO IT'S FOR</div>

    <div class="audience-top">
      <h2 class="audience-title" v-html="decoratedTitle" />

      <div class="audience-intro">
        <p class="audience-intro__lead" v-html="decoratedLead" />
        <p class="audience-intro__detail">{{ intro[1] }}</p>
      </div>
    </div>

    <div class="audience-figure-block">
      <div class="audience-figure-stage">
        <div class="audience-note">HIGH\nCONSEQ\nUENCE\nDECISI\nONS</div>
        <figure class="audience-figure" aria-label="Who it's for illustration">
          <img src="/landing/WhoIsItFor.webp" alt="" />
        </figure>
      </div>
    </div>

    <div class="audience-cases">
      <article
        v-for="(line, index) in lines"
        :key="line"
        class="audience-case"
      >
        <div class="audience-case__index">{{ String(index + 1).padStart(2, '0') }}</div>
        <p class="audience-case__text">{{ line }}</p>
      </article>
    </div>

    <p class="audience-outro" v-html="decoratedOutro" />
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

const props = defineProps({
  intro: {
    type: Array,
    required: true,
  },
  lines: {
    type: Array,
    required: true,
  },
  outro: {
    type: String,
    required: true,
  },
})

const { targetRef, isVisible } = useRevealOnScroll()

const decorate = (text, target, replacement) => text.replace(target, replacement)

const decoratedTitle = computed(() => decorate(
  'For decisions that do not stay on paper.',
  'on paper',
  '<span class="audience-circle">on paper</span>'
))

const decoratedLead = computed(() => decorate(
  decorate(
    props.intro[0] || '',
    'millions',
    '<span class="audience-circle audience-circle--small">millions</span>'
  ),
  'silence you cannot measure',
  '<span class="audience-underline audience-underline--tight">silence you cannot measure</span>'
))

const decoratedOutro = computed(() => decorate(
  props.outro,
  'the rehearsal',
  '<span class="audience-circle">the rehearsal</span>'
))
</script>

<style scoped>
.audience-shell {
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.audience-shell--visible {
  opacity: 1;
  transform: translateY(0);
}

.audience-label {
  margin-bottom: 20px;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.audience-top {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(260px, 0.78fr);
  gap: 36px;
  align-items: start;
}

.audience-title {
  margin: 0;
  color: #050505;
  font-family: var(--murmur-font-display);
  font-size: clamp(40px, 5.4vw, 68px);
  font-weight: 800;
  line-height: 0.95;
  letter-spacing: -0.035em;
  text-wrap: balance;
}

.audience-intro {
  padding-top: 10px;
}

.audience-figure-block {
  margin-top: 46px;
}

.audience-figure-stage {
  position: relative;
  width: min(100%, 760px);
  margin: 0 auto;
  min-height: 560px;
}

.audience-figure {
  margin: 0;
  position: absolute;
  left: 50%;
  top: 18px;
  z-index: 2;
  display: flex;
  justify-content: center;
  transform: translateX(-50%);
}

.audience-figure img {
  display: block;
  width: min(100%, 560px);
  height: auto;
}

.audience-intro__lead,
.audience-intro__detail {
  margin: 0;
  color: #050505;
}

.audience-intro__lead {
  font-family: var(--murmur-font-ui);
  font-size: 21px;
  line-height: 1.45;
}

.audience-intro__detail {
  margin-top: 18px;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 18px;
  line-height: 1.24;
}

.audience-cases {
  position: relative;
  margin-top: 30px;
  padding-top: 24px;
  border-top: 1px solid rgba(5, 5, 5, 0.12);
}

.audience-note {
  position: absolute;
  left: 8px;
  top: 54px;
  z-index: 1;
  color: #0048ff;
  font-family: var(--murmur-font-hand);
  font-size: clamp(62px, 8.3vw, 88px);
  line-height: 0.82;
  text-align: left;
  transform: rotate(-3deg);
  white-space: pre-line;
}

.audience-case {
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr);
  gap: 18px;
  align-items: start;
  padding: 18px 0;
  border-top: 1px solid rgba(5, 5, 5, 0.08);
}

.audience-case:first-of-type {
  border-top: none;
}

.audience-case__index {
  color: #0048ff;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 18px;
  line-height: 1;
  padding-top: 3px;
}

.audience-case__text {
  margin: 0;
  color: #050505;
  font-family: var(--murmur-font-display);
  font-size: 31px;
  font-weight: 700;
  line-height: 1.18;
}

.audience-outro {
  max-width: 760px;
  margin: 34px 0 0;
  color: #050505;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 22px;
  line-height: 1.3;
}

:deep(.audience-underline),
:deep(.audience-circle) {
  position: relative;
  display: inline-block;
}

:deep(.audience-underline::after) {
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

:deep(.audience-underline--tight::after) {
  left: -0.04em;
  right: -0.04em;
  bottom: -0.05em;
}

:deep(.audience-circle::before),
:deep(.audience-circle::after) {
  content: '';
  position: absolute;
  pointer-events: none;
  border-radius: 999px;
}

:deep(.audience-circle::before) {
  inset: -0.16em -0.18em -0.1em -0.18em;
  border: 2px solid rgba(0, 72, 255, 0.9);
  transform: rotate(-5deg);
}

:deep(.audience-circle::after) {
  inset: -0.08em -0.12em -0.16em -0.14em;
  border: 2px solid rgba(0, 72, 255, 0.72);
  transform: rotate(4deg);
}

:deep(.audience-circle--small::before) {
  inset: -0.12em -0.16em -0.08em -0.16em;
}

:deep(.audience-circle--small::after) {
  inset: -0.08em -0.12em -0.12em -0.12em;
}

@media (max-width: 960px) {
  .audience-top {
    grid-template-columns: 1fr;
    gap: 22px;
  }

  .audience-figure-block {
    margin-top: 34px;
  }

  .audience-figure-stage {
    min-height: 460px;
  }

  .audience-figure {
    top: 26px;
  }

  .audience-figure img {
    width: min(100%, 460px);
  }

  .audience-intro {
    padding-top: 0;
  }
}

@media (max-width: 640px) {
  .audience-intro__lead {
    font-size: 18px;
  }

  .audience-intro__detail,
  .audience-outro,
  .audience-case__index {
    font-size: 16px;
  }

  .audience-case {
    grid-template-columns: 32px minmax(0, 1fr);
    gap: 14px;
  }

  .audience-case__text {
    font-size: 24px;
  }

  .audience-note {
    top: 22px;
    left: 0;
    font-size: clamp(42px, 13vw, 64px);
  }
}
</style>
