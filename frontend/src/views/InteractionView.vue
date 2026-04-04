<template>
  <div class="main-view">
    <!-- Header -->
    <header class="app-header">
      <div class="header-left">
        <div class="brand" @click="router.push('/')">{{ brandLabel }}</div>
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
          <span class="step-num">{{ workflowStepLabel }}</span>
          <span class="step-name">Live Interactions</span>
        </div>
        <div class="step-divider"></div>
        <span class="status-indicator" :class="statusClass">
          <span class="dot"></span>
          {{ statusText }}
        </span>
        <button
          v-if="isDemoRoute"
          class="demo-continue-btn"
          type="button"
          @click="handleDemoContinue"
        >
          {{ demoContinueLabel }} →
        </button>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="content-area">
      <!-- Left Panel: Graph -->
      <div class="panel-wrapper left" :style="leftPanelStyle">
        <GraphPanel 
          :graphData="graphData"
          :loading="graphLoading"
          :currentPhase="5"
          :isSimulating="false"
          @refresh="refreshGraph"
          @toggle-maximize="toggleMaximize('graph')"
        />
      </div>

      <!-- Right Panel: Step5 Live Interactions -->
      <div class="panel-wrapper right" :style="rightPanelStyle">
        <Step5Interaction
          :reportId="currentReportId"
          :simulationId="simulationId"
          :systemLogs="systemLogs"
          @add-log="addLog"
          @update-status="updateStatus"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GraphPanel from '../components/GraphPanel.vue'
import Step5Interaction from '../components/Step5Interaction.vue'
import { getProject, getGraphData } from '../api/graph'
import { getSimulation } from '../api/simulation'
import { getReport } from '../api/report'
import { authState } from '../store/auth'
import { demoState, initializeDemoFlow } from '../store/demoFlow'
import { useDemoBrand } from '../composables/useDemoBrand'

const route = useRoute()
const router = useRouter()
const isDemoRoute = computed(() => route.path.startsWith('/demo'))
const { brandLabel } = useDemoBrand()

// Props
const props = defineProps({
  reportId: String
})

// Layout State - Default switch to workstation view
const viewMode = ref('workbench')

// Data State
const currentReportId = ref(route.params.reportId)
const simulationId = ref(null)
const projectData = ref(null)
const graphData = ref(null)
const graphLoading = ref(false)
const systemLogs = ref([])
const currentStatus = ref('ready') // ready | processing | completed | error

// --- Computed Layout Styles ---
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

// --- Status Computed ---
const statusClass = computed(() => {
  return currentStatus.value
})

const statusText = computed(() => {
  if (currentStatus.value === 'error') return 'Error'
  if (currentStatus.value === 'completed') return 'Completed'
  if (currentStatus.value === 'processing') return 'Processing'
  return 'Ready'
})
const workflowStepLabel = computed(() => (isDemoRoute.value ? 'Step 5/6' : 'Step 5/5'))
const demoContinueLabel = computed(() => {
  return authState.user ? 'Open console with this brief' : 'Sign up to run the real scenario'
})

const buildConsolePath = (scenario = '') => {
  if (!scenario) {
    return '/console'
  }
  return `/console?scenario=${encodeURIComponent(scenario)}`
}

// --- Helpers ---
const addLog = (msg) => {
  const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + '.' + new Date().getMilliseconds().toString().padStart(3, '0')
  systemLogs.value.push({ time, msg })
  if (systemLogs.value.length > 200) {
    systemLogs.value.shift()
  }
}

const updateStatus = (status) => {
  currentStatus.value = status
}

const resetInteractionViewState = () => {
  simulationId.value = null
  projectData.value = null
  graphData.value = null
  graphLoading.value = false
  systemLogs.value = []
  currentStatus.value = 'processing'
}

// --- Layout Methods ---
const toggleMaximize = (target) => {
  if (viewMode.value === target) {
    viewMode.value = 'split'
  } else {
    viewMode.value = target
  }
}

