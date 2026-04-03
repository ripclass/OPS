<template>
  <footer ref="targetRef" class="footer-shell" :class="{ 'footer-shell--visible': isVisible }">
    <div class="footer-label">FROM HERE</div>

    <div class="footer-top">
      <div class="footer-brand">
        <h2 class="footer-brand__word">MURMUR</h2>
        <p class="footer-brand__line">{{ lines[3] }}</p>
      </div>

      <div class="footer-copy">
        <p v-for="(line, index) in primaryLines" :key="index">{{ line }}</p>
      </div>
    </div>

    <div class="footer-scribble">built in Dhaka / not pointed at us</div>

    <nav class="footer-links" aria-label="Footer">
      <a href="#about">About</a>
      <a href="mailto:hello@murmur.app">Contact</a>
      <a href="#research">Research</a>
      <a href="#privacy">Privacy</a>
    </nav>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

const props = defineProps({
  lines: {
    type: Array,
    required: true,
  },
})

const { targetRef, isVisible } = useRevealOnScroll()

const primaryLines = computed(() => props.lines.slice(0, 3))
</script>

<style scoped>
.footer-shell {
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 0.6s ease, transform 0.6s ease;
  padding-bottom: 72px;
}

.footer-shell--visible {
  opacity: 1;
  transform: translateY(0);
}

.footer-label {
  margin-bottom: 20px;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.footer-top {
  display: grid;
  grid-template-columns: minmax(260px, 0.8fr) minmax(0, 1.08fr);
  gap: 40px;
  align-items: start;
}

.footer-brand__word {
  margin: 0;
  color: #050505;
  font-family: var(--murmur-font-display);
  font-size: clamp(40px, 5.4vw, 72px);
  font-weight: 800;
  line-height: 0.94;
  letter-spacing: -0.035em;
}

.footer-brand__line {
  max-width: 320px;
  margin: 18px 0 0;
  color: #050505;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 20px;
  line-height: 1.28;
}

.footer-copy {
  display: grid;
  gap: 14px;
}

.footer-copy p {
  margin: 0;
  color: #050505;
  font-family: var(--murmur-font-ui);
  font-size: 22px;
  line-height: 1.42;
}

.footer-scribble {
  margin: 30px 0 0;
  color: #0048ff;
  font-family: var(--murmur-font-hand);
  font-size: 28px;
  line-height: 0.82;
  text-align: right;
  transform: rotate(-2deg);
}

.footer-links {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid rgba(5, 5, 5, 0.12);
}

.footer-links a {
  color: #5a7692;
  text-decoration: none;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 16px;
}

@media (max-width: 960px) {
  .footer-top {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}

@media (max-width: 640px) {
  .footer-brand__line,
  .footer-links a {
    font-size: 16px;
  }

  .footer-copy p {
    font-size: 18px;
  }

  .footer-scribble {
    text-align: left;
    font-size: 22px;
  }
}
</style>
