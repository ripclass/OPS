<template>
  <section ref="targetRef" class="library-shell" :class="{ 'library-shell--visible': isVisible }">
    <div class="library-label">SCENARIO LIBRARY</div>

    <div class="library-top">
      <h2 class="library-title" v-html="decoratedTitle" />

      <div class="library-standfirst">
        <p class="library-standfirst__lead" v-html="decoratedLead" />
        <p class="library-standfirst__detail">{{ intro.detail }}</p>
      </div>
    </div>

    <div class="library-scribble">{{ intro.scribble }}</div>

    <div class="library-grid">
      <button
        v-for="(item, index) in items"
        :key="item.countryCode"
        class="library-card"
        type="button"
        @click="$emit('select', item.countryCode)"
      >
        <span class="library-card__meta">
          <span class="library-card__index">{{ String(index + 1).padStart(2, '0') }}</span>
          <span class="library-card__sector">{{ item.sector }}</span>
        </span>

        <span class="library-card__title">{{ item.title }}</span>
        <span class="library-card__place">{{ item.place }}</span>

        <span class="library-card__quiet-label">Who goes quiet</span>
        <span class="library-card__quiet">{{ item.quiet }}</span>

        <span class="library-card__run">
          <span>Run this rehearsal</span>
          <span class="library-card__arrow">-&gt;</span>
        </span>
      </button>
    </div>

    <p class="library-close" v-html="decoratedClose" />
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

const props = defineProps({
  intro: {
    type: Object,
    required: true,
  },
  items: {
    type: Array,
    required: true,
  },
})

defineEmits(['select'])

const { targetRef, isVisible } = useRevealOnScroll()

const decorate = (text, target, replacement) => text.replace(target, replacement)

const decoratedTitle = computed(() => decorate(
  props.intro.title,
  'rehearsals',
  '<span class="library-circle">rehearsals</span>'
))

const decoratedLead = computed(() => decorate(
  props.intro.lead,
  'in a different way',
  '<span class="library-underline">in a different way</span>'
))

const decoratedClose = computed(() => decorate(
  props.intro.close,
  'Write the brief below',
  '<span class="library-underline library-underline--tight">Write the brief below</span>'
))
</script>

<style scoped>
.library-shell {
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.library-shell--visible {
  opacity: 1;
  transform: translateY(0);
}

.library-label {
  margin-bottom: 20px;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.library-top {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(260px, 0.78fr);
  gap: 36px;
  align-items: start;
}

.library-title {
  margin: 0;
  color: #050505;
  font-family: var(--murmur-font-display);
  font-size: clamp(40px, 5.4vw, 68px);
  font-weight: 800;
  line-height: 0.95;
  letter-spacing: -0.035em;
  text-wrap: balance;
}

.library-standfirst {
  padding-top: 8px;
}

.library-standfirst__lead,
.library-standfirst__detail {
  margin: 0;
  color: #050505;
}

.library-standfirst__lead {
  font-family: var(--murmur-font-ui);
  font-size: 21px;
  line-height: 1.4;
}

.library-standfirst__detail {
  margin-top: 18px;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 15px;
  line-height: 1.34;
}

.library-scribble {
  margin: 26px 0 0;
  color: #0048ff;
  font-family: var(--murmur-font-hand);
  font-size: 28px;
  line-height: 0.82;
  text-align: right;
  transform: rotate(-2deg);
}

.library-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 30px;
  padding-top: 26px;
  border-top: 1px solid rgba(5, 5, 5, 0.12);
}

/* The first scenario is the one the hero already told, so it opens the grid
   full width. It also makes an odd count of seven sit square. */
.library-grid > .library-card:first-child {
  grid-column: 1 / -1;
}

.library-card {
  display: grid;
  gap: 0;
  align-content: start;
  width: 100%;
  margin: 0;
  padding: 22px 22px 20px;
  border: 1px solid rgba(5, 5, 5, 0.18);
  background: #fff;
  color: #050505;
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.18s ease;
}

.library-card:hover,
.library-card:focus-visible {
  border-color: #0048ff;
  outline: none;
}

.library-card__meta {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 12px;
}

.library-card__index,
.library-card__sector {
  color: #0048ff;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  line-height: 1;
}

.library-card__index {
  font-size: 18px;
}

.library-card__sector {
  font-size: 14px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.library-card__title {
  color: #050505;
  font-family: var(--murmur-font-display);
  font-size: 27px;
  font-weight: 800;
  line-height: 1.04;
  letter-spacing: -0.02em;
}

.library-grid > .library-card:first-child .library-card__title {
  font-size: 36px;
}

.library-card__place {
  margin-top: 7px;
  color: #6d6d6d;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 13px;
  line-height: 1.32;
}

.library-card__quiet-label {
  margin-top: 18px;
  padding-top: 14px;
  border-top: 1px solid rgba(5, 5, 5, 0.1);
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.library-card__quiet {
  margin-top: 8px;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 16px;
  line-height: 1.44;
}

.library-card__run {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 18px;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  transition: color 0.18s ease;
}

.library-card__arrow {
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 15px;
  letter-spacing: 0;
  white-space: nowrap;
}

.library-card:hover .library-card__run,
.library-card:focus-visible .library-card__run {
  color: #0048ff;
}

.library-close {
  max-width: 820px;
  margin: 34px 0 0;
  color: #050505;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 22px;
  line-height: 1.3;
}

:deep(.library-underline),
:deep(.library-circle) {
  position: relative;
  display: inline-block;
}

:deep(.library-underline::after) {
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

:deep(.library-underline--tight::after) {
  left: -0.04em;
  right: -0.04em;
  bottom: -0.05em;
  border-bottom-width: 3px;
}

:deep(.library-circle::before),
:deep(.library-circle::after) {
  content: '';
  position: absolute;
  pointer-events: none;
  border-radius: 999px;
}

:deep(.library-circle::before) {
  inset: -0.16em -0.18em -0.1em -0.18em;
  border: 2px solid rgba(0, 72, 255, 0.9);
  transform: rotate(-5deg);
}

:deep(.library-circle::after) {
  inset: -0.08em -0.12em -0.16em -0.14em;
  border: 2px solid rgba(0, 72, 255, 0.72);
  transform: rotate(4deg);
}

@media (max-width: 960px) {
  .library-top {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .library-standfirst {
    padding-top: 0;
  }

  .library-grid {
    grid-template-columns: 1fr;
  }

  .library-grid > .library-card:first-child {
    grid-column: auto;
  }

  .library-grid > .library-card:first-child .library-card__title {
    font-size: 30px;
  }
}

@media (max-width: 640px) {
  .library-standfirst__lead {
    font-size: 18px;
  }

  .library-standfirst__detail {
    font-size: 14px;
  }

  .library-scribble {
    text-align: left;
    font-size: 22px;
  }

  .library-grid {
    margin-top: 24px;
    padding-top: 20px;
    gap: 12px;
  }

  .library-card {
    padding: 18px 16px 16px;
  }

  .library-card__title,
  .library-grid > .library-card:first-child .library-card__title {
    font-size: 24px;
  }

  .library-card__quiet {
    font-size: 15px;
  }

  /* A whole card is the tap target, so the run line only has to stay legible
     and stay on one line. */
  .library-card__run {
    margin-top: 16px;
    font-size: 11px;
  }

  .library-close {
    font-size: 17px;
  }
}
</style>
