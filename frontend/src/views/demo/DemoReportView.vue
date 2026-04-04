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
        <div class="demo-report__eyebrow">Prediction Report</div>
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
        <article
          v-for="(item, index) in currentPack.report.workbench"
          :key="item.title"
          class="demo-workbench__item"
        >
          <div class="demo-workbench__label">{{ String(index + 1).padStart(2, '0') }} / {{ item.label }}</div>
          <h2 class="demo-workbench__title">{{ item.title }}</h2>
          <p class="demo-workbench__detail">{{ item.detail }}</p>
        </article>

        <button class="demo-workbench__cta" type="button" @click="goNext">
          Open Deep Interaction ->
        </button>
      </div>
    </template>
  </DemoWorkspaceShell>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import DemoWorkspaceShell from '../../components/demo/DemoWorkspaceShell.vue'
import { useDemoRoute } from '../../composables/useDemoRoute'

const route = useRoute()
const router = useRouter()
const { loading, currentPack, scenario, demoQuery } = useDemoRoute(route, router, 'report')

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

.demo-report__eyebrow {
  display: inline-flex;
  padding: 6px 10px;
  background: #050505;
  color: #fff;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
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

.demo-workbench__item {
  padding: 18px;
  border: 1px solid #e7e7e7;
  border-radius: 12px;
  background: #fff;
}

.demo-workbench__item + .demo-workbench__item {
  margin-top: 14px;
}

.demo-workbench__label {
  color: #6a6a6a;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 12px;
  text-transform: uppercase;
}

.demo-workbench__title {
  margin: 12px 0 0;
  font-size: 26px;
  line-height: 1.08;
}

.demo-workbench__detail {
  margin: 12px 0 0;
  font-size: 17px;
  line-height: 1.55;
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
</style>
