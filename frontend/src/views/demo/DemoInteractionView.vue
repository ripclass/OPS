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
        <div class="demo-report__header">
          <div class="demo-report__eyebrow">Prediction Report</div>
          <div class="demo-report__id">ID: {{ reportIdentifier }}</div>
        </div>
        <h1 class="demo-report__title">{{ currentPack.report.title }}</h1>
        <p class="demo-report__summary">{{ currentPack.report.summary }}</p>
      </article>
    </template>

    <template #right>
      <div class="demo-interaction">
        <section class="demo-interaction__toolbar">
          <button class="demo-interaction__tab demo-interaction__tab--active" type="button">
            Report Agent
          </button>
          <button class="demo-interaction__tab" type="button">
            Interview a simulated person
          </button>
        </section>

        <div class="demo-interaction__workspace">
          <section class="demo-thread">
            <div class="demo-thread__header">
              <div>
                <div class="demo-thread__title">OPS Report Agent</div>
                <div class="demo-thread__subtitle">Interrogate the report, trace evidence, and pressure-test conclusions.</div>
              </div>
              <div class="demo-thread__chip">3 tools online</div>
            </div>

            <div class="demo-thread__messages">
              <article
                v-for="(message, index) in currentPack.interaction.reportAgentMessages"
                :key="`${message.role}-${index}`"
                class="demo-thread__message"
                :class="`demo-thread__message--${message.role}`"
              >
                <div class="demo-thread__role">{{ message.role === 'assistant' ? 'Report Agent' : 'Operator' }}</div>
                <p>{{ message.text }}</p>
              </article>
            </div>

            <div class="demo-thread__composer">
              <div class="demo-thread__composer-label">Ask the report agent</div>
              <div class="demo-thread__composer-shell">
                <span class="demo-thread__composer-prompt">&gt;_</span>
                <span class="demo-thread__composer-text">What makes the issue spread before the ministry clarifies it?</span>
                <button class="demo-thread__composer-send" type="button">Send</button>
              </div>
            </div>
          </section>

          <aside class="demo-agents">
            <div class="demo-agents__header">
              <div class="demo-thread__title">Interviewable People</div>
              <div class="demo-agents__count">{{ currentPack.interaction.interviewAgents.length }} loaded</div>
            </div>

            <div class="demo-agents__list">
              <button
                v-for="(agent, index) in currentPack.interaction.interviewAgents"
                :key="agent.name"
                class="demo-agent"
                :class="{ 'demo-agent--active': index === selectedAgentIndex }"
                type="button"
                @click="selectedAgentIndex = index"
              >
                <div class="demo-agent__avatar">{{ agent.name[0] }}</div>
                <div class="demo-agent__body">
                  <div class="demo-agent__name">{{ agent.name }}</div>
                  <div class="demo-agent__role">{{ agent.role }}</div>
                </div>
              </button>
            </div>

            <article v-if="selectedAgent" class="demo-agent-card">
              <div class="demo-agent-card__label">Selected interview subject</div>
              <h2 class="demo-agent-card__name">{{ selectedAgent.name }}</h2>
              <div class="demo-agent-card__role">{{ selectedAgent.role }}</div>
              <p class="demo-agent-card__response">{{ selectedAgent.response }}</p>
            </article>
          </aside>
        </div>

        <button class="demo-interaction__cta" type="button" @click="handleFinalAction">
          {{ finalCtaLabel }} ->
        </button>
      </div>
    </template>
  </DemoWorkspaceShell>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DemoWorkspaceShell from '../../components/demo/DemoWorkspaceShell.vue'
import { useDemoRoute } from '../../composables/useDemoRoute'
import { authState } from '../../store/auth'

const route = useRoute()
const router = useRouter()
const { loading, currentPack, scenario } = useDemoRoute(route, router, 'interaction')
const selectedAgentIndex = ref(0)

const finalCtaLabel = computed(() => (
  authState.user ? 'Open console with this brief' : 'Sign up to run the real scenario'
))
const selectedAgent = computed(() => currentPack.value.interaction.interviewAgents[selectedAgentIndex.value] || null)
const reportIdentifier = computed(() => `report_${currentPack.value.countryCode.toLowerCase()}_${currentPack.value.key}`)

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

