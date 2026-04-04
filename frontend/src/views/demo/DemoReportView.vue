<template>
  <DemoWorkspaceShell
    v-if="!loading"
    :step-number="4"
    step-name="Report"
    status-text="Generating"
    status-tone="processing"
    :logs="currentPack.report.logs"
    :scenario="scenario"
    back-path="/demo/simulation"
    initial-mode="workbench"
    initial-layout-mode="split"
    console-label="CONSOLE OUTPUT"
    console-id="demo_report"
  >
    <template #left>
      <article class="demo-report">
        <div class="demo-report__header">
          <div class="demo-report__eyebrow">Prediction Report</div>
          <div class="demo-report__id">ID: {{ reportIdentifier }}</div>
        </div>
        <h1 class="demo-report__title">{{ currentPack.report.title }}</h1>
        <p class="demo-report__summary">{{ currentPack.report.summary }}</p>

        <section
          v-for="(section, index) in currentPack.report.sections"
          :key="section.title"
          class="demo-report__section"
        >
          <div class="demo-report__section-number">{{ String(index + 1).padStart(2, '0') }}</div>
          <div class="demo-report__section-body">
            <h2 class="demo-report__section-title">{{ section.title }}</h2>
            <p
              v-for="paragraph in section.paragraphs"
              :key="paragraph"
              class="demo-report__paragraph"
            >
              {{ paragraph }}
            </p>
          </div>
        </section>
      </article>
    </template>

    <template #right>
      <div class="demo-workbench">
        <section class="demo-workbench__status-panel">
          <div class="demo-workbench__status-top">
            <div class="demo-workbench__status-title">OK · COMPLETE</div>
            <div class="demo-workbench__status-chip">Section 1/{{ currentPack.report.sections.length }}</div>
          </div>

          <div class="demo-workbench__status-list">
            <article
              v-for="(item, index) in currentPack.report.workbench"
              :key="`status-${item.title}`"
              class="demo-workbench__status-row"
            >
              <span class="demo-workbench__status-index">{{ String(index + 1).padStart(2, '0') }}</span>
              <span class="demo-workbench__status-text">{{ item.title }}</span>
              <span class="demo-workbench__status-check">+</span>
            </article>
          </div>
        </section>

        <section class="demo-workbench__timeline">
          <article
            v-for="entry in workbenchEntries"
            :key="entry.key"
            class="demo-workbench__trace"
            :class="`demo-workbench__trace--${entry.tone}`"
          >
            <div class="demo-workbench__trace-meta">
              <span class="demo-workbench__trace-type">{{ entry.kind }}</span>
              <span class="demo-workbench__trace-time">{{ entry.elapsed }}</span>
            </div>

            <div class="demo-workbench__trace-header">
              <div class="demo-workbench__trace-label">{{ entry.label }}</div>
              <button class="demo-workbench__trace-toggle" type="button">
                {{ entry.toggleLabel }}
              </button>
            </div>

            <h2 class="demo-workbench__trace-title">{{ entry.title }}</h2>
            <p class="demo-workbench__trace-detail">{{ entry.detail }}</p>

            <div v-if="entry.points?.length" class="demo-workbench__trace-points">
              <article
                v-for="point in entry.points"
                :key="point"
                class="demo-workbench__trace-point"
              >
                {{ point }}
              </article>
            </div>
          </article>
        </section>

        <button class="demo-workbench__cta" type="button" @click="goNext">
          Open Deep Interaction ->
        </button>
      </div>
    </template>
  </DemoWorkspaceShell>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DemoWorkspaceShell from '../../components/demo/DemoWorkspaceShell.vue'
import { useDemoRoute } from '../../composables/useDemoRoute'

const route = useRoute()
const router = useRouter()
const { loading, currentPack, scenario, demoQuery } = useDemoRoute(route, router, 'report')

const reportIdentifier = computed(() => `report_${currentPack.value.countryCode.toLowerCase()}_${currentPack.value.key}`)
const workbenchEntries = computed(() => {
  const sectionTitles = currentPack.value.report.sections.map(section => section.title)
  const sectionHighlights = currentPack.value.report.sections.map(section => section.paragraphs[0])
  const personaSignals = currentPack.value.population.personas.map(persona => `${persona.name}: ${persona.trait}`)

  const entryMeta = [
    {
      kind: 'LLM RESPONSE',
      tone: 'neutral',
      elapsed: '+72.5s',
      toggleLabel: 'Hide response',
      points: sectionTitles,
    },
    {
      kind: 'TOOL CALL',
      tone: 'blue',
      elapsed: '+120.4s',
      toggleLabel: 'Show params',
      points: personaSignals,
    },
    {
      kind: 'TOOL RESULT',
      tone: 'orange',
      elapsed: '+166.8s',
      toggleLabel: 'Raw output',
      points: sectionHighlights,
    },
    {
      kind: 'LLM RESPONSE',
      tone: 'green',
      elapsed: '+208.1s',
      toggleLabel: 'Hide response',
      points: ['Draft package compiled.', 'Evidence chain linked.', 'Workbench trace preserved.'],
    },
  ]

  return currentPack.value.report.workbench.map((item, index) => ({
    key: `${item.label}-${index}`,
    ...entryMeta[index],
    ...item,
  }))
})

