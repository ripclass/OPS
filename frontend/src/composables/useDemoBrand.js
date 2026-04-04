import { computed } from 'vue'
import { useRoute } from 'vue-router'

export function useDemoBrand() {
  const route = useRoute()
  const isDemoRoute = computed(() => route.path.startsWith('/demo'))

  const brandLabel = computed(() => 'Murmur')
  const reportAgentLabel = computed(() => 'Murmur report agent')
  const insightReportLabel = computed(() => 'Murmur Insight Report')
  const interactionToolsLabel = computed(() => 'Murmur Interaction Tools')
  const workbenchLabel = computed(() => 'Murmur Workbench')
  const runNoun = computed(() => 'Murmur run')
  const personasLabel = computed(() => 'Generated Murmur Personas')
  const inputModelLabel = computed(() => 'MURMUR INPUT MODEL')
  const engineLabel = computed(() => 'Engine: Murmur / OASIS')

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
