<template>
  <Transition name="story-shell" mode="out-in">
    <article :key="story.key" class="agent-story">
      <div
        v-for="(scribble, index) in story.scribbles || []"
        :key="`${story.key}-scribble-${index}`"
        class="agent-story__scribble"
        :class="scribble.className"
      >
        {{ scribble.text }}
      </div>

      <div class="agent-story__media">
        <div class="agent-story__frame">
          <img
            v-if="showImage"
            class="agent-story__image"
            :src="story.imagePath"
            :alt="story.imageAlt || story.headlineName"
            @error="handleImageError"
          />
          <div
            v-if="showImage && story.eyeMarker"
            class="agent-story__eye-marker"
            :style="eyeMarkerStyle"
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
            {{ line }}
          </p>
        </div>
      </div>
    </article>
  </Transition>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

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

const imageFailed = ref(false)

watch(
  () => props.story.key,
  () => {
    imageFailed.value = false
    if (typeof window !== 'undefined') {
      window.setTimeout(() => emit('complete', props.story.key), 220)
    } else {
      emit('complete', props.story.key)
    }
  },
  { immediate: true }
)

const handleImageError = () => {
  imageFailed.value = true
}

const showImage = computed(() => Boolean(props.story.imagePath) && !imageFailed.value)
const eyeMarkerStyle = computed(() => {
  if (!props.story.eyeMarker) {
    return {}
  }

  return {
    top: props.story.eyeMarker.top,
    left: props.story.eyeMarker.left,
    width: props.story.eyeMarker.width,
    height: props.story.eyeMarker.height,
    transform: `rotate(${props.story.eyeMarker.rotate || '0deg'})`,
  }
})
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
</script>

<style scoped>
.agent-story {
  position: relative;
  display: grid;
  grid-template-columns: minmax(250px, 348px) minmax(0, 420px);
  gap: 56px;
  align-items: start;
  justify-content: center;
  padding: 40px 0 84px;
}

.agent-story__media {
  position: relative;
  z-index: 2;
}

.agent-story__frame {
  position: relative;
  width: 100%;
  background: #f5f5f1;
  overflow: hidden;
}

.agent-story__image {
  display: block;
  width: 100%;
  height: auto;
  object-fit: cover;
  filter: grayscale(1) contrast(1.03);
}

.agent-story__eye-marker {
  position: absolute;
  background: #c0392b;
  opacity: 0.96;
  mix-blend-mode: multiply;
}

.agent-story__placeholder {
  display: flex;
  min-height: 470px;
  flex-direction: column;
  justify-content: center;
  padding: 24px;
  background: #ece7de;
  color: #111;
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
  line-height: 1.5;
}

.agent-story__copy {
  position: relative;
  z-index: 2;
  padding-top: 10px;
}

.agent-story__label {
  margin-bottom: 16px;
  color: #6e6a64;
  font-family: var(--murmur-font-mono);
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.agent-story__headline {
  margin-bottom: 18px;
}

.agent-story__headline-name,
.agent-story__headline-meta {
  margin: 0;
}

.agent-story__headline-name {
  color: #0c0c0c;
  font-family: var(--murmur-font-body);
  font-size: clamp(42px, 5vw, 64px);
  font-weight: 700;
  line-height: 0.95;
  letter-spacing: -0.06em;
}

.agent-story__headline-meta {
  margin-top: 8px;
  color: #111;
  font-family: var(--murmur-font-body);
  font-size: clamp(18px, 2vw, 24px);
  line-height: 1.2;
}

.agent-story__body {
  max-width: 30rem;
}

.agent-story__line {
  margin: 0 0 4px;
  color: #090909;
  font-family: var(--murmur-font-mono);
  font-size: clamp(15px, 1.22vw, 17px);
  line-height: 1.08;
  letter-spacing: -0.01em;
}

.agent-story__scribble {
  position: absolute;
  z-index: 1;
  white-space: pre-line;
  color: #0b0b0b;
  font-family: var(--murmur-font-hand);
  font-weight: 700;
  line-height: 0.9;
  letter-spacing: 0.01em;
  pointer-events: none;
  transform: rotate(-4deg);
  opacity: 0.97;
}

.scribble--xl {
  font-size: clamp(38px, 5vw, 72px);
}

.scribble--lg {
  font-size: clamp(28px, 3.3vw, 44px);
}

.scribble--md {
  font-size: clamp(22px, 2.5vw, 32px);
}

.scribble--sm {
  font-size: clamp(16px, 1.8vw, 22px);
}

.scribble--xs {
  font-size: clamp(14px, 1.35vw, 18px);
}

.scribble--top-left {
  top: -38px;
  left: -8px;
  max-width: 360px;
  transform: rotate(-5deg);
}

.scribble--left-mid {
  top: 150px;
  left: -118px;
  max-width: 180px;
  transform: rotate(-7deg);
}

.scribble--top-right {
  top: 24px;
  right: 56px;
  transform: rotate(5deg);
}

.scribble--bottom-right {
  right: 12px;
  bottom: -12px;
  max-width: 270px;
  transform: rotate(-4deg);
}

.scribble--bottom-left {
  left: 200px;
  bottom: 48px;
  transform: rotate(3deg);
}

.scribble--below-copy {
  left: 420px;
  bottom: -8px;
  max-width: 290px;
  transform: rotate(-5deg);
}

.scribble--accent {
  color: #c0392b;
}

.story-shell-enter-active,
.story-shell-leave-active {
  transition: opacity 0.45s ease;
}

.story-shell-enter-from,
.story-shell-leave-to {
  opacity: 0;
}

@media (max-width: 1040px) {
  .agent-story {
    grid-template-columns: minmax(220px, 320px) minmax(0, 1fr);
    gap: 38px;
  }

  .scribble--left-mid {
    left: -72px;
  }

  .scribble--bottom-right {
    right: 0;
    bottom: -30px;
  }

  .scribble--below-copy {
    left: 340px;
    bottom: 0;
  }
}

@media (max-width: 820px) {
  .agent-story {
    grid-template-columns: 1fr;
    gap: 28px;
    padding-top: 14px;
  }

  .agent-story__frame {
    max-width: 360px;
  }

  .agent-story__scribble {
    display: none;
  }
}

@media (max-width: 640px) {
  .agent-story__headline-name {
    font-size: 36px;
  }

  .agent-story__headline-meta {
    font-size: 18px;
  }

  .agent-story__line {
    font-size: 14px;
    line-height: 1.08;
    margin-bottom: 4px;
  }

  .agent-story__placeholder {
    min-height: 320px;
  }
}
</style>
