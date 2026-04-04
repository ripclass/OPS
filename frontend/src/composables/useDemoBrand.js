import { computed } from 'vue'
import { useRoute } from 'vue-router'

export function useDemoBrand() {
  const route = useRoute()
  const isDemoRoute = computed(() => route.path.startsWith('/demo'))

  const brandLabel = computed(() => (isDemoRoute.value ? 'Murmur' : 'OPS'))
  const reportAgentLabel = computed(() => (isDemoRoute.value ? 'Murmur report agent' : 'OPS report agent'))
  const insightReportLabel = computed(() => (isDemoRoute.value ? 'Murmur Insight Report' : 'OPS Insight Report'))
  const interactionToolsLabel = computed(() => (isDemoRoute.value ? 'Murmur Interaction Tools' : 'OPS Interaction Tools'))
  const workbenchLabel = computed(() => (isDemoRoute.value ? 'Murmur Workbench' : 'OPS WORKBENCH'))
  const runNoun = computed(() => (isDemoRoute.value ? 'Murmur run' : 'OPS run'))
  const personasLabel = computed(() => (isDemoRoute.value ? 'Generated Murmur Personas' : 'Generated OPS Personas'))
  const inputModelLabel = computed(() => (isDemoRoute.value ? 'MURMUR INPUT MODEL' : 'OPS INPUT MODEL'))
  const engineLabel = computed(() => (isDemoRoute.value ? 'Engine: Murmur / OASIS' : 'Engine: OPS / OASIS'))

  return {
    isDemoRoute,
    brandLabel,
    reportAgentLabel,
    insightReportLabel,
    interactionToolsLabel,
    workbenchLabel,
    runNoun,
    personasLabel,
    inputModelLabel,
    engineLabel,
  }
}
