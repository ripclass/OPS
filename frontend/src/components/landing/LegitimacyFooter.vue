<template>
  <footer ref="targetRef" class="footer-shell" :class="{ 'footer-shell--visible': isVisible }">
    <div class="footer-copy">
      <p v-for="(line, index) in lines" :key="index">{{ line }}</p>
    </div>
    <nav class="footer-links" aria-label="Footer">
      <a href="#about">About</a>
      <a href="mailto:hello@murmur.app">Contact</a>
      <a href="#research">Research</a>
      <a href="#privacy">Privacy</a>
    </nav>
  </footer>
</template>

<script setup>
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

defineProps({
  lines: {
    type: Array,
    required: true,
  },
})

const { targetRef, isVisible } = useRevealOnScroll()
</script>

<style scoped>
.footer-shell {
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 0.6s ease, transform 0.6s ease;
  padding-bottom: 64px;
}

.footer-shell--visible {
  opacity: 1;
  transform: translateY(0);
}

.footer-copy {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.footer-copy p {
  margin: 0;
  color: var(--murmur-text-primary);
  font-size: 18px;
  line-height: 1.8;
}

.footer-links {
  display: flex;
  gap: 18px;
  flex-wrap: wrap;
  margin-top: 28px;
}

.footer-links a {
  color: var(--murmur-link);
  text-decoration: none;
  font-size: 15px;
}
</style>
