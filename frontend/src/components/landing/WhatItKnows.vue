<template>
  <section ref="targetRef" class="knowledge-shell" :class="{ 'knowledge-shell--visible': isVisible }">
    <div class="section-label">What it knows</div>
    <div class="knowledge-list">
      <article v-for="(item, index) in items" :key="index" class="knowledge-item">
        <div class="knowledge-item__index">{{ String(index + 1).padStart(2, '0') }}</div>
        <p class="knowledge-item__text">{{ item }}</p>
      </article>
    </div>
    <p class="knowledge-close">We know these people because we are from where they are from.</p>
  </section>
</template>

<script setup>
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

defineProps({
  items: {
    type: Array,
    required: true,
  },
})

const { targetRef, isVisible } = useRevealOnScroll()
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

.section-label {
  margin-bottom: 26px;
  color: var(--murmur-text-muted);
  font-family: var(--murmur-font-mono);
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 34px;
}

.knowledge-item {
  display: grid;
  grid-template-columns: 56px minmax(0, 1fr);
  gap: 12px;
}

.knowledge-item__index {
  color: var(--murmur-text-muted);
  font-family: var(--murmur-font-mono);
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  padding-top: 5px;
}

.knowledge-item__text {
  margin: 0;
  color: var(--murmur-text-primary);
  font-size: 20px;
  line-height: 1.8;
}

.knowledge-close {
  margin: 42px 0 0;
  color: var(--murmur-text-heading);
  font-family: var(--murmur-font-serif);
  font-size: 30px;
  line-height: 1.45;
}

@media (max-width: 640px) {
  .knowledge-item {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .knowledge-item__text {
    font-size: 18px;
  }

  .knowledge-close {
    font-size: 24px;
  }
}
</style>