.demo-report__header {
  display: flex;
  align-items: center;
  gap: 14px;
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

.demo-report__id {
  color: #9a9a9a;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 13px;
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

.demo-interaction__toolbar {
  display: flex;
  gap: 10px;
}

.demo-interaction__tab {
  border: 1px solid #e2e2e2;
  border-radius: 999px;
  background: #fff;
  color: #4f4f4f;
  font-size: 13px;
  font-weight: 700;
  padding: 10px 15px;
  cursor: default;
}

.demo-interaction__tab--active {
  background: #111;
  border-color: #111;
  color: #fff;
}

.demo-interaction__workspace {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(290px, 0.9fr);
  gap: 16px;
  margin-top: 16px;
}

.demo-thread,
.demo-agents {
  padding: 18px;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  background: #fff;
}

.demo-thread__header,
.demo-agents__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.demo-thread__title {
  margin: 0;
  font-size: 22px;
}

.demo-thread__subtitle {
  margin-top: 6px;
  color: #707070;
  font-size: 14px;
  line-height: 1.45;
}

.demo-thread__chip {
  padding: 7px 10px;
  border-radius: 999px;
  background: #f3f6ff;
  color: #0052ff;
  font-size: 12px;
  font-weight: 800;
  white-space: nowrap;
}

.demo-thread__messages {
  margin-top: 16px;
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

.demo-thread__message p {
  margin: 10px 0 0;
  font-size: 17px;
  line-height: 1.55;
}

.demo-thread__composer {
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid #ececec;
}

.demo-thread__composer-label {
  color: #777;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 12px;
  text-transform: uppercase;
}

.demo-thread__composer-shell {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
  padding: 14px 14px 14px 16px;
  border: 1px solid #e5e5e5;
  border-radius: 10px;
  background: #fafafa;
}

.demo-thread__composer-prompt {
  color: #0052ff;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 13px;
  font-weight: 700;
}

.demo-thread__composer-text {
  flex: 1;
  color: #565656;
  font-size: 15px;
  line-height: 1.45;
}

.demo-thread__composer-send {
  border: none;
  border-radius: 8px;
  background: #050505;
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  padding: 10px 14px;
  cursor: default;
}

.demo-agents__count {
  color: #7b7b7b;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 12px;
  white-space: nowrap;
}

.demo-agents__list {
  margin-top: 14px;
}

.demo-agent {
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr);
  gap: 12px;
  width: 100%;
  margin: 0;
  padding: 12px;
  border: 1px solid #ececec;
  border-radius: 10px;
  background: #fafafa;
  cursor: pointer;
  text-align: left;
}

.demo-agent + .demo-agent {
  margin-top: 10px;
}

.demo-agent--active {
  border-color: #dce7ff;
  background: #f6f9ff;
}

.demo-agent__avatar {
  width: 40px;
  height: 40px;
  border-radius: 999px;
  background: #121212;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 800;
}

.demo-agent__body {
  min-width: 0;
}

.demo-agent__name {
  margin: 0;
  font-size: 22px;
  font-weight: 900;
}

.demo-agent__role {
  margin-top: 4px;
}

.demo-agent-card {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid #ececec;
  border-radius: 12px;
  background: #fbfbfb;
}

.demo-agent-card__label {
  color: #777;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 12px;
  text-transform: uppercase;
}

.demo-agent-card__name {
  margin: 14px 0 0;
  font-size: 32px;
  line-height: 1.05;
}

.demo-agent-card__role {
  margin-top: 8px;
  color: #6d6d6d;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
  font-size: 12px;
  text-transform: uppercase;
}

.demo-agent-card__response {
  margin: 14px 0 0;
  font-size: 17px;
  line-height: 1.58;
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

@media (max-width: 1220px) {
  .demo-interaction__workspace {
    grid-template-columns: 1fr;
  }

  .demo-agent__name {
    font-size: 18px;
  }

  .demo-agent-card__name {
    font-size: 26px;
  }
}
</style>
