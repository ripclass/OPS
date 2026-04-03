<template>
  <Transition name="story-shell" mode="out-in">
    <article :key="story.key" class="agent-story" :class="{ 'agent-story--global': globalMode }">
      <div class="agent-story__label">
        <span v-if="globalMode">South Asia opening story</span>
        <span v-else>{{ story.code }} opening story</span>
      </div>

      <div class="agent-story__lines">
        <p
          v-for="(line, index) in story.lines"
          :key="`${story.key}-${index}`"
          class="agent-story__line"
          :class="{ 'agent-story__line--visible': index < visibleCount }"
        >
          {{ line }}
        </p>
      </div>
    </article>
  </Transition>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'

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

const visibleCount = ref(0)
let timers = []

const clearTimers = () => {
  timers.forEach(timer => window.clearTimeout(timer))
  timers = []
}

const scheduleReveal = () => {
  clearTimers()
  visibleCount.value = 0

  props.story.lines.forEach((_, index) => {
    timers.push(
      window.setTimeout(() => {
        visibleCount.value = index + 1
      }, 450 + index * 360)
    )
  })

  timers.push(
    window.setTimeout(() => {
      emit('complete', props.story.key)
    }, 850 + props.story.lines.length * 360)
  )
}

watch(
  () => props.story.key,
  () => {
    if (typeof window === 'undefined') {
      visibleCount.value = props.story.lines.length
      emit('complete', props.story.key)
      return
    }
    scheduleReveal()
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  clearTimers()
})
</script>

<style scoped>
.agent-story {
  width: 100%;
}

.agent-story__label {
  margin-bottom: 26px;
  color: var(--murmur-text-muted);
  font-family: var(--murmur-font-mono);
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.agent-story__lines {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.agent-story__line {
  margin: 0;
  color: var(--murmur-text-primary);
  font-family: var(--murmur-font-body);
  font-size: clamp(22px, 4.1vw, 34px);
  line-height: 1.42;
  transform: translateY(12px);
  opacity: 0;
  transition: opacity 0.72s ease, transform 0.72s ease;
}

.agent-story__line--visible {
  opacity: 1;
  transform: translateY(0);
}

.agent-story__line:first-child {
  color: var(--murmur-text-heading);
  font-family: var(--murmur-font-body);
  font-size: clamp(24px, 4.6vw, 40px);
  line-height: 1.34;
}

.agent-story__line:nth-last-child(2),
.agent-story__line:last-child {
  color: var(--murmur-text-heading);
}

.story-shell-enter-active,
.story-shell-leave-active {
  transition: opacity 0.8s ease;
}

.story-shell-enter-from,
.story-shell-leave-to {
  opacity: 0;
}

@media (max-width: 640px) {
  .agent-story__label {
    margin-bottom: 22px;
  }

  .agent-story__line {
    font-size: 20px;
    line-height: 1.5;
  }

  .agent-story__line:first-child {
    font-size: 25px;
  }
}
</style>