// --- Data Logic ---
const loadReportData = async () => {
  if (!currentReportId.value) return

  try {
    addLog(`Loading report data: ${currentReportId.value}`)
    currentStatus.value = 'processing'
    
    // Retrieve report information to obtain simulation_id
    const reportRes = await getReport(currentReportId.value)
    if (reportRes.success && reportRes.data) {
      const reportData = reportRes.data
      simulationId.value = reportData.simulation_id
      
      if (simulationId.value) {
        // Fetch simulation information
        const simRes = await getSimulation(simulationId.value)
        if (simRes.success && simRes.data) {
          const simData = simRes.data
          
          // Fetch project information
          if (simData.project_id) {
            const projRes = await getProject(simData.project_id)
            if (projRes.success && projRes.data) {
              projectData.value = projRes.data
              addLog(`Project loaded successfully: ${projRes.data.project_id}`)
              
              // Retrieve graph data
              if (projRes.data.graph_id) {
                await loadGraph(projRes.data.graph_id)
              }
              currentStatus.value = 'ready'
            } else {
              addLog(`Failed to load project data: ${projRes.error || 'Unknown error'}`)
              currentStatus.value = 'error'
            }
          } else {
            addLog('Simulation record is missing project_id')
            currentStatus.value = 'error'
          }
        } else {
          addLog(`Failed to load simulation data: ${simRes.error || 'Unknown error'}`)
          currentStatus.value = 'error'
        }
      } else {
        addLog('Report record is missing simulation_id')
        currentStatus.value = 'error'
      }
    } else {
      addLog(`Failed to get report information: ${reportRes.error || 'Unknown error'}`)
      currentStatus.value = 'error'
    }
  } catch (err) {
    addLog(`Load exception: ${err.message}`)
    currentStatus.value = 'error'
  }
}

const loadGraph = async (graphId) => {
  graphLoading.value = true
  
  try {
    const res = await getGraphData(graphId)
    if (res.success) {
      graphData.value = res.data
      addLog('Graph Data Load Successful')
    }
  } catch (err) {
    addLog(`Spectrum load failed: ${err.message}`)
  } finally {
    graphLoading.value = false
  }
}

const refreshGraph = () => {
  if (projectData.value?.graph_id) {
    loadGraph(projectData.value.graph_id)
  }
}

const handleDemoContinue = () => {
  const redirect = buildConsolePath(demoState.scenario)
  if (authState.user) {
    router.push(redirect)
    return
  }

  router.push({
    name: 'Home',
    query: {
      auth: 'signup',
      redirect,
    },
  })
}

// Watch route params
watch(() => route.params.reportId, (newId) => {
  if (newId && newId !== currentReportId.value) {
    currentReportId.value = String(newId)
    resetInteractionViewState()
    loadReportData()
  }
})

onMounted(() => {
  const bootstrap = async () => {
    addLog('Interaction View Initialized')
    if (isDemoRoute.value) {
      const pack = await initializeDemoFlow({
        scenario: typeof route.query.scenario === 'string' ? route.query.scenario : '',
        country: typeof route.query.country === 'string' ? route.query.country : '',
      })
      currentReportId.value = `demo_${pack.key}_report`
    }
    loadReportData()
  }

  bootstrap()
})
</script>

<style scoped>
.main-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #FFF;
  overflow: hidden;
  font-family: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
}

/* Header */
.app-header {
  height: 60px;
  border-bottom: 1px solid #EAEAEA;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: #FFF;
  z-index: 100;
  position: relative;
}

.header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.brand {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  font-size: 18px;
  letter-spacing: 1px;
  cursor: pointer;
}

.view-switcher {
  display: flex;
  background: #F5F5F5;
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
  background: #FFF;
  color: #000;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.demo-continue-btn {
  border: none;
  background: #000;
  color: #FFF;
  padding: 10px 18px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.03em;
  cursor: pointer;
  transition: background 0.2s ease;
}

.demo-continue-btn:hover {
  background: #222;
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
  background-color: #E0E0E0;
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
  background: #CCC;
}

.status-indicator.ready .dot { background: #4CAF50; }
.status-indicator.processing .dot { background: #FF9800; animation: pulse 1s infinite; }
.status-indicator.completed .dot { background: #4CAF50; }
.status-indicator.error .dot { background: #F44336; }

@keyframes pulse { 50% { opacity: 0.5; } }

/* Content */
.content-area {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
}

.panel-wrapper {
  height: 100%;
  overflow: hidden;
  transition: width 0.4s cubic-bezier(0.25, 0.8, 0.25, 1), opacity 0.3s ease, transform 0.3s ease;
  will-change: width, opacity, transform;
}

.panel-wrapper.left {
  border-right: 1px solid #EAEAEA;
}
</style>
