<template>
  <Transition name="story-shell" mode="out-in">
    <article :key="story.key" class="hero-story">
      <div class="hero-story__canvas">
        <div
          v-for="(scribble, index) in shellScribbles"
          :key="`${story.key}-shell-${index}`"
          class="hero-story__scribble"
          :class="scribble.className"
        >
          {{ scribble.text }}
        </div>

        <div class="hero-story__media">
          <img
            v-if="showImage"
            class="hero-story__image"
            :src="story.imagePath"
            :alt="story.imageAlt || story.headlineName"
            @error="handleImageError"
          />
          <div
            v-else
            class="hero-story__placeholder"
          >
            <div class="hero-story__placeholder-note">Place portrait here</div>
            <div class="hero-story__placeholder-path">{{ placeholderPath }}</div>
          </div>

          <div
            v-for="(scribble, index) in mediaScribbles"
            :key="`${story.key}-media-${index}`"
            class="hero-story__scribble hero-story__scribble--media"
            :class="scribble.className"
          >
            {{ scribble.text }}
          </div>

          <div
            v-if="showImage && story.eyeMarker"
            class="hero-story__eye-marker"
            :style="eyeMarkerStyle"
          />
        </div>

        <div class="hero-story__ink-title">
          <p v-for="(line, index) in inkTitleLines" :key="`${story.key}-ink-${index}`">{{ line }}</p>
        </div>

        <div class="hero-story__copy">
          <h1 class="hero-story__headline">{{ story.headlineName }}</h1>
          <p v-if="story.headlineInkMeta" class="hero-story__headline-meta">{{ story.headlineInkMeta }}</p>
          <div class="hero-story__body">
            <p
              v-for="(paragraph, index) in storyParagraphs"
              :key="`${story.key}-paragraph-${index}`"
              class="hero-story__paragraph"
            >
              {{ paragraph }}
            </p>
          </div>
        </div>

        <div class="hero-story__brand-lockup">
          <div class="hero-story__brand-word">{{ story.footerWordmark || 'MURMUR' }}</div>
          <p class="hero-story__brand-subtitle">
            {{ story.footerSubtitle || 'South Asia Behavioral Intelligence' }}
          </p>
        </div>

        <div
          v-for="(scribble, index) in belowMediaScribbles"
          :key="`${story.key}-footer-note-${index}`"
          class="hero-story__scribble hero-story__scribble--footer"
          :class="scribble.className"
        >
          {{ scribble.text }}
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
      window.setTimeout(() => emit('complete', props.story.key), 180)
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
const allScribbles = computed(() => props.story.scribbles || [])
const shellScribbles = computed(() => allScribbles.value.filter(item => (item.target || 'shell') === 'shell'))
const mediaScribbles = computed(() => allScribbles.value.filter(item => item.target === 'media'))
const belowMediaScribbles = computed(() => allScribbles.value.filter(item => item.target === 'belowMedia'))
const placeholderPath = computed(() => (
  props.story.imagePath
    ? `frontend/public${props.story.imagePath}`
    : ''
))
const eyeMarkerStyle = computed(() => {
  if (!props.story.eyeMarker) {
    return {}
  }

  return {
    top: props.story.eyeMarker.top,
    left: props.story.eyeMarker.left,
    width: props.story.eyeMarker.width,
    height: props.story.eyeMarker.height,
    background: props.story.eyeMarker.color || '#0048ffbf',
    transform: `rotate(${props.story.eyeMarker.rotate || '0deg'})`,
  }
})
const storyParagraphs = computed(() => {
  if (Array.isArray(props.story.bodyParagraphs) && props.story.bodyParagraphs.length) {
    return props.story.bodyParagraphs
  }
  return props.story.bodyLines || []
})
const inkTitleLines = computed(() => {
  if (Array.isArray(props.story.heroInkLines) && props.story.heroInkLines.length) {
    return props.story.heroInkLines
  }
  return ['MURMUR', 'KNOWS', String(props.story.name || '').toUpperCase()]
})
</script>

<style scoped>
.hero-story {
  display: flex;
  justify-content: center;
}

.hero-story__canvas {
  position: relative;
  width: min(978px, 100%);
  min-height: 940px;
}

.hero-story__media {
  position: absolute;
  left: 7px;
  top: 81px;
  width: 560px;
  height: 677px;
  overflow: hidden;
}

.hero-story__image,
.hero-story__placeholder {
  width: 100%;
  height: 100%;
}

.hero-story__image {
  display: block;
  object-fit: cover;
  object-position: center 30%;
  filter: grayscale(1) contrast(1.05) brightness(1.02);
}

.hero-story__placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 32px;
  background: #ece9e3;
}

