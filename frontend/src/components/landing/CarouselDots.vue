<template>
  <div class="carousel-dots" aria-label="Story selection">
    <button
      v-for="(_, index) in total"
      :key="index"
      class="carousel-dot"
      :class="{ 'carousel-dot--active': index === activeIndex }"
      type="button"
      :aria-label="`Show story ${index + 1}`"
      @click="$emit('select', index)"
    />
  </div>
</template>

<script setup>
defineProps({
  total: {
    type: Number,
    required: true,
  },
  activeIndex: {
    type: Number,
    required: true,
  },
})

defineEmits(['select'])
</script>

<style scoped>
.carousel-dots {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.carousel-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  border: 1px solid var(--murmur-border);
  background: transparent;
  cursor: pointer;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.carousel-dot--active {
  background: var(--murmur-text-heading);
  border-color: var(--murmur-text-heading);
}

@media (max-width: 768px) {
  .carousel-dot {
    width: 14px;
    height: 14px;
  }
}
</style>
