<template>
  <div class="main-view">
    <header class="app-header">
      <div class="header-left">
        <div class="brand" @click="router.push('/')">OPS</div>
      </div>

      <div class="header-center">
        <div class="view-switcher">
          <button
            v-for="mode in ['graph', 'split', 'workbench']"
            :key="mode"
            class="switch-btn"
            :class="{ active: viewMode === mode }"
            @click="viewMode = mode"
          >
            {{ { graph: 'Graph', split: 'Split View', workbench: 'Workbench' }[mode] }}
          </button>
        </div>
      </div>

      <div class="header-right">
        <div class="workflow-step">
          <span class="step-num">Step 3/5</span>
          <span class="step-name">Run Simulation</span>
        </div>
        <div class="step-divider"></div>
        <span class="status-indicator" :class="statusClass">
          <span class="dot"></span>
          {{ statusText }}
        </span>
      </div>
    </header>

    <main class="content-area">
      <div class="panel-wrapper left" :style="leftPanelStyle">
        <GraphPanel
          :graphData="graphData"
          :loading="graphLoading"
          :currentPhase="3"
          :isSimulating="currentStatus === 'processing'"
          @refresh="refreshGraph"
          @toggle-maximize="toggleMaximize('graph')"
        />
      </div>

      <div class="panel-wrapper right" :style="rightPanelStyle">
        <Step3Simulation
          :simulationId="currentSimulationId"
          :maxRounds="maxRounds"
          :projectData="projectData"
          :graphData="graphData"
          :systemLogs="systemLogs"
          :next-route-name="isDemoRoute ? 'DemoReport' : ''"
          :next-route-query="isDemoRoute ? demoQuery : {}"
          @go-back="handleGoBack"
          @add-log="addLog"
          @update-status="updateStatus"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GraphPanel from '../components/GraphPanel.vue'
import Step3Simulation from '../components/Step3Simulation.vue'
import { getProject, getGraphData } from '../api/graph'
import { getSimulation } from '../api/simulation'
import { buildDemoQuery, initializeDemoFlow } from '../store/demoFlow'

const route = useRoute()
const router = useRouter()
const isDemoRoute = computed(() => route.path.startsWith('/demo'))
const demoQuery = computed(() => buildDemoQuery())

const props = defineProps({
  simulationId: String,
})

const viewMode = ref('split')

const currentSimulationId = ref(props.simulationId || route.params.simulationId)
const projectData = ref(null)
const graphData = ref(null)
const graphLoading = ref(false)
const systemLogs = ref([])
const currentStatus = ref('processing')

const maxRounds = computed(() => {
  const raw = route.query.maxRounds
  if (!raw) {
    return undefined
  }

  const parsed = Number.parseInt(String(raw), 10)
  return Number.isFinite(parsed) ? parsed : undefined
})

const leftPanelStyle = computed(() => {
  if (viewMode.value === 'graph') return { width: '100%', opacity: 1, transform: 'translateX(0)' }
  if (viewMode.value === 'workbench') return { width: '0%', opacity: 0, transform: 'translateX(-20px)' }
  return { width: '50%', opacity: 1, transform: 'translateX(0)' }
})

const rightPanelStyle = computed(() => {
  if (viewMode.value === 'workbench') return { width: '100%', opacity: 1, transform: 'translateX(0)' }
  if (viewMode.value === 'graph') return { width: '0%', opacity: 0, transform: 'translateX(20px)' }
  return { width: '50%', opacity: 1, transform: 'translateX(0)' }
})

const statusClass = computed(() => currentStatus.value)

const statusText = computed(() => {
  if (currentStatus.value === 'error') return 'Error'
  if (currentStatus.value === 'completed') return 'Completed'
  if (currentStatus.value === 'ready') return 'Ready'
  return 'Running'
})

const addLog = (msg) => {
  const now = new Date()
  const time =
    now.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }) +
    '.' +
    now.getMilliseconds().toString().padStart(3, '0')

  systemLogs.value.push({ time, msg })
  if (systemLogs.value.length > 200) {
    systemLogs.value.shift()
  }
}

const updateStatus = (status) => {
  currentStatus.value = status
}

const toggleMaximize = (target) => {
  if (viewMode.value === target) {
    viewMode.value = 'split'
  } else {
    viewMode.value = target
  }
}

