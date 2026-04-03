<template>
  <Transition name="story-shell" mode="out-in">
    <article :key="story.key" class="agent-story">
      <div class="agent-story__media">
        <div class="agent-story__frame">
          <img
            v-if="showImage"
            class="agent-story__image"
            :src="story.imagePath"
            :alt="story.imageAlt || story.headlineName"
            @error="handleImageError"
          />
          <div v-else class="agent-story__placeholder">
            <div class="agent-story__placeholder-note">{{ placeholderNote }}</div>
            <div v-if="placeholderPath" class="agent-story__placeholder-path">{{ placeholderPath }}</div>
          </div>
        </div>
      </div>

      <div class="agent-story__copy">
        <div class="agent-story__label">
          <span v-if="globalMode">South Asia opening story</span>
          <span v-else>{{ story.code }} opening story</span>
        </div>

        <header class="agent-story__headline">
          <h1 class="agent-story__headline-name">{{ story.headlineName }}</h1>
          <p class="agent-story__headline-meta">{{ story.headlineMeta }}</p>
        </header>

        <div class="agent-story__body">
          <p
            v-for="(line, index) in story.bodyLines"
            :key="`${story.key}-${index}`"
            class="agent-story__line"
          >
            <span>{{ typedLines[index] }}</span>
            <span v-if="index === activeLine && typedLines[index] !== line" class="agent-story__cursor">|</span>
          </p>
        </div>
      </div>
    </article>
  </Transition>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps({
  story: {
    type: Object,
    required: true,
  },
  globalMode: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['complete'])

const typedLines = ref([])
const activeLine = ref(-1)
const imageFailed = ref(false)
let timers = []

const clearTimers = () => {
  timers.forEach(timer => window.clearTimeout(timer))
  timers = []
}

const resetTypingState = () => {
  typedLines.value = props.story.bodyLines.map(() => '')
  activeLine.value = -1
}

const completeInstantly = () => {
  typedLines.value = [...props.story.bodyLines]
  activeLine.value = -1
  emit('complete', props.story.key)
}

const queueTimeout = (callback, delay) => {
  const timer = window.setTimeout(callback, delay)
  timers.push(timer)
}

const typeLine = (lineIndex, charIndex = 0) => {
  if (lineIndex >= props.story.bodyLines.length) {
    activeLine.value = -1
    queueTimeout(() => emit('complete', props.story.key), 450)
    return
  }

  const line = props.story.bodyLines[lineIndex]
  activeLine.value = lineIndex

  if (charIndex < line.length) {
    typedLines.value[lineIndex] = line.slice(0, charIndex + 1)
    const currentChar = line[charIndex]
    const delay = currentChar === ' ' ? 12 : 22
    queueTimeout(() => typeLine(lineIndex, charIndex + 1), delay)
    return
  }

  queueTimeout(() => typeLine(lineIndex + 1, 0), 260)
}

const startTypewriter = () => {
  clearTimers()
  resetTypingState()

  if (typeof window === 'undefined' || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    completeInstantly()
    return
  }

  queueTimeout(() => typeLine(0, 0), 320)
}

const handleImageError = () => {
  imageFailed.value = true
}

watch(
  () => props.story.key,
  () => {
    imageFailed.value = false
    startTypewriter()
  },
  { immediate: true }
)

const showImage = computed(() => Boolean(props.story.imagePath) && !imageFailed.value)
const placeholderNote = computed(() => (
  props.story.imagePath
    ? 'Place portrait here'
    : 'Portrait archive pending'
))
const placeholderPath = computed(() => (
  props.story.imagePath
    ? `frontend/public${props.story.imagePath}`
    : ''
))

onBeforeUnmount(() => {
  clearTimers()
})
</script>

<style scoped>
.agent-story {
  display: grid;
  grid-template-columns: minmax(280px, 380px) minmax(0, 1fr);
  gap: 48px;
  align-items: start;
}

.agent-story__frame {
  width: 100%;
  background: #ddd7cd;
  box-shadow: 0 20px 40px rgba(28, 21, 12, 0.1);
  overflow: hidden;
}

.agent-story__image {
  display: block;
  width: 100%;
  height: auto;
  object-fit: cover;
}

.agent-story__placeholder {
  display: flex;
  min-height: 470px;
  flex-direction: column;
  justify-content: center;
  padding: 24px;
  background: #dfd8ce;
  color: #1f1a16;
}

.agent-story__placeholder-note {
  font-family: var(--murmur-font-hand);
  font-size: 34px;
  line-height: 1;
}

.agent-story__placeholder-path {
  margin-top: 12px;
  font-family: var(--murmur-font-mono);
  font-size: 12px;
  line-height: 1.8;
}

.agent-story__label {
  margin-bottom: 18px;
  color: var(--murmur-text-muted);
  font-family: var(--murmur-font-mono);
  font-size: 11px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.agent-story__headline {
  margin-bottom: 28px;
}

.agent-story__headline-name,
.agent-story__headline-meta {
  margin: 0;
}

.agent-story__headline-name {
  color: var(--murmur-text-heading);
  font-family: var(--murmur-font-body);
  font-size: clamp(42px, 5vw, 62px);
  font-weight: 700;
  line-height: 0.98;
  letter-spacing: -0.04em;
}

.agent-story__headline-meta {
  margin-top: 12px;
  color: var(--murmur-text-primary);
  font-family: var(--murmur-font-body);
  font-size: clamp(20px, 2vw, 25px);
  line-height: 1.45;
}

.agent-story__body {
  max-width: 34rem;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.agent-story__line {
  margin: 0;
  color: var(--murmur-text-primary);
  font-family: var(--murmur-font-mono);
  font-size: clamp(17px, 1.45vw, 19px);
  line-height: 1.85;
  min-height: 1.85em;
}

.agent-story__cursor {
  display: inline-block;
  margin-left: 2px;
  animation: cursor-blink 0.9s steps(1, end) infinite;
}

.story-shell-enter-active,
.story-shell-leave-active {
  transition: opacity 0.45s ease;
}

.story-shell-enter-from,
.story-shell-leave-to {
  opacity: 0;
}

@keyframes cursor-blink {
  50% {
    opacity: 0;
  }
}

@media (max-width: 960px) {
  .agent-story {
    grid-template-columns: 1fr;
    gap: 28px;
  }

  .agent-story__frame {
    max-width: 420px;
  }
}

@media (max-width: 640px) {
  .agent-story__headline-name {
    font-size: 34px;
  }

  .agent-story__headline-meta {
    font-size: 18px;
  }

  .agent-story__line {
    font-size: 16px;
  }

  .agent-story__placeholder {
    min-height: 320px;
  }
}
</style>
