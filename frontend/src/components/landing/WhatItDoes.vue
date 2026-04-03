<template>
  <section ref="targetRef" class="prose-shell" :class="{ 'prose-shell--visible': isVisible }">
    <div class="section-label">What it does</div>
    <div class="prose-copy">
      <p v-for="(paragraph, index) in paragraphs" :key="index">{{ paragraph }}</p>
    </div>
  </section>
</template>

<script setup>
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

defineProps({
  paragraphs: {
    type: Array,
    required: true,
  },
})

const { targetRef, isVisible } = useRevealOnScroll()
</script>

<style scoped>
.prose-shell {
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.prose-shell--visible {
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

.prose-copy {
  display: flex;
  flex-direction: column;
  gap: 26px;
}

.prose-copy p {
  margin: 0;
  color: var(--murmur-text-primary);
  font-size: 21px;
  line-height: 1.82;
}

@media (max-width: 640px) {
  .prose-copy p {
    font-size: 18px;
  }
}
</style>
