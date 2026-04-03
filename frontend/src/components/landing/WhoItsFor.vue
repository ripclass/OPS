<template>
  <section ref="targetRef" class="audience-shell" :class="{ 'audience-shell--visible': isVisible }">
    <div class="section-label">Who it's for</div>
    <div class="audience-copy">
      <p v-for="(paragraph, index) in intro" :key="`intro-${index}`">{{ paragraph }}</p>
    </div>
    <div class="audience-lines">
      <p v-for="(line, index) in lines" :key="index" class="audience-line">{{ line }}</p>
    </div>
    <p class="audience-outro">{{ outro }}</p>
  </section>
</template>

<script setup>
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

defineProps({
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

.section-label {
  margin-bottom: 26px;
  color: var(--murmur-text-muted);
  font-family: var(--murmur-font-mono);
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.audience-copy,
.audience-lines {
  display: flex;
  flex-direction: column;
}

.audience-copy {
  gap: 22px;
}

.audience-copy p,
.audience-outro {
  margin: 0;
  color: var(--murmur-text-primary);
  font-size: 21px;
  line-height: 1.82;
}

.audience-lines {
  gap: 22px;
  margin: 44px 0;
}

.audience-line {
  margin: 0;
  color: var(--murmur-text-heading);
  font-family: var(--murmur-font-serif);
  font-size: 33px;
  line-height: 1.45;
}

@media (max-width: 640px) {
  .audience-copy p,
  .audience-outro {
    font-size: 18px;
  }

  .audience-line {
    font-size: 25px;
  }
}
</style>
