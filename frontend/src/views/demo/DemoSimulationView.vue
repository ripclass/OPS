<template>
  <DemoWorkspaceShell
    v-if="!loading"
    :step-number="3"
    step-name="Simulation"
    :status-text="shellStatusText"
    :status-tone="shellStatusTone"
    :logs="visibleLogs"
    :scenario="scenario"
    back-path="/demo/population"
    initial-mode="split"
    initial-layout-mode="split"
    console-id="demo_simulation"
  >
    <template #left>
      <GraphPanel
        :graph-data="currentPack.graph.graphData"
        :loading="false"
        :current-phase="3"
        :is-simulating="running"
      />
    </template>

    <template #right>
      <div class="demo-simulation">
        <div class="demo-simulation__toolbar">
          <div class="demo-simulation__communities">
            <article class="demo-simulation__community">
              <div class="demo-simulation__community-title">{{ currentPack.simulation.communityA.name }}</div>
              <div class="demo-simulation__community-meta">
                <span>Round {{ visibleRound }}/40</span>
                <span>Acts {{ visibleActsA }}</span>
              </div>
            </article>
            <article class="demo-simulation__community">
              <div class="demo-simulation__community-title">{{ currentPack.simulation.communityB.name }}</div>
              <div class="demo-simulation__community-meta">
                <span>Round {{ visibleRound }}/40</span>
                <span>Acts {{ visibleActsB }}</span>
              </div>
            </article>
          </div>

          <button
            v-if="completed"
            class="demo-simulation__header-cta"
            type="button"
            @click="goNext"
          >
            Generate Report ->
          </button>
        </div>

        <div class="demo-simulation__summary">
          <span class="demo-simulation__summary-pill">Total Events: {{ totalEvents }}</span>
          <span class="demo-simulation__summary-pill">{{ visibleActions.length }} surfaced actions</span>
          <span class="demo-simulation__summary-pill">Graph sync {{ completed ? '100%' : `${Math.max(12, visibleRound * 2)}%` }}</span>
        </div>

        <div class="demo-simulation__workspace">
          <section class="demo-simulation__focus" v-if="latestAction">
            <div class="demo-simulation__focus-header">
              <span>{{ latestAction.platform === 'plaza' ? currentPack.simulation.communityA.name : currentPack.simulation.communityB.name }}</span>
              <span>{{ latestAction.round }} / {{ latestAction.time }}</span>
            </div>
            <div class="demo-simulation__focus-role">{{ latestAction.role }}</div>
            <h2 class="demo-simulation__focus-actor">{{ latestAction.actor }}</h2>
            <p class="demo-simulation__focus-text">{{ latestAction.text }}</p>
            <div class="demo-simulation__focus-tag">{{ latestAction.kind }}</div>
          </section>

          <section class="demo-simulation__feed">
            <article
              v-for="action in visibleActions"
              :key="action.id"
              class="demo-simulation__event"
            >
              <div class="demo-simulation__event-meta">
                <span>{{ action.actor }}</span>
                <span>{{ action.role }}</span>
                <span>{{ action.time }}</span>
              </div>
              <div class="demo-simulation__event-kind">{{ action.kind }}</div>
              <p class="demo-simulation__event-text">{{ action.text }}</p>
            </article>
          </section>
        </div>

        <button
          v-if="!running && !completed"
          class="demo-simulation__cta"
          type="button"
          @click="startSimulation"
        >
          Start Simulation ->
        </button>

        <button
          v-else-if="running"
          class="demo-simulation__cta demo-simulation__cta--disabled"
          type="button"
          disabled
        >
          Still processing some content...
        </button>

        <div v-if="running" class="demo-simulation__toast">
          <span class="demo-simulation__toast-dot" />
          Still processing some content...
        </div>
      </div>
    </template>
  </DemoWorkspaceShell>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GraphPanel from '../../components/GraphPanel.vue'
import DemoWorkspaceShell from '../../components/demo/DemoWorkspaceShell.vue'
import { useDemoRoute } from '../../composables/useDemoRoute'
import { demoState, setSimulationState } from '../../store/demoFlow'

const route = useRoute()
const router = useRouter()
const { loading, currentPack, scenario, demoQuery } = useDemoRoute(route, router, 'simulation')

const running = ref(false)
const completed = ref(demoState.simulationCompleted)
const visibleCount = ref(0)
const visibleRound = ref(0)
const visibleActsA = ref(0)
const visibleActsB = ref(0)
const logCount = ref(1)
const timers = []

watch(
  currentPack,
  pack => {
    if (demoState.simulationCompleted) {
      visibleCount.value = pack.simulation.actions.length
      visibleRound.value = 40
      visibleActsA.value = pack.simulation.communityA.acts
      visibleActsB.value = pack.simulation.communityB.acts
      logCount.value = pack.simulation.logs.length
    }
  },
  { immediate: true }
)

if (!demoState.simulationCompleted && demoState.simulationStarted) {
  setSimulationState({ started: false, completed: false })
}

const visibleActions = computed(() => currentPack.value.simulation.actions.slice(0, visibleCount.value))
const visibleLogs = computed(() => currentPack.value.simulation.logs.slice(0, logCount.value))
const latestAction = computed(() => visibleActions.value[visibleActions.value.length - 1] || null)
const totalEvents = computed(() => visibleActsA.value + visibleActsB.value)
const shellStatusText = computed(() => {
  if (completed.value) return 'Completed'
  if (running.value) return 'Processing'
  return 'Ready'
})
const shellStatusTone = computed(() => {
  if (completed.value) return 'completed'
  if (running.value) return 'processing'
  return 'ready'
})

