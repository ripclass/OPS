<template>
  <DemoWorkspaceShell
    v-if="!loading"
    :step-number="5"
    step-name="Deep Interaction"
    status-text="Completed"
    status-tone="completed"
    :logs="currentPack.interaction.logs"
    :scenario="scenario"
    back-path="/demo/report"
    initial-mode="workbench"
    initial-layout-mode="split"
    console-label="INTERACTION LOG"
    console-id="demo_interaction"
  >
    <template #left>
      <article class="demo-report demo-report--condensed">
        <div class="demo-report__eyebrow">Prediction Report</div>
        <h1 class="demo-report__title">{{ currentPack.report.title }}</h1>
        <p class="demo-report__summary">{{ currentPack.report.summary }}</p>
      </article>
    </template>

    <template #right>
      <div class="demo-interaction">
        <section class="demo-thread">
          <h2 class="demo-thread__title">Report Agent</h2>
          <article
            v-for="(message, index) in currentPack.interaction.reportAgentMessages"
            :key="`${message.role}-${index}`"
            class="demo-thread__message"
            :class="`demo-thread__message--${message.role}`"
          >
            <div class="demo-thread__role">{{ message.role === 'assistant' ? 'Report Agent' : 'Operator' }}</div>
            <p>{{ message.text }}</p>
          </article>
        </section>

        <section class="demo-agents">
          <h2 class="demo-thread__title">Interviewable People</h2>
          <article
            v-for="agent in currentPack.interaction.interviewAgents"
            :key="agent.name"
            class="demo-agent"
          >
            <div class="demo-agent__name">{{ agent.name }}</div>
            <div class="demo-agent__role">{{ agent.role }}</div>
            <p class="demo-agent__response">{{ agent.response }}</p>
          </article>
        </section>

        <button class="demo-interaction__cta" type="button" @click="handleFinalAction">
          {{ finalCtaLabel }} ->
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
import { authState } from '../../store/auth'

const route = useRoute()
const router = useRouter()
const { loading, currentPack, scenario } = useDemoRoute(route, router, 'interaction')

const finalCtaLabel = computed(() => (
  authState.user ? 'Open console with this brief' : 'Sign up to run the real scenario'
))

const handleFinalAction = () => {
  const redirect = scenario.value
    ? `/console?scenario=${encodeURIComponent(scenario.value)}`
    : '/console'

  if (authState.user) {
    router.push(redirect)
    return
  }

  router.push({
    path: '/',
    query: {
      auth: 'signup',
      redirect,
    },
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

.demo-report--condensed {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
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
  max-width: 760px;
  font-family: 'Source Serif 4', Georgia, serif;
  font-size: clamp(38px, 4.3vw, 60px);
  line-height: 1.06;
}

.demo-report__summary {
  margin: 22px 0 0;
  max-width: 720px;
  color: #5a5a5a;
  font-family: 'Source Serif 4', Georgia, serif;
  font-size: 23px;
  line-height: 1.6;
}

.demo-interaction {
  height: 100%;
  overflow: auto;
  padding: 20px;
  background: #fbfbfb;
}

.demo-thread,
.demo-agents {
  padding: 18px;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  background: #fff;
}

.demo-agents {
  margin-top: 16px;
}

.demo-thread__title {
  margin: 0;
  font-size: 22px;
}

.demo-thread__message {
  margin-top: 14px;
  padding: 14px;
  border-radius: 10px;
  background: #f7f7f7;
}

.demo-thread__message--assistant {
  border-left: 4px solid #0052ff;
}

.demo-thread__message--user {
  border-left: 4px solid #050505;
}

.demo-thread__role,
.demo-agent__role {
  color: #6d6d6d;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 12px;
  text-transform: uppercase;
}

.demo-thread__message p,
.demo-agent__response {
  margin: 10px 0 0;
  font-size: 17px;
  line-height: 1.55;
}

.demo-agent + .demo-agent {
  margin-top: 14px;
}

.demo-agent__name {
  margin-top: 14px;
  font-size: 22px;
  font-weight: 900;
}

.demo-interaction__cta {
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
