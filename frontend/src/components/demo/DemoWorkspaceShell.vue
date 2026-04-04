<template>
  <div class="demo-shell">
    <header class="demo-shell__header">
      <div class="demo-shell__header-left">
        <button class="demo-shell__back" type="button" @click="handleBack">
          <span aria-hidden="true">←</span>
        </button>
        <button class="demo-shell__brand" type="button" @click="router.push('/')">
          Murmur
        </button>
      </div>

      <div class="demo-shell__header-center">
        <div class="demo-shell__switcher">
          <button
            v-for="mode in modes"
            :key="mode.key"
            class="demo-shell__switch"
            :class="{ 'demo-shell__switch--active': localMode === mode.key }"
            type="button"
            @click="localMode = mode.key"
          >
            {{ mode.label }}
          </button>
        </div>
      </div>

      <div class="demo-shell__header-right">
        <div class="demo-shell__step">
          <span class="demo-shell__step-count">Step {{ stepNumber }}/5</span>
          <span class="demo-shell__step-name">{{ stepName }}</span>
        </div>
        <div class="demo-shell__status" :class="`demo-shell__status--${statusTone}`">
          <span class="demo-shell__status-dot" />
          {{ statusText }}
        </div>
        <button
          v-if="authState.user"
          class="demo-shell__action"
          type="button"
          @click="openConsole"
        >
          Open console
        </button>
        <button
          v-else
          class="demo-shell__action demo-shell__action--ghost"
          type="button"
          @click="openLogin"
        >
          Login
        </button>
      </div>
    </header>

    <main class="demo-shell__body">
      <section
        v-if="localMode !== 'workbench'"
        class="demo-shell__panel demo-shell__panel--left"
        :style="leftPanelStyle"
      >
        <slot name="left" />
      </section>

      <section
        v-if="localMode !== 'graph'"
        class="demo-shell__panel demo-shell__panel--right"
        :style="rightPanelStyle"
      >
        <slot name="right" />
      </section>
    </main>

    <footer class="demo-shell__console">
      <div class="demo-shell__console-header">
        <span>{{ consoleLabel }}</span>
        <span>{{ consoleId }}</span>
      </div>
      <div class="demo-shell__console-body">
        <div v-for="(line, index) in logs" :key="`${index}-${line}`" class="demo-shell__console-line">
          {{ line }}
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { authState } from '../../store/auth'

const props = defineProps({
  stepNumber: {
    type: Number,
    required: true,
  },
  stepName: {
    type: String,
    required: true,
  },
  statusText: {
    type: String,
    required: true,
  },
  statusTone: {
    type: String,
    default: 'ready',
  },
  logs: {
    type: Array,
    default: () => [],
  },
  scenario: {
    type: String,
    default: '',
  },
  backPath: {
    type: String,
    default: '/demo',
  },
  defaultMode: {
    type: String,
    default: 'split',
  },
  consoleLabel: {
    type: String,
    default: 'SYSTEM DASHBOARD',
  },
  consoleId: {
    type: String,
    default: 'demo_murmur',
  },
})

const router = useRouter()
const localMode = ref(props.defaultMode)

watch(
  () => props.defaultMode,
  value => {
    localMode.value = value
  }
)

const modes = computed(() => [
  { key: 'graph', label: 'Graph' },
  { key: 'split', label: 'Split' },
  { key: 'workbench', label: 'Workbench' },
])

const leftPanelStyle = computed(() => {
  if (localMode.value === 'graph') {
    return { width: '100%' }
  }

  return { width: '50%' }
})

const rightPanelStyle = computed(() => {
  if (localMode.value === 'workbench') {
    return { width: '100%' }
  }

  return { width: '50%' }
})

const handleBack = () => {
  router.push(props.backPath)
}

const openConsole = () => {
  router.push({
    path: '/console',
    query: props.scenario ? { scenario: props.scenario } : {},
  })
}

const openLogin = () => {
  const redirect = props.scenario
    ? `/console?scenario=${encodeURIComponent(props.scenario)}`
    : '/console'

  router.push({
    path: '/',
    query: {
      auth: 'signin',
      redirect,
    },
  })
}
</script>

<style scoped>
.demo-shell {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #fff;
  color: #050505;
  overflow: hidden;
  font-family: var(--murmur-font-ui, 'Lato', system-ui, sans-serif);
}

.demo-shell__header {
  position: relative;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 22px;
  border-bottom: 1px solid #e6e6e6;
  background: #fff;
  z-index: 2;
}

.demo-shell__header-left,
.demo-shell__header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.demo-shell__header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.demo-shell__back,
.demo-shell__brand,
.demo-shell__action,
.demo-shell__switch {
  border: 1px solid #e0e0e0;
  background: #fff;
  color: #050505;
}

.demo-shell__back {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  font-size: 16px;
}

.demo-shell__brand {
  border: none;
  padding: 0;
  font-size: 30px;
  font-weight: 900;
  cursor: pointer;
}

.demo-shell__switcher {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  border-radius: 8px;
  background: #f4f4f4;
}

.demo-shell__switch {
  min-width: 68px;
  padding: 8px 14px;
  border: none;
  border-radius: 6px;
  background: transparent;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.demo-shell__switch--active {
  background: #fff;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.04);
}

.demo-shell__step {
  display: flex;
  gap: 6px;
  font-size: 13px;
  color: #8a8a8a;
}

.demo-shell__step-name {
  color: #050505;
  font-weight: 700;
}

.demo-shell__status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #6f6f6f;
}

.demo-shell__status-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #5fb36a;
}

.demo-shell__status--processing .demo-shell__status-dot {
  background: #ff6b35;
}

.demo-shell__status--completed .demo-shell__status-dot,
.demo-shell__status--ready .demo-shell__status-dot {
  background: #5fb36a;
}

.demo-shell__action {
  padding: 10px 16px;
  border-radius: 8px;
  background: #111;
  color: #fff;
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
}

.demo-shell__action--ghost {
  background: #fff;
  color: #050505;
}

.demo-shell__body {
  flex: 1;
  min-height: 0;
  display: flex;
  overflow: hidden;
}

.demo-shell__panel {
  min-width: 0;
  min-height: 0;
  border-right: 1px solid #ececec;
  transition: width 0.25s ease;
  overflow: hidden;
}

.demo-shell__panel--right {
  border-right: none;
}

.demo-shell__console {
  height: 124px;
  display: flex;
  flex-direction: column;
  background: #050505;
  color: #f1f1f1;
  font-family: var(--murmur-font-type, 'Special Elite', monospace);
}

.demo-shell__console-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.demo-shell__console-body {
  flex: 1;
  overflow: auto;
  padding: 10px 14px 14px;
  font-size: 12px;
  line-height: 1.55;
}

.demo-shell__console-line + .demo-shell__console-line {
  margin-top: 4px;
}

@media (max-width: 1080px) {
  .demo-shell__header {
    height: auto;
    flex-wrap: wrap;
    gap: 12px;
    padding: 14px;
  }

  .demo-shell__header-center {
    position: static;
    left: auto;
    transform: none;
    order: 3;
    width: 100%;
  }

  .demo-shell__body {
    flex-direction: column;
  }

  .demo-shell__panel,
  .demo-shell__panel--right {
    width: 100% !important;
    border-right: none;
    border-bottom: 1px solid #ececec;
  }
}
</style>
