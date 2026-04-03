<template>
  <section ref="targetRef" class="scenario-shell" :class="{ 'scenario-shell--visible': isVisible }">
    <div class="section-label">Run a scenario</div>
    <form class="scenario-form" @submit.prevent="handleSubmit">
      <textarea
        v-model.trim="scenario"
        class="scenario-input"
        rows="3"
        :placeholder="placeholder"
      />
      <button class="scenario-button" type="submit">Run scenario -&gt;</button>
    </form>
    <button class="scenario-link" type="button" @click="$emit('request-access')">
      Or request full platform access for your team -&gt;
    </button>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

const emit = defineEmits(['submit', 'request-access'])

const placeholder = "Tell us what you're about to announce. We'll show you what happens next."
const scenario = ref('')
const { targetRef, isVisible } = useRevealOnScroll()

const handleSubmit = () => {
  if (!scenario.value) {
    return
  }

  const value = scenario.value
  scenario.value = ''
  emit('submit', value)
}
</script>

<style scoped>
.scenario-shell {
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.scenario-shell--visible {
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

.scenario-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.scenario-input {
  width: 100%;
  border: 1px solid var(--murmur-border);
  background: var(--murmur-bg-input);
  color: var(--murmur-text-heading);
  padding: 22px 20px;
  resize: vertical;
  min-height: 110px;
  line-height: 1.7;
}

.scenario-input:focus {
  outline: none;
  border-color: rgba(192, 57, 43, 0.5);
  box-shadow: 0 0 0 4px rgba(192, 57, 43, 0.12);
}

.scenario-button,
.scenario-link {
  align-self: flex-start;
  background: transparent;
  cursor: pointer;
}

.scenario-button {
  border: none;
  color: var(--murmur-text-heading);
  padding: 12px 0;
  font-family: var(--murmur-font-mono);
  font-size: 13px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.scenario-link {
  margin-top: 16px;
  border: none;
  padding: 0;
  color: var(--murmur-link);
  font-size: 16px;
}
</style>
