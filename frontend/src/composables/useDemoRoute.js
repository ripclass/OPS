import { computed, onMounted, ref, watch } from 'vue'
import {
  buildDemoQuery,
  currentDemoPack,
  demoState,
  initializeDemoFlow,
  setDemoCurrentStep,
} from '../store/demoFlow'

export function useDemoRoute(route, router, stepName) {
  const loading = ref(true)

  const syncDemoState = async () => {
    loading.value = true

    await initializeDemoFlow({
      scenario: typeof route.query.scenario === 'string' ? route.query.scenario : '',
      country: typeof route.query.country === 'string' ? route.query.country : '',
    })

    setDemoCurrentStep(stepName)

    const nextQuery = {
      ...route.query,
      ...buildDemoQuery(),
    }

    if (route.query.country !== nextQuery.country || route.query.scenario !== nextQuery.scenario) {
      router.replace({
        path: route.path,
        query: nextQuery,
      })
    }

    loading.value = false
  }

  watch(
    () => [route.query.country, route.query.scenario],
    () => {
      syncDemoState()
    }
  )

  onMounted(() => {
    syncDemoState()
  })

  return {
    loading,
    demoState,
    currentPack: computed(() => currentDemoPack.value),
    scenario: computed(() => demoState.scenario),
    countryCode: computed(() => demoState.countryCode),
    demoQuery: computed(() => buildDemoQuery()),
  }
}
