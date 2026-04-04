<template>
  <DemoWorkspaceShell
    v-if="!loading"
    :step-number="2"
    step-name="Population Setup"
    status-text="Ready"
    status-tone="ready"
    :logs="currentPack.population.logs"
    :scenario="scenario"
    back-path="/demo/graph"
    initial-mode="split"
    initial-layout-mode="split"
    console-id="demo_population"
  >
    <template #left>
      <GraphPanel
        :graph-data="currentPack.graph.graphData"
        :loading="false"
        :current-phase="2"
      />
    </template>

    <template #right>
      <div class="demo-population">
        <section class="demo-population__card">
          <div class="demo-population__row">
            <div>
              <div class="demo-population__kicker">01 / Runtime Context</div>
              <h2 class="demo-population__title">Static Demo Initialization</h2>
              <div class="demo-population__meta-line">PACK / {{ currentPack.countryLabel.toUpperCase() }} / {{ currentPack.population.simulationId }}</div>
            </div>
            <span class="demo-population__status">Ready</span>
          </div>
          <dl class="demo-population__meta">
            <div><dt>Run ID</dt><dd>{{ currentPack.population.runId }}</dd></div>
            <div><dt>Graph ID</dt><dd>{{ currentPack.population.graphId }}</dd></div>
            <div><dt>Simulation ID</dt><dd>{{ currentPack.population.simulationId }}</dd></div>
          </dl>
        </section>

        <section class="demo-population__card">
          <div class="demo-population__kicker">02 / Population Notes</div>
          <ul class="demo-population__notes">
            <li v-for="note in currentPack.population.notes" :key="note">{{ note }}</li>
          </ul>
        </section>

        <section class="demo-population__card">
          <div class="demo-population__kicker">03 / Persona Seeds</div>
          <div class="demo-population__personas">
            <article
              v-for="persona in currentPack.population.personas"
              :key="persona.name"
              class="demo-population__persona"
            >
              <div class="demo-population__persona-name">{{ persona.name }}</div>
              <div class="demo-population__persona-role">{{ persona.role }}</div>
              <p class="demo-population__persona-detail">{{ persona.detail }}</p>
              <div class="demo-population__persona-trait">{{ persona.trait }}</div>
            </article>
          </div>
        </section>

        <button class="demo-population__cta" type="button" @click="goNext">
          Go to Simulation ->
        </button>
      </div>
    </template>
  </DemoWorkspaceShell>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import GraphPanel from '../../components/GraphPanel.vue'
import DemoWorkspaceShell from '../../components/demo/DemoWorkspaceShell.vue'
import { useDemoRoute } from '../../composables/useDemoRoute'
import { resetSimulationState } from '../../store/demoFlow'

const route = useRoute()
const router = useRouter()
const { loading, currentPack, scenario, demoQuery } = useDemoRoute(route, router, 'population')

const goNext = () => {
  resetSimulationState()
  router.push({
    path: '/demo/simulation',
    query: demoQuery.value,
  })
}
</script>

<style scoped>
.demo-population {
  height: 100%;
  overflow: auto;
  padding: 24px;
  background: #fbfbfb;
}

.demo-population__card {
  padding: 22px;
  border: 1px solid #e8e8e8;
  border-radius: 14px;
  background: #fff;
}

.demo-population__card + .demo-population__card {
  margin-top: 18px;
}

.demo-population__row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.demo-population__kicker,
.demo-population__meta-line {
  color: #888;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 13px;
}

.demo-population__meta-line {
  margin-top: 10px;
}

.demo-population__title {
  margin: 10px 0 0;
  font-size: 34px;
  line-height: 1.04;
}

.demo-population__status {
  padding: 6px 10px;
  border-radius: 999px;
  background: #eef8ef;
  color: #3a8f48;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.demo-population__meta {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin: 18px 0 0;
}

.demo-population__meta dt {
  color: #8d8d8d;
  font-size: 12px;
  text-transform: uppercase;
}

.demo-population__meta dd {
  margin: 6px 0 0;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 15px;
}

.demo-population__notes {
  margin: 14px 0 0;
  padding-left: 22px;
  font-size: 18px;
  line-height: 1.6;
}

.demo-population__notes li + li {
  margin-top: 10px;
}

.demo-population__personas {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 18px;
}

.demo-population__persona {
  padding: 16px;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  background: #fafafa;
}

.demo-population__persona-name {
  font-size: 24px;
  font-weight: 900;
}

.demo-population__persona-role {
  margin-top: 4px;
  color: #0052ff;
  font-size: 15px;
  font-weight: 800;
}

.demo-population__persona-detail,
.demo-population__persona-trait {
  margin: 10px 0 0;
  font-size: 16px;
  line-height: 1.5;
}

.demo-population__cta {
  width: 100%;
  margin-top: 20px;
  padding: 18px 20px;
  border: none;
  border-radius: 10px;
  background: #050505;
  color: #fff;
  font-size: 18px;
  font-weight: 800;
  cursor: pointer;
}
</style>
