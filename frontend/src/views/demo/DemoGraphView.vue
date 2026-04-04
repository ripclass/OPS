<template>
  <DemoWorkspaceShell
    v-if="!loading"
    :step-number="1"
    step-name="Graph Build"
    status-text="Ready"
    status-tone="ready"
    :logs="currentPack.graph.logs"
    :scenario="scenario"
    back-path="/demo"
    initial-mode="split"
    initial-layout-mode="split"
    console-id="demo_graph"
  >
    <template #left>
      <GraphPanel
        :graph-data="currentPack.graph.graphData"
        :loading="false"
        :current-phase="2"
      />
    </template>

    <template #right>
      <div class="demo-step-panel">
        <article class="demo-card">
          <div class="demo-card__header">
            <div>
              <div class="demo-card__number">01</div>
              <h2 class="demo-card__title">Ontology Generation</h2>
              <div class="demo-card__meta">POST /api/graph/ontology/generate</div>
            </div>
            <span class="demo-card__status">Build Complete</span>
          </div>
          <p class="demo-card__body">
            Murmur reads the scenario brief, extracts public actors, locations, institutions, and pressure points, then stages an ontology for the simulated public sphere.
          </p>
          <div class="demo-card__group-label">Generated Entity Types</div>
          <div class="demo-pill-list">
            <span v-for="type in currentPack.graph.entityTypes" :key="type" class="demo-pill">{{ type }}</span>
          </div>
          <div class="demo-card__group-label demo-card__group-label--spaced">Generated Relation Types</div>
          <div class="demo-pill-list">
            <span v-for="type in currentPack.graph.relationTypes" :key="type" class="demo-pill">{{ type }}</span>
          </div>
        </article>

        <article class="demo-card">
          <div class="demo-card__header">
            <div>
              <div class="demo-card__number">02</div>
              <h2 class="demo-card__title">GraphRAG Build</h2>
              <div class="demo-card__meta">POST /api/graph/build</div>
            </div>
            <span class="demo-card__status">Build Complete</span>
          </div>
          <p class="demo-card__body">
            Country priors, community summaries, and relation paths are assembled into a graph memory layer that the downstream simulation will query in motion.
          </p>
          <div class="demo-stats">
            <div class="demo-stat">
              <span class="demo-stat__value">{{ currentPack.graph.stats.nodes }}</span>
              <span class="demo-stat__label">Entity Nodes</span>
            </div>
            <div class="demo-stat">
              <span class="demo-stat__value">{{ currentPack.graph.stats.edges }}</span>
              <span class="demo-stat__label">Relation Edges</span>
            </div>
            <div class="demo-stat">
              <span class="demo-stat__value">{{ currentPack.graph.stats.types }}</span>
              <span class="demo-stat__label">Schema Types</span>
            </div>
          </div>
        </article>

        <article class="demo-card demo-card--cta">
          <div class="demo-card__header">
            <div>
              <div class="demo-card__number">03</div>
              <h2 class="demo-card__title">Build Complete</h2>
              <div class="demo-card__meta">POST /api/simulation/create</div>
            </div>
            <span class="demo-card__status demo-card__status--accent">Ready for Step 2</span>
          </div>
          <p class="demo-card__body">
            The scenario graph is ready. Continue to population setup to stage Murmur's country-grounded agents and environment scaffolding.
          </p>
          <button class="demo-card__button" type="button" @click="goNext">
            Go to Population Setup ->
          </button>
        </article>
      </div>
    </template>
  </DemoWorkspaceShell>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import GraphPanel from '../../components/GraphPanel.vue'
import DemoWorkspaceShell from '../../components/demo/DemoWorkspaceShell.vue'
import { useDemoRoute } from '../../composables/useDemoRoute'

const route = useRoute()
const router = useRouter()
const { loading, currentPack, scenario, demoQuery } = useDemoRoute(route, router, 'graph')

const goNext = () => {
  router.push({
    path: '/demo/population',
    query: demoQuery.value,
  })
}
</script>

<style scoped>
.demo-step-panel {
  height: 100%;
  overflow: auto;
  padding: 24px;
  background: #fbfbfb;
}

.demo-card {
  padding: 22px;
  border: 1px solid #e8e8e8;
  border-radius: 14px;
  background: #fff;
}

.demo-card + .demo-card {
  margin-top: 20px;
}

.demo-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.demo-card__number {
  color: #b2b2b2;
  font-size: 34px;
  font-weight: 900;
  line-height: 1;
}

.demo-card__title {
  margin: 8px 0 0;
  font-size: 34px;
  line-height: 1.02;
}

.demo-card__meta {
  margin-top: 10px;
  color: #a1a1a1;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 12px;
}

.demo-card__status {
  padding: 6px 10px;
  border-radius: 999px;
  background: #eef8ef;
  color: #3a8f48;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.demo-card__body {
  margin: 18px 0 0;
  color: #444;
  font-size: 18px;
  line-height: 1.58;
}

.demo-card__group-label {
  margin-top: 20px;
  color: #9a9a9a;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 12px;
  text-transform: uppercase;
}

.demo-card__group-label--spaced {
  margin-top: 18px;
}

.demo-pill-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.demo-pill {
  padding: 10px 14px;
  border: 1px solid #e6e6e6;
  border-radius: 10px;
  background: #fafafa;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 14px;
}

.demo-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 18px;
  padding: 14px;
  border-radius: 12px;
  background: #fafafa;
}

.demo-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.demo-stat__value {
  font-size: 40px;
  font-weight: 900;
}

.demo-stat__label {
  color: #8b8b8b;
  font-size: 12px;
  text-transform: uppercase;
}

.demo-card--cta {
  border-color: #ff6b35;
  background: #fffaf7;
}

.demo-card__status--accent {
  background: #fff2eb;
  color: #ff6b35;
}

.demo-card__button {
  width: 100%;
  margin-top: 18px;
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