.hero-story__placeholder-note {
  font-family: var(--murmur-font-hand);
  font-size: 34px;
  line-height: 0.9;
}

.hero-story__placeholder-path {
  margin-top: 14px;
  color: #111;
  font-family: var(--murmur-font-type);
  font-size: 12px;
  line-height: 1.3;
}

.hero-story__eye-marker {
  position: absolute;
}

.hero-story__ink-title {
  position: absolute;
  left: 595px;
  top: 84px;
  width: 383px;
  color: #000;
  font-family: var(--murmur-font-hand);
  font-size: 78px;
  line-height: 0.7;
  text-transform: uppercase;
}

.hero-story__ink-title p {
  margin: 0;
}

.hero-story__copy {
  position: absolute;
  left: 595px;
  top: 620px;
  width: 263px;
  color: #000;
}

.hero-story__headline {
  margin: 0;
  color: #050505;
  font-family: var(--murmur-font-display);
  font-size: 24px;
  font-weight: 700;
  line-height: 1.29;
}

.hero-story__headline-meta {
  margin: 2px 0 0;
  color: #0048ff;
  font-family: var(--murmur-font-hand);
  font-size: 18px;
  line-height: 0.68;
  white-space: pre-line;
}

.hero-story__body {
  margin-top: 10px;
}

.hero-story__paragraph {
  margin: 0 0 10px;
  color: #000;
  font-family: var(--murmur-font-type);
  font-size: 10px;
  line-height: 1;
  text-shadow:
    0.15px 0 rgba(0, 0, 0, 0.9),
    0 0 0.35px rgba(0, 0, 0, 0.45);
}

.hero-story__brand-lockup {
  position: absolute;
  left: 11px;
  top: 850px;
  width: 271px;
}

.hero-story__brand-word {
  color: #050505;
  font-family: var(--murmur-font-display);
  font-size: 64px;
  font-weight: 800;
  line-height: 1;
}

.hero-story__brand-subtitle {
  margin: 6px 0 0;
  color: #000;
  font-family: var(--murmur-font-ui);
  font-size: 18px;
  line-height: 1.1;
}

.hero-story__scribble {
  position: absolute;
  z-index: 2;
  white-space: pre-line;
  color: #000;
  font-family: var(--murmur-font-hand);
  line-height: 0.68;
  letter-spacing: 0;
  pointer-events: none;
}

.hero-story__scribble--media {
  z-index: 3;
}

.hero-story__scribble--footer {
  position: absolute;
  left: 655px;
  top: 864px;
  width: 312px;
  text-align: right;
}

.scribble--hero-top-left {
  left: 7px;
  top: 26px;
  font-size: 36px;
  transform: rotate(-2deg);
}

.scribble--top-left {
  left: 14px;
  top: 32px;
  max-width: 320px;
  font-size: 52px;
  transform: rotate(-3deg);
}

.scribble--top-right {
  right: 6px;
  top: 42px;
  max-width: 260px;
  font-size: 24px;
  text-align: right;
  transform: rotate(4deg);
}

.scribble--bottom-right {
  right: 0;
  bottom: 36px;
  max-width: 260px;
  font-size: 34px;
  text-align: right;
  transform: rotate(-3deg);
}

.scribble--hero-in-image {
  left: 8px;
  bottom: 10px;
  width: 302px;
  color: #fff;
  font-size: 64px;
  transform: rotate(-3deg);
}

.scribble--hero-footer-note {
  font-size: 28px;
  transform: rotate(-2deg);
}

.story-shell-enter-active,
.story-shell-leave-active {
  transition: opacity 0.35s ease;
}

.story-shell-enter-from,
.story-shell-leave-to {
  opacity: 0;
}

@media (max-width: 1024px) {
  .hero-story__canvas {
    min-height: 0;
    padding-bottom: 48px;
  }

  .hero-story__media,
  .hero-story__ink-title,
  .hero-story__copy,
  .hero-story__brand-lockup,
  .hero-story__scribble,
  .hero-story__scribble--footer {
    position: static;
    width: auto;
  }

  .hero-story__canvas {
    display: grid;
    gap: 24px;
  }

  .hero-story__media {
    height: auto;
  }

  .hero-story__image,
  .hero-story__placeholder {
    aspect-ratio: 560 / 677;
    height: auto;
  }

  .hero-story__ink-title {
    font-size: 56px;
  }

  .hero-story__copy {
    max-width: 420px;
  }

  .hero-story__brand-word {
    font-size: 48px;
  }

  .hero-story__brand-subtitle {
    font-size: 16px;
  }

  .hero-story__scribble {
    display: none;
  }
}
</style>
