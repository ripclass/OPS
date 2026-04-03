<template>
  <section ref="targetRef" class="intro-shell" :class="{ 'intro-shell--visible': isVisible }">
    <div class="intro-kicker">{{ kicker }}</div>

    <div class="intro-grid">
      <div class="intro-lead">
        <h2 class="intro-title">{{ title }}</h2>
      </div>

      <div class="intro-copy">
        <p class="intro-summary">{{ summary }}</p>
        <p class="intro-detail">{{ detail }}</p>
      </div>
    </div>

    <div class="intro-note">THIS IS WHAT MURMUR IS.</div>
  </section>
</template>

<script setup>
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

defineProps({
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

.intro-note {
  margin-top: 28px;
  color: #050505;
  font-family: var(--murmur-font-display);
  font-size: 34px;
  font-weight: 800;
  line-height: 0.9;
  letter-spacing: -0.02em;
  text-align: right;
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

  .intro-note {
    text-align: left;
  }
}
</style>
