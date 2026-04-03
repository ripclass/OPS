<template>
  <Transition name="story-shell" mode="out-in">
    <article :key="story.key" class="agent-story">
      <div
        v-for="(scribble, index) in shellScribbles"
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
            v-for="(scribble, index) in mediaScribbles"
            :key="`${story.key}-media-${index}`"
            class="agent-story__scribble agent-story__scribble--media"
            :class="scribble.className"
          >
            {{ scribble.text }}
          </div>
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

        <div
          v-for="(scribble, index) in belowMediaScribbles"
          :key="`${story.key}-below-media-${index}`"
          class="agent-story__scribble agent-story__scribble--below-media"
          :class="scribble.className"
        >
          {{ scribble.text }}
        </div>
      </div>

      <div class="agent-story__copy">
        <div
          v-for="(scribble, index) in copyScribbles"
          :key="`${story.key}-copy-${index}`"
          class="agent-story__scribble agent-story__scribble--copy"
          :class="scribble.className"
        >
          {{ scribble.text }}
        </div>

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
            v-for="(paragraph, index) in storyParagraphs"
            :key="`${story.key}-${index}`"
            class="agent-story__paragraph"
          >
            {{ paragraph }}
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

const allScribbles = computed(() => props.story.scribbles || [])
const shellScribbles = computed(() => allScribbles.value.filter(s => (s.target || 'shell') === 'shell'))
const mediaScribbles = computed(() => allScribbles.value.filter(s => s.target === 'media'))
const belowMediaScribbles = computed(() => allScribbles.value.filter(s => s.target === 'belowMedia'))
const copyScribbles = computed(() => allScribbles.value.filter(s => s.target === 'copy'))
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
const storyParagraphs = computed(() => {
  if (Array.isArray(props.story.bodyParagraphs) && props.story.bodyParagraphs.length) {
    return props.story.bodyParagraphs
  }
  return props.story.bodyLines || []
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
  filter: grayscale(1) contrast(1.08) brightness(1.02);
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

.agent-story__paragraph {
  margin: 0 0 12px;
  color: #000;
  font-family: var(--murmur-font-mono);
  font-size: clamp(15px, 1.22vw, 17px);
  line-height: 1.22;
  letter-spacing: -0.01em;
  text-shadow:
    0.14px 0 rgba(0, 0, 0, 0.85),
    0 0 0.5px rgba(0, 0, 0, 0.35);
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

.agent-story__scribble--media {
  position: absolute;
}

.agent-story__scribble--below-media {
  position: relative;
  display: inline-block;
  margin-top: 16px;
}

.agent-story__scribble--copy {
  position: absolute;
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

.scribble--copy-shoulder {
  top: 52px;
  right: 10px;
  max-width: 190px;
  transform: rotate(4deg);
}

.scribble--accent {
  color: #c0392b;
}

.scribble--in-image {
  left: 18px;
  bottom: 18px;
  max-width: 220px;
  line-height: 0.86;
  transform: rotate(-3deg);
}

.scribble--under-image {
  max-width: 220px;
  line-height: 0.96;
  transform: rotate(-2deg);
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

  .agent-story__scribble,
  .agent-story__scribble--copy,
  .agent-story__scribble--media,
  .agent-story__scribble--below-media {
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

  .agent-story__paragraph {
    font-size: 14px;
    line-height: 1.2;
    margin-bottom: 10px;
  }

  .agent-story__placeholder {
    min-height: 320px;
  }
}
</style>
