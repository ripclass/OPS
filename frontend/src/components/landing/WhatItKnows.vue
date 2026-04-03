<template>
  <section ref="targetRef" class="knowledge-shell" :class="{ 'knowledge-shell--visible': isVisible }">
    <div class="knowledge-label">WHAT IT KNOWS</div>

    <div class="knowledge-top">
      <h2 class="knowledge-title" v-html="decoratedTitle" />

      <div class="knowledge-standfirst">
        <p class="knowledge-standfirst__lead" v-html="decoratedLead" />
        <p class="knowledge-standfirst__detail" v-html="decoratedDetail" />
      </div>
    </div>

    <div class="knowledge-scribble">where most models start lying</div>

    <div class="knowledge-list">
      <article
        v-for="entry in knowledgeEntries"
        :key="entry.index"
        class="knowledge-item"
      >
        <div class="knowledge-item__meta">
          <div class="knowledge-item__index">{{ entry.index }}</div>
          <div class="knowledge-item__label">{{ entry.label }}</div>
        </div>
        <p class="knowledge-item__text">{{ entry.text }}</p>
      </article>
    </div>

    <p class="knowledge-close" v-html="decoratedClose" />
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

const props = defineProps({
  items: {
    type: Array,
    required: true,
  },
})

const { targetRef, isVisible } = useRevealOnScroll()

const labels = [
  'Chittagong EPZ / migrant women',
  'Rangpur / health trust economy',
  'Noakhali / remittance households',
  'Dhaka and district youth / not one public',
  'Barisal to Gazipur / price shock math',
]

const decorate = (text, target, replacement) => text.replace(target, replacement)

const decoratedTitle = computed(() => decorate(
  'It knows the people other systems erase.',
  'people',
  '<span class="knowledge-circle">people</span>'
))

const decoratedLead = computed(() => decorate(
  'The difference between realism and fiction is whether the model knows who actually carries the cost.',
  'carries the cost',
  '<span class="knowledge-underline">carries the cost</span>'
))

const decoratedDetail = computed(() => decorate(
  'Not averages. Not generic users. Social position, silence, and pressure in the right proportions.',
  'Not generic users',
  '<span class="knowledge-circle knowledge-circle--small">Not generic users</span>'
))

const decoratedClose = computed(() => decorate(
  'We know these people because we are from here.',
  'from here',
  '<span class="knowledge-underline knowledge-underline--tight">from here</span>'
))

const knowledgeEntries = computed(() => props.items.map((text, index) => ({
  index: String(index + 1).padStart(2, '0'),
  label: labels[index] || `Field note ${index + 1}`,
  text,
})))
</script>

<style scoped>
.knowledge-shell {
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.knowledge-shell--visible {
  opacity: 1;
  transform: translateY(0);
}

.knowledge-label {
  margin-bottom: 20px;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.knowledge-top {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(260px, 0.78fr);
  gap: 36px;
  align-items: start;
}

.knowledge-title {
  margin: 0;
  color: #050505;
  font-family: var(--murmur-font-display);
  font-size: clamp(40px, 5.4vw, 68px);
  font-weight: 800;
  line-height: 0.95;
  letter-spacing: -0.035em;
  text-wrap: balance;
}

.knowledge-standfirst {
  padding-top: 8px;
}

.knowledge-standfirst__lead,
.knowledge-standfirst__detail {
  margin: 0;
  color: #050505;
}

.knowledge-standfirst__lead {
  font-family: var(--murmur-font-ui);
  font-size: 22px;
  line-height: 1.36;
}

.knowledge-standfirst__detail {
  margin-top: 18px;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 18px;
  line-height: 1.24;
}

.knowledge-scribble {
  margin: 28px 0 0;
  color: #0048ff;
  font-family: var(--murmur-font-hand);
  font-size: 28px;
  line-height: 0.82;
  text-align: right;
  transform: rotate(-2deg);
}

.knowledge-list {
  display: grid;
  gap: 18px;
  margin-top: 30px;
  padding-top: 26px;
  border-top: 1px solid rgba(5, 5, 5, 0.12);
}

.knowledge-item {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  gap: 26px;
  align-items: start;
  padding: 18px 0;
  border-top: 1px solid rgba(5, 5, 5, 0.08);
}

.knowledge-item:first-child {
  border-top: none;
}

.knowledge-item__meta {
  display: grid;
  gap: 8px;
}

.knowledge-item__index {
  color: #0048ff;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 18px;
  line-height: 1;
}

.knowledge-item__label {
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 14px;
  font-weight: 900;
  letter-spacing: 0.09em;
  line-height: 1.15;
  text-transform: uppercase;
}

.knowledge-item__text {
  margin: 0;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 21px;
  line-height: 1.48;
}

.knowledge-close {
  max-width: 820px;
  margin: 38px 0 0;
  color: #050505;
  font-family: var(--murmur-font-display);
  font-size: clamp(28px, 3.6vw, 44px);
  font-weight: 700;
  line-height: 1.08;
}

:deep(.knowledge-underline),
:deep(.knowledge-circle) {
  position: relative;
  display: inline-block;
}

:deep(.knowledge-underline::after) {
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

:deep(.knowledge-underline--tight::after) {
  left: -0.04em;
  right: -0.04em;
  bottom: -0.05em;
}

:deep(.knowledge-circle::before),
:deep(.knowledge-circle::after) {
  content: '';
  position: absolute;
  pointer-events: none;
  border-radius: 999px;
}

:deep(.knowledge-circle::before) {
  inset: -0.16em -0.18em -0.1em -0.18em;
  border: 2px solid rgba(0, 72, 255, 0.9);
  transform: rotate(-5deg);
}

:deep(.knowledge-circle::after) {
  inset: -0.08em -0.12em -0.16em -0.14em;
  border: 2px solid rgba(0, 72, 255, 0.72);
  transform: rotate(4deg);
}

:deep(.knowledge-circle--small::before) {
  inset: -0.12em -0.16em -0.08em -0.16em;
}

:deep(.knowledge-circle--small::after) {
  inset: -0.08em -0.12em -0.12em -0.12em;
}

@media (max-width: 960px) {
  .knowledge-top {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .knowledge-standfirst {
    padding-top: 0;
  }

  .knowledge-item {
    grid-template-columns: 1fr;
    gap: 14px;
  }
}

@media (max-width: 640px) {
  .knowledge-standfirst__lead {
    font-size: 18px;
  }

  .knowledge-standfirst__detail,
  .knowledge-item__index {
    font-size: 16px;
  }

  .knowledge-item__text {
    font-size: 18px;
  }

  .knowledge-scribble {
    text-align: left;
    font-size: 22px;
  }
}
</style>
