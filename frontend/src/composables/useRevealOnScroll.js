import { onBeforeUnmount, onMounted, ref } from 'vue'

export function useRevealOnScroll(options = {}) {
  const targetRef = ref(null)
  const isVisible = ref(false)
  let observer = null

  onMounted(() => {
    if (typeof window === 'undefined' || !targetRef.value) {
      isVisible.value = true
      return
    }

    observer = new IntersectionObserver(
      entries => {
        const [entry] = entries
        if (entry?.isIntersecting) {
          isVisible.value = true
          observer?.disconnect()
          observer = null
        }
      },
      {
        threshold: options.threshold ?? 0.16,
        rootMargin: options.rootMargin ?? '0px 0px -8% 0px',
      }
    )

    observer.observe(targetRef.value)
  })

  onBeforeUnmount(() => {
    observer?.disconnect()
    observer = null
  })

  return {
    targetRef,
    isVisible,
  }
}