function clearTimers() {
  while (timers.length) {
    window.clearTimeout(timers.pop())
  }
}

function startSimulation() {
  if (running.value || completed.value) return

  clearTimers()
  running.value = true
  setSimulationState({ started: true, completed: false })
  logCount.value = 1

  currentPack.value.simulation.actions.forEach((action, index) => {
    const timer = window.setTimeout(() => {
      visibleCount.value = index + 1
      visibleRound.value = Math.min(40, (index + 1) * 7)
      visibleActsA.value = Math.round(
        currentPack.value.simulation.communityA.acts * ((index + 1) / currentPack.value.simulation.actions.length)
      )
      visibleActsB.value = Math.round(
        currentPack.value.simulation.communityB.acts * ((index + 1) / currentPack.value.simulation.actions.length)
      )
      logCount.value = Math.min(currentPack.value.simulation.logs.length, index + 2)
    }, index * 900)
    timers.push(timer)
  })

  const completeTimer = window.setTimeout(() => {
    running.value = false
    completed.value = true
    visibleCount.value = currentPack.value.simulation.actions.length
    visibleRound.value = 40
    visibleActsA.value = currentPack.value.simulation.communityA.acts
    visibleActsB.value = currentPack.value.simulation.communityB.acts
    logCount.value = currentPack.value.simulation.logs.length
    setSimulationState({ started: true, completed: true })
  }, currentPack.value.simulation.actions.length * 900 + 400)

  timers.push(completeTimer)
}

function goNext() {
  router.push({
    path: '/demo/report',
    query: demoQuery.value,
  })
}

onBeforeUnmount(() => {
  clearTimers()
})
</script>

<style scoped>
.demo-simulation {
  height: 100%;
  overflow: auto;
  padding: 22px;
  background: #fbfbfb;
}

.demo-simulation__toolbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.demo-simulation__communities {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  flex: 1;
}

.demo-simulation__community {
  padding: 18px;
  border: 1px solid #00a870;
  border-radius: 12px;
  background: #fff;
}

.demo-simulation__community-title {
  font-size: 20px;
  font-weight: 900;
}

.demo-simulation__community-meta {
  display: flex;
  gap: 14px;
  margin-top: 10px;
  color: #6b6b6b;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 13px;
}

.demo-simulation__header-cta {
  min-width: 220px;
  padding: 20px 22px;
  border: none;
  border-radius: 10px;
  background: #050505;
  color: #fff;
  font-size: 17px;
  font-weight: 800;
  cursor: pointer;
}

.demo-simulation__summary {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin: 18px 0 0;
}

.demo-simulation__summary-pill {
  display: inline-flex;
  align-items: center;
  padding: 10px 14px;
  border-radius: 999px;
  background: #f1f1f1;
  color: #585858;
  font-size: 12px;
  font-weight: 700;
}

.demo-simulation__workspace {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
  gap: 18px;
  margin-top: 20px;
}

.demo-simulation__focus {
  padding: 22px;
  border: 1px solid #dfe6ff;
  border-radius: 12px;
  background: #fff;
}

.demo-simulation__focus-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: #7c7c7c;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 12px;
  text-transform: uppercase;
}

.demo-simulation__focus-role {
  margin-top: 18px;
  color: #6f6f6f;
  font-size: 14px;
  text-transform: uppercase;
}

.demo-simulation__focus-actor {
  margin: 8px 0 0;
  font-size: 28px;
  line-height: 1.04;
}

.demo-simulation__focus-text {
  margin: 16px 0 0;
  font-size: 24px;
  line-height: 1.5;
}

.demo-simulation__focus-tag {
  display: inline-flex;
  margin-top: 18px;
  padding: 8px 12px;
  border-radius: 999px;
  background: #f6f7fb;
  color: #0052ff;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.demo-simulation__feed {
  display: grid;
  gap: 16px;
  align-content: start;
}

.demo-simulation__event {
  padding: 18px;
  border: 1px solid #e9e9e9;
  border-radius: 12px;
  background: #fff;
}

.demo-simulation__event-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: #7c7c7c;
  font-size: 13px;
  text-transform: uppercase;
}

.demo-simulation__event-kind {
  margin-top: 10px;
  font-size: 14px;
  font-weight: 900;
}

.demo-simulation__event-text {
  margin: 10px 0 0;
  font-size: 17px;
  line-height: 1.55;
}

.demo-simulation__cta {
  width: 100%;
  margin-top: 18px;
  padding: 18px 20px;
  border: none;
  border-radius: 10px;
  background: #050505;
  color: #fff;
  font-size: 17px;
  font-weight: 800;
  cursor: pointer;
}

.demo-simulation__cta--disabled {
  background: #5c5c5c;
  cursor: not-allowed;
}

.demo-simulation__toast {
  position: sticky;
  left: 0;
  bottom: 0;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-top: 18px;
  padding: 14px 18px;
  border-radius: 999px;
  background: rgba(84, 84, 84, 0.92);
  color: #fff;
  width: fit-content;
  font-size: 14px;
  font-weight: 700;
}

.demo-simulation__toast-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #fff;
  opacity: 0.9;
}

@media (max-width: 1120px) {
  .demo-simulation__workspace {
    grid-template-columns: 1fr;
  }
}
</style>
