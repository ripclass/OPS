<template>
  <header class="ops-product-header">
    <div class="ops-product-top">
      <div class="ops-product-brand">
        <RouterLink to="/" class="brand-home-link" aria-label="Go to OPS wizard">
          <span class="brand-mark">OPS</span>
        </RouterLink>
        <div class="brand-copy">
          <span class="brand-name">Organic Population Simulation</span>
          <span class="brand-tagline">How South Asia actually responds</span>
        </div>
      </div>

      <div class="ops-product-rail">
        <span v-if="sectionLabel" class="section-label">{{ sectionLabel }}</span>
        <div class="ops-product-actions">
          <slot name="actions" />
        </div>
      </div>
    </div>

    <nav class="flow-nav" aria-label="OPS flow">
      <RouterLink to="/" class="flow-pill" :class="{ active: activeView === 'wizard' }">
        <span class="flow-pill-index">01</span>
        <span class="flow-pill-copy">
          <span class="flow-pill-title">Wizard</span>
          <span class="flow-pill-desc">Scenario, population, and launch setup</span>
        </span>
      </RouterLink>

      <RouterLink
        v-if="simulationId"
        :to="{ name: 'SimulationRun', params: { simulationId } }"
        class="flow-pill"
        :class="{ active: activeView === 'run' }"
      >
        <span class="flow-pill-index">02</span>
        <span class="flow-pill-copy">
          <span class="flow-pill-title">Live Run</span>
          <span class="flow-pill-desc">Monitor the simulation as responses emerge</span>
        </span>
      </RouterLink>
      <span v-else class="flow-pill disabled">
        <span class="flow-pill-index">02</span>
        <span class="flow-pill-copy">
          <span class="flow-pill-title">Live Run</span>
          <span class="flow-pill-desc">Available after the wizard launches a run</span>
        </span>
      </span>

      <RouterLink
        v-if="reportId"
        :to="{ name: 'Report', params: { reportId } }"
        class="flow-pill"
        :class="{ active: activeView === 'results' }"
      >
        <span class="flow-pill-index">03</span>
        <span class="flow-pill-copy">
          <span class="flow-pill-title">Results</span>
          <span class="flow-pill-desc">Review report outputs and cascade insights</span>
        </span>
      </RouterLink>
      <span v-else class="flow-pill disabled">
        <span class="flow-pill-index">03</span>
        <span class="flow-pill-copy">
          <span class="flow-pill-title">Results</span>
          <span class="flow-pill-desc">Available after the run generates a report</span>
        </span>
      </span>
    </nav>
  </header>
</template>

<script setup>
import { RouterLink } from 'vue-router'

defineProps({
  activeView: {
    type: String,
    required: true,
  },
  simulationId: {
    type: [String, Number],
    default: '',
  },
  reportId: {
    type: [String, Number],
    default: '',
  },
  sectionLabel: {
    type: String,
    default: '',
  },
})
</script>

<style scoped>
.ops-product-header {
  position: sticky;
  top: 0;
  z-index: 30;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px 32px 18px;
  background: rgba(255, 253, 248, 0.82);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--ops-border);
}

.ops-product-top,
.ops-product-brand,
.ops-product-rail,
.ops-product-actions,
.flow-nav {
  display: flex;
}

.ops-product-top {
  justify-content: space-between;
  align-items: center;
  gap: 24px;
}

.ops-product-brand {
  align-items: center;
  gap: 14px;
}

.brand-home-link {
  text-decoration: none;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 54px;
  height: 54px;
  border-radius: 14px;
  background: linear-gradient(135deg, #111827 0%, #26334b 100%);
  color: #fff;
  font-family: var(--ops-font-mono);
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.18em;
}

.brand-copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.brand-name {
  font-size: 0.96rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.brand-tagline,
.section-label,
.flow-pill-index,
.flow-pill-desc {
  font-family: var(--ops-font-mono);
}

.brand-tagline {
  font-size: 0.75rem;
  color: var(--ops-muted);
  text-transform: uppercase;
  letter-spacing: 0.18em;
}

.ops-product-rail {
  align-items: center;
  justify-content: flex-end;
  gap: 18px;
  flex-wrap: wrap;
}

.section-label {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  padding: 0 12px;
  border-radius: 999px;
  background: var(--ops-accent-soft);
  color: var(--ops-accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.ops-product-actions {
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.flow-nav {
  gap: 12px;
  flex-wrap: wrap;
}

.flow-pill {
  flex: 1 1 220px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid var(--ops-border);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.84);
  color: var(--ops-ink);
  text-decoration: none;
  box-shadow: var(--ops-shadow-tight);
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.flow-pill:not(.disabled):hover {
  transform: translateY(-1px);
  border-color: rgba(201, 75, 34, 0.4);
}

.flow-pill.active {
  border-color: var(--ops-accent);
  box-shadow: 0 18px 36px rgba(201, 75, 34, 0.14);
}

.flow-pill.disabled {
  opacity: 0.62;
  cursor: default;
  box-shadow: none;
}

.flow-pill-index {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: #f3efe5;
  font-size: 0.78rem;
  font-weight: 700;
}

.flow-pill.active .flow-pill-index {
  background: var(--ops-accent);
  color: #fff;
}

.flow-pill-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.flow-pill-title {
  font-size: 0.95rem;
  font-weight: 700;
}

.flow-pill-desc {
  font-size: 0.72rem;
  line-height: 1.5;
  letter-spacing: 0.02em;
  color: var(--ops-muted);
}

@media (max-width: 900px) {
  .ops-product-header {
    padding-left: 18px;
    padding-right: 18px;
  }

  .ops-product-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .ops-product-rail {
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 620px) {
  .ops-product-rail,
  .ops-product-actions,
  .flow-nav {
    width: 100%;
  }

  .ops-product-actions {
    justify-content: flex-start;
  }

  .flow-pill {
    flex-basis: 100%;
  }
}
</style>
