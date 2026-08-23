<template>
  <footer ref="targetRef" class="footer-shell" :class="{ 'footer-shell--visible': isVisible }">
    <div class="footer-label">ABOUT</div>

    <div class="footer-top">
      <div class="footer-brand">
        <h2 class="footer-brand__word">MURMUR</h2>
        <p class="footer-brand__line">{{ punch }}</p>
      </div>

      <div class="footer-copy">
        <p v-for="(line, index) in lines" :key="index">{{ line }}</p>
      </div>
    </div>

    <p class="footer-pullquote">
      {{ pullquote.before }}<span class="footer-pullquote__mark">{{ pullquote.emphasis }}</span>{{ pullquote.after }}
    </p>

    <div class="footer-scribble">built inside south asia / not pointed at it</div>

    <nav class="footer-links" aria-label="Footer">
      <a href="#about-us">About</a>
      <a href="#research">Research</a>
      <a href="#privacy">Privacy</a>
    </nav>
  </footer>
</template>

<script setup>
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

defineProps({
  punch: {
    type: String,
    required: true,
  },
  lines: {
    type: Array,
    required: true,
  },
  pullquote: {
    type: Object,
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
  font-size: 20px;
  line-height: 1.45;
}

.footer-pullquote {
  max-width: 820px;
  margin: 40px 0 0;
  padding-top: 24px;
  border-top: 1px solid rgba(5, 5, 5, 0.12);
  color: #050505;
  font-family: 'Mom´sTypewriter', var(--murmur-font-type);
  font-size: 24px;
  line-height: 1.32;
}

.footer-pullquote__mark {
  position: relative;
  display: inline-block;
}

.footer-pullquote__mark::after {
  content: '';
  position: absolute;
  left: -0.04em;
  right: -0.04em;
  bottom: -0.1em;
  border-bottom: 3px solid #0048ff;
  border-radius: 999px;
  transform: rotate(-1.2deg);
  pointer-events: none;
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
  .footer-shell {
    padding-bottom: 48px;
  }

  .footer-brand__line,
  .footer-links a {
    font-size: 16px;
  }

  .footer-brand__line {
    max-width: none;
    margin-top: 14px;
  }

  .footer-copy p {
    font-size: 17px;
  }

  .footer-pullquote {
    margin-top: 30px;
    padding-top: 20px;
    font-size: 19px;
  }

  .footer-scribble {
    text-align: left;
    font-size: 22px;
  }

  /* Three links on one 343px row left no space between the tap targets. */
  .footer-links {
    gap: 14px 22px;
    margin-top: 26px;
  }

  .footer-links a {
    padding: 6px 0;
  }
}
</style>