const handleGoBack = () => {
  if (isDemoRoute.value) {
    router.push({ name: 'DemoPopulation', query: demoQuery.value })
    return
  }

  router.push({ name: 'Simulation', params: { simulationId: currentSimulationId.value } })
}

const loadGraph = async (graphId) => {
  graphLoading.value = true

  try {
    const res = await getGraphData(graphId)
    if (res.success) {
      graphData.value = res.data
      addLog('Graph data loaded successfully')
    } else {
      addLog(`Failed to load graph data: ${res.error || 'Unknown error'}`)
    }
  } catch (error) {
    addLog(`Graph loading error: ${error.message}`)
  } finally {
    graphLoading.value = false
  }
}

const loadSimulationData = async () => {
  if (!currentSimulationId.value) {
    return
  }

  try {
    addLog(`Loading simulation data: ${currentSimulationId.value}`)
    const simRes = await getSimulation(currentSimulationId.value)
    if (simRes.success && simRes.data) {
      const simData = simRes.data
      if (simData.project_id) {
        const projRes = await getProject(simData.project_id)
        if (projRes.success && projRes.data) {
          projectData.value = projRes.data
          addLog(`Project loaded successfully: ${projRes.data.project_id}`)
          if (projRes.data.graph_id) {
            await loadGraph(projRes.data.graph_id)
          }
        } else {
          addLog(`Failed to load project data: ${projRes.error || 'Unknown error'}`)
        }
      }
    } else {
      addLog(`Failed to load simulation data: ${simRes.error || 'Unknown error'}`)
      currentStatus.value = 'error'
    }
  } catch (error) {
    addLog(`Simulation load error: ${error.message}`)
    currentStatus.value = 'error'
  }
}

const refreshGraph = () => {
  if (projectData.value?.graph_id) {
    loadGraph(projectData.value.graph_id)
  }
}

watch(
  () => route.params.simulationId,
  (newId) => {
    if (newId && newId !== currentSimulationId.value) {
      currentSimulationId.value = String(newId)
      systemLogs.value = []
      loadSimulationData()
    }
  }
)

onMounted(() => {
  const bootstrap = async () => {
    addLog('Simulation run view initialized')
    if (isDemoRoute.value) {
      const pack = await initializeDemoFlow({
        scenario: typeof route.query.scenario === 'string' ? route.query.scenario : '',
        country: typeof route.query.country === 'string' ? route.query.country : '',
      })
      currentSimulationId.value = pack.population.simulationId
    }
    loadSimulationData()
  }

  bootstrap()
})
</script>

<style scoped>
.main-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #fff;
  overflow: hidden;
  font-family: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
}

.app-header {
  height: 60px;
  border-bottom: 1px solid #eaeaea;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: #fff;
  z-index: 100;
  position: relative;
}

.brand {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  font-size: 18px;
  letter-spacing: 1px;
  cursor: pointer;
}

.header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.view-switcher {
  display: flex;
  background: #f5f5f5;
  padding: 4px;
  border-radius: 6px;
  gap: 4px;
}

.switch-btn {
  border: none;
  background: transparent;
  padding: 6px 16px;
  font-size: 12px;
  font-weight: 600;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.switch-btn.active {
  background: #fff;
  color: #000;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.workflow-step {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #999;
}

.step-name {
  font-weight: 700;
  color: #000;
}

.step-divider {
  width: 1px;
  height: 14px;
  background-color: #e0e0e0;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
}

.status-indicator.processing .dot {
  background: #ff5722;
  animation: pulse 1s infinite;
}

.status-indicator.completed .dot,
.status-indicator.ready .dot {
  background: #4caf50;
}

.status-indicator.error .dot {
  background: #f44336;
}

@keyframes pulse {
  50% {
    opacity: 0.5;
  }
}

.content-area {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
}

.panel-wrapper {
  height: 100%;
  overflow: hidden;
  transition:
    width 0.4s cubic-bezier(0.25, 0.8, 0.25, 1),
    opacity 0.3s ease,
    transform 0.3s ease;
  will-change: width, opacity, transform;
}

.panel-wrapper.left {
  border-right: 1px solid #eaeaea;
}
</style>