const goNext = () => {
  router.push({
    path: '/demo/interaction',
    query: demoQuery.value,
  })
}
</script>

<style scoped>
.demo-report {
  height: 100%;
  overflow: auto;
  padding: 34px 38px 44px;
  background: #fff;
}

.demo-report__header {
  display: flex;
  align-items: center;
  gap: 14px;
}

.demo-report__eyebrow {
  display: inline-flex;
  padding: 6px 10px;
  background: #050505;
  color: #fff;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.demo-report__id {
  color: #9a9a9a;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 13px;
}

.demo-report__title {
  margin: 24px 0 0;
  max-width: 780px;
  font-family: 'Source Serif 4', Georgia, serif;
  font-size: clamp(42px, 4.5vw, 66px);
  line-height: 1.05;
  letter-spacing: -0.03em;
}

.demo-report__summary {
  margin: 24px 0 0;
  max-width: 760px;
  color: #5c5c5c;
  font-family: 'Source Serif 4', Georgia, serif;
  font-size: 25px;
  line-height: 1.6;
}

.demo-report__section {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 18px;
  margin-top: 44px;
  padding-top: 24px;
  border-top: 1px solid #ebebeb;
}

.demo-report__section-number {
  color: #b5b5b5;
  font-size: 28px;
  font-weight: 900;
}

.demo-report__section-title {
  margin: 0;
  font-family: 'Source Serif 4', Georgia, serif;
  font-size: 38px;
  line-height: 1.16;
}

.demo-report__paragraph {
  margin: 20px 0 0;
  max-width: 720px;
  font-size: 21px;
  line-height: 1.7;
}

.demo-workbench {
  height: 100%;
  overflow: auto;
  padding: 18px 20px 30px;
  background: #fbfbfb;
}

.demo-workbench__status-panel {
  padding: 16px;
  border: 1px solid #e7e7e7;
  border-radius: 12px;
  background: #fff;
}

.demo-workbench__status-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.demo-workbench__status-title {
  font-size: 14px;
  font-weight: 900;
  text-transform: uppercase;
}

.demo-workbench__status-chip {
  padding: 6px 10px;
  border-radius: 999px;
  background: #202934;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}

.demo-workbench__status-list {
  margin-top: 14px;
}

.demo-workbench__status-row {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr) 22px;
  align-items: center;
  gap: 12px;
  padding: 14px 12px;
  border: 1px solid #ececec;
  border-radius: 10px;
  background: #fbfbfb;
}

.demo-workbench__status-row + .demo-workbench__status-row {
  margin-top: 10px;
}

.demo-workbench__status-index {
  color: #0052ff;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 12px;
  text-transform: uppercase;
}

.demo-workbench__status-text {
  font-size: 15px;
  font-weight: 700;
}

.demo-workbench__status-check {
  color: #15a35b;
  font-size: 22px;
  font-weight: 900;
}

.demo-workbench__timeline {
  margin-top: 16px;
}

.demo-workbench__trace {
  padding: 18px;
  border: 1px solid #e7e7e7;
  border-radius: 12px;
  background: #fff;
}

.demo-workbench__trace + .demo-workbench__trace {
  margin-top: 14px;
}

.demo-workbench__trace--blue {
  border-color: #d7e5ff;
}

.demo-workbench__trace--orange {
  border-color: #ffd8c2;
}

.demo-workbench__trace--green {
  border-color: #d7f0e0;
}

.demo-workbench__trace-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #8f8f8f;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 11px;
  text-transform: uppercase;
}

.demo-workbench__trace-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 14px;
}

.demo-workbench__trace-label {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  background: #f4f4f4;
  color: #4d4d4d;
  font-size: 12px;
  font-weight: 800;
}

.demo-workbench__trace-toggle {
  border: 1px solid #e2e2e2;
  border-radius: 6px;
  background: #fff;
  color: #7d7d7d;
  font-size: 11px;
  font-weight: 700;
  padding: 6px 9px;
  cursor: default;
}

.demo-workbench__trace-title {
  margin: 12px 0 0;
  font-size: 24px;
  line-height: 1.12;
}

.demo-workbench__trace-detail {
  margin: 10px 0 0;
  font-size: 16px;
  line-height: 1.6;
}

.demo-workbench__trace-points {
  margin-top: 16px;
}

.demo-workbench__trace-point {
  padding: 12px 14px;
  border: 1px solid #ececec;
  border-radius: 10px;
  background: #fafafa;
  font-size: 14px;
  line-height: 1.5;
}

.demo-workbench__trace-point + .demo-workbench__trace-point {
  margin-top: 8px;
}

.demo-workbench__cta {
  width: 100%;
  margin-top: 16px;
  padding: 18px 20px;
  border: none;
  border-radius: 10px;
  background: #050505;
  color: #fff;
  font-size: 18px;
  font-weight: 800;
  cursor: pointer;
}

@media (max-width: 1280px) {
  .demo-report__title {
    font-size: clamp(36px, 4vw, 56px);
  }

  .demo-report__summary {
    font-size: 22px;
  }

  .demo-report__section-title {
    font-size: 32px;
  }

  .demo-report__paragraph {
    font-size: 19px;
  }
}
</style>
