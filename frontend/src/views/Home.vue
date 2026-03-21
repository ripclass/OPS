<template>
  <div class="ops-home">
    <nav class="topbar">
      <div class="brand-lockup">
        <span class="brand-mark">OPS</span>
        <div class="brand-copy">
          <span class="brand-name">Organic Population Simulation</span>
          <span class="brand-tagline">How South Asia actually responds</span>
        </div>
      </div>

      <a href="https://github.com/ripclass/OPS" target="_blank" rel="noreferrer" class="repo-link">
        Source repository
      </a>
    </nav>

    <main class="page-shell">
      <section class="hero-panel">
        <div class="hero-copy">
          <div class="hero-kicker">OPS Simulation Wizard</div>
          <h1>Launch a South Asia population run in five guided steps.</h1>
          <p>
            Define the scenario, choose the population slice, price the run, and launch the existing OPS
            simulation stack without changing the backend workflow underneath it.
          </p>
        </div>

        <div class="hero-aside">
          <div class="hero-card">
            <div class="hero-card-label">Built for</div>
            <div class="hero-card-value">Policy, health, brand, crisis, and disaster response modeling</div>
          </div>
          <img src="../assets/logo/ops_logo_left.jpeg" alt="OPS" class="hero-logo" />
        </div>
      </section>

      <section class="wizard-layout">
        <aside class="wizard-rail">
          <div class="rail-card">
            <div class="rail-heading">Launch Sequence</div>
            <div class="step-list">
              <button
                v-for="step in steps"
                :key="step.id"
                type="button"
                class="step-pill"
                :class="{
                  active: currentStep === step.id,
                  complete: currentStep > step.id || (step.id === 5 && launch.stage === 'done')
                }"
                :disabled="!canJumpToStep(step.id)"
                @click="jumpToStep(step.id)"
              >
                <span class="step-pill-number">{{ String(step.id).padStart(2, '0') }}</span>
                <span class="step-pill-copy">
                  <span class="step-pill-title">{{ step.title }}</span>
                  <span class="step-pill-desc">{{ step.summary }}</span>
                </span>
              </button>
            </div>
          </div>

          <div class="rail-card">
            <div class="rail-heading">Current Run Summary</div>
            <div class="summary-grid">
              <div class="summary-item">
                <span class="summary-label">Use case</span>
                <span class="summary-value">{{ form.useCase }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Country</span>
                <span class="summary-value">{{ form.country }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Segments</span>
                <span class="summary-value">{{ segmentsLabel }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Target agents</span>
                <span class="summary-value">{{ targetAgentsLabel }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Requested outputs</span>
                <span class="summary-value">{{ outputsLabel }}</span>
              </div>
              <div class="summary-item summary-estimate">
                <span class="summary-label">Estimated cost</span>
                <span class="summary-value">{{ estimatedCostLabel }}</span>
              </div>
            </div>
          </div>

          <div class="rail-card">
            <div class="rail-heading">Backend Contract</div>
            <p class="rail-note">
              The wizard keeps the current OPS APIs unchanged. Your selections are embedded into
              <code>simulation_requirement</code> as structured metadata before launch.
            </p>
          </div>
        </aside>

        <section class="wizard-stage">
          <div class="stage-card">
            <header class="stage-header">
              <div>
                <div class="stage-step">Step {{ currentStep }}</div>
                <h2>{{ currentStepMeta.title }}</h2>
              </div>
              <div class="stage-progress">
                <span>{{ currentStepMeta.summary }}</span>
                <div class="stage-progress-bar">
                  <div class="stage-progress-fill" :style="{ width: `${(currentStep / 5) * 100}%` }"></div>
                </div>
              </div>
            </header>

            <div v-if="currentStep === 1" class="stage-body step-body">
              <div class="field-block">
                <label class="field-label" for="scenario-brief">Scenario brief</label>
                <textarea
                  id="scenario-brief"
                  v-model="form.scenario"
                  class="scenario-input"
                  placeholder="Describe the trigger, the audience, and the location. Example: The government announces a 40% rice price increase next month. How do low-income households in Sylhet, Kolkata, and Karachi respond?"
                  rows="8"
                ></textarea>
                <div class="field-hint">
                  This text becomes the primary scenario seed passed into the existing OPS ontology endpoint.
                </div>
              </div>

              <div class="two-column-grid">
                <div class="field-block">
                  <span class="field-label">Use case</span>
                  <div class="chip-grid compact">
                    <button
                      v-for="useCase in USE_CASE_OPTIONS"
                      :key="useCase.value"
                      type="button"
                      class="choice-chip"
                      :class="{ selected: form.useCase === useCase.value }"
                      @click="form.useCase = useCase.value"
                    >
                      <span class="choice-title">{{ useCase.label }}</span>
                      <span class="choice-meta">{{ useCase.description }}</span>
                    </button>
                  </div>
                </div>

                <div class="field-block">
                  <div class="field-label-row">
                    <span class="field-label">Supporting material</span>
                    <span class="field-meta">Optional uploads: PDF, MD, TXT</span>
                  </div>

                  <div
                    class="upload-zone"
                    :class="{ active: isDragOver, populated: files.length > 0 }"
                    @dragover.prevent="handleDragOver"
                    @dragleave.prevent="handleDragLeave"
                    @drop.prevent="handleDrop"
                    @click="triggerFilePicker"
                  >
                    <input
                      ref="fileInput"
                      type="file"
                      multiple
                      accept=".pdf,.md,.txt"
                      class="hidden-input"
                      @change="handleFileSelect"
                    />

                    <div v-if="files.length === 0" class="upload-empty">
                      <div class="upload-title">Drop source files here or click to attach them.</div>
                      <div class="upload-copy">
                        Use documents when you want ontology extraction to pull from supporting evidence as well as the brief.
                      </div>
                    </div>

                    <div v-else class="file-stack">
                      <div v-for="(file, index) in files" :key="`${file.name}-${index}`" class="file-chip">
                        <span class="file-chip-name">{{ file.name }}</span>
                        <button type="button" class="file-chip-remove" @click.stop="removeFile(index)">Remove</button>
                      </div>
                    </div>
                  </div>

                  <div v-if="lostFileWarning" class="field-warning">
                    {{ lostFileWarning }}
                  </div>
                </div>
              </div>
            </div>

            <div v-else-if="currentStep === 2" class="stage-body step-body">
              <div class="field-block">
                <span class="field-label">Country or audience base</span>
                <div class="chip-grid">
                  <button
                    v-for="country in COUNTRY_OPTIONS"
                    :key="country.value"
                    type="button"
                    class="choice-chip"
                    :class="{ selected: form.country === country.value }"
                    @click="form.country = country.value"
                  >
                    <span class="choice-title">{{ country.label }}</span>
                    <span class="choice-meta">{{ country.description }}</span>
                  </button>
                </div>
              </div>

              <div class="field-block">
                <div class="field-label-row">
                  <span class="field-label">Demographic segments</span>
                  <span class="field-meta">Select one or more segments to scope the run</span>
                </div>
                <div class="checkbox-grid">
                  <label v-for="segment in SEGMENT_OPTIONS" :key="segment.value" class="checkbox-card">
                    <input
                      type="checkbox"
                      :value="segment.value"
                      :checked="form.segments.includes(segment.value)"
                      @change="toggleSegment(segment.value)"
                    />
                    <span class="checkbox-content">
                      <span class="choice-title">{{ segment.label }}</span>
                      <span class="choice-meta">{{ segment.description }}</span>
                    </span>
                  </label>
                </div>
              </div>
            </div>

            <div v-else-if="currentStep === 3" class="stage-body step-body">
              <div class="field-block">
                <span class="field-label">Agent scale</span>
                <div class="pricing-grid">
                  <button
                    v-for="option in AGENT_COUNT_OPTIONS"
                    :key="option.value"
                    type="button"
                    class="pricing-card"
                    :class="{ selected: form.agentScale === option.value }"
                    @click="form.agentScale = option.value"
                  >
                    <span class="pricing-size">{{ option.label }}</span>
                    <span class="pricing-blurb">{{ option.description }}</span>
                    <span class="pricing-estimate">{{ option.estimateLabel }}</span>
                  </button>
                </div>
              </div>

              <div v-if="form.agentScale === 'custom'" class="field-block">
                <label class="field-label" for="custom-agent-count">Custom requested agent count</label>
                <input
                  id="custom-agent-count"
                  v-model="form.customAgentCount"
                  type="number"
                  min="1"
                  step="1"
                  class="text-input"
                  placeholder="Enter the target scale for internal scoping"
                />
                <div class="field-hint">Pricing for custom scale is manual. The estimate remains “Contact us”.</div>
              </div>

              <div class="two-column-grid">
                <div class="field-block">
                  <span class="field-label">Requested outputs</span>
                  <div class="checkbox-grid output-grid">
                    <label v-for="output in OUTPUT_OPTIONS" :key="output.value" class="checkbox-card">
                      <input
                        type="checkbox"
                        :value="output.value"
                        :checked="form.outputs.includes(output.value)"
                        @change="toggleOutput(output.value)"
                      />
                      <span class="checkbox-content">
                        <span class="choice-title">{{ output.label }}</span>
                        <span class="choice-meta">{{ output.description }}</span>
                      </span>
                    </label>
                  </div>
                </div>

                <div class="estimate-card">
                  <span class="estimate-kicker">Estimated cost</span>
                  <span class="estimate-price">{{ estimatedCostLabel }}</span>
                  <p class="estimate-copy">
                    Pricing is front-end only in this phase. The wizard still launches the existing OPS stack with
                    the same backend API contract.
                  </p>
                </div>
              </div>
            </div>

            <div v-else-if="currentStep === 4" class="stage-body step-body">
              <div class="review-grid">
                <div class="review-card">
                  <span class="review-label">Scenario brief</span>
                  <p class="review-value review-scenario">{{ form.scenario || 'No scenario entered yet.' }}</p>
                </div>

                <div class="review-card">
                  <span class="review-label">Use case</span>
                  <p class="review-value">{{ form.useCase }}</p>
                </div>

                <div class="review-card">
                  <span class="review-label">Population</span>
                  <p class="review-value">{{ form.country }} / {{ segmentsLabel }}</p>
                </div>

                <div class="review-card">
                  <span class="review-label">Target agents</span>
                  <p class="review-value">{{ targetAgentsLabel }}</p>
                </div>

                <div class="review-card">
                  <span class="review-label">Requested outputs</span>
                  <p class="review-value">{{ outputsLabel }}</p>
                </div>

                <div class="review-card">
                  <span class="review-label">Estimated cost</span>
                  <p class="review-value">{{ estimatedCostLabel }}</p>
                </div>
              </div>

              <div class="review-panel">
                <div class="review-panel-copy">
                  <div class="field-label-row">
                    <span class="field-label">Payment gate</span>
                    <span class="field-meta">Frontend only for this phase</span>
                  </div>

                  <p>
                    The Stripe step is external in this version. Open checkout in a new tab, complete payment there,
                    then confirm in this wizard before OPS launches the existing backend sequence.
                  </p>

                  <div v-if="!checkoutUrl" class="field-warning">
                    Stripe checkout is not configured in this environment. Set
                    <code>VITE_STRIPE_CHECKOUT_URL</code> to enable launch.
                  </div>
                </div>

                <div class="payment-actions">
                  <button
                    type="button"
                    class="primary-button"
                    :disabled="!checkoutUrl"
                    @click="openCheckout"
                  >
                    Pay and open checkout
                  </button>

                  <label class="confirm-row" :class="{ disabled: !payment.checkoutOpened }">
                    <input v-model="payment.confirmed" type="checkbox" :disabled="!payment.checkoutOpened" />
                    <span>I completed checkout and want to continue to launch.</span>
                  </label>

                  <button
                    type="button"
                    class="secondary-button"
                    :disabled="!checkoutUrl || !payment.confirmed || launchBusy"
                    @click="beginLaunch"
                  >
                    Continue to launch
                  </button>
                </div>
              </div>

              <div class="metadata-preview">
                <div class="field-label-row">
                  <span class="field-label">Embedded simulation requirement preview</span>
                  <span class="field-meta">This is what the backend receives</span>
                </div>
                <pre>{{ metadataRequirement }}</pre>
              </div>
            </div>

            <div v-else class="stage-body launch-body">
              <div class="launch-hero">
                <div>
                  <div class="launch-kicker">Launching OPS</div>
                  <h3>{{ launchHeadline }}</h3>
                  <p>{{ launch.message || 'OPS is stepping through the existing backend pipeline now.' }}</p>
                </div>
                <div class="launch-progress-box">
                  <span class="launch-progress-label">Launch progress</span>
                  <span class="launch-progress-value">{{ launch.progress }}%</span>
                </div>
              </div>

              <div class="launch-progress-track">
                <div class="launch-progress-fill" :style="{ width: `${launch.progress}%` }"></div>
              </div>

              <div class="launch-steps">
                <div v-for="phase in launchPhases" :key="phase.key" class="launch-step" :class="launchPhaseClass(phase.key)">
                  <span class="launch-step-index">{{ phase.index }}</span>
                  <div class="launch-step-copy">
                    <span class="launch-step-title">{{ phase.title }}</span>
                    <span class="launch-step-desc">{{ phase.description }}</span>
                  </div>
                  <span class="launch-step-state">{{ launchPhaseLabel(phase.key) }}</span>
                </div>
              </div>

              <div v-if="launch.error" class="launch-error">
                <div class="launch-error-title">Launch paused</div>
                <div class="launch-error-copy">{{ launch.error }}</div>
                <div class="launch-error-actions">
                  <button type="button" class="primary-button" @click="resumeLaunch">Retry launch</button>
                  <button type="button" class="secondary-button" @click="returnToReview">Back to review</button>
                </div>
              </div>

              <div class="launch-grid">
                <div class="launch-log">
                  <div class="launch-log-header">Launch activity</div>
                  <div class="launch-log-list">
                    <div v-for="entry in launch.activity" :key="entry.id" class="launch-log-item">
                      <span class="launch-log-time">{{ entry.time }}</span>
                      <span class="launch-log-text">{{ entry.message }}</span>
                    </div>
                    <div v-if="launch.activity.length === 0" class="launch-log-empty">
                      Activity will appear here as each backend stage completes.
                    </div>
                  </div>
                </div>

                <div class="launch-state-card">
                  <div class="launch-state-row">
                    <span>Project ID</span>
                    <strong>{{ launch.projectId || '-' }}</strong>
                  </div>
                  <div class="launch-state-row">
                    <span>Graph ID</span>
                    <strong>{{ launch.graphId || '-' }}</strong>
                  </div>
                  <div class="launch-state-row">
                    <span>Simulation ID</span>
                    <strong>{{ launch.simulationId || '-' }}</strong>
                  </div>
                  <div class="launch-state-row">
                    <span>Current stage</span>
                    <strong>{{ launch.stage || 'idle' }}</strong>
                  </div>
                  <div class="launch-state-note">
                    This stage is persisted in session storage so a refresh can resume graph build, preparation, or
                    launch. If refresh happens before source uploads finish, attached files must be re-added.
                  </div>
                </div>
              </div>
            </div>

            <footer class="stage-footer">
              <button
                v-if="currentStep > 1 && currentStep < 5"
                type="button"
                class="secondary-button"
                @click="goBack"
              >
                Back
              </button>

              <div class="footer-spacer"></div>

              <button
                v-if="currentStep < 4"
                type="button"
                class="primary-button"
                :disabled="!stepIsValid(currentStep)"
                @click="goNext"
              >
                Continue
              </button>
            </footer>
          </div>
        </section>
      </section>

      <HistoryDatabase />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { buildGraph, generateOntology, getProject, getTaskStatus } from '../api/graph'
import { createSimulation, getPrepareStatus, prepareSimulation, startSimulation } from '../api/simulation'
import HistoryDatabase from '../components/HistoryDatabase.vue'
import {
  AGENT_COUNT_OPTIONS,
  COUNTRY_OPTIONS,
  OUTPUT_OPTIONS,
  SEGMENT_OPTIONS,
  USE_CASE_OPTIONS,
  getAgentEstimateLabel,
  getTargetAgentsLabel,
} from '../constants/opsWizard'

const router = useRouter()

const STORAGE_KEY = 'ops-wizard-state-v1'
const checkoutUrl = (import.meta.env.VITE_STRIPE_CHECKOUT_URL || '').trim()

const steps = [
  { id: 1, title: 'Scenario Brief', summary: 'Define the trigger, uploads, and use case.' },
  { id: 2, title: 'Population Selector', summary: 'Scope geography and demographic segments.' },
  { id: 3, title: 'Configuration', summary: 'Choose scale, outputs, and estimate.' },
  { id: 4, title: 'Review and Launch', summary: 'Confirm the package and trigger checkout.' },
  { id: 5, title: 'Launching', summary: 'Orchestrate the existing OPS backend flow.' },
]

const launchPhases = [
  {
    key: 'ontology',
    index: '01',
    title: 'Scenario intake',
    description: 'Send the brief and optional files into the ontology generator.',
  },
  {
    key: 'graph',
    index: '02',
    title: 'Scenario graph',
    description: 'Build the graph and wait for the project to receive a graph ID.',
  },
  {
    key: 'simulation',
    index: '03',
    title: 'Simulation record',
    description: 'Create the simulation instance tied to the current project.',
  },
  {
    key: 'prepare',
    index: '04',
    title: 'Population preparation',
    description: 'Generate personas and environment state using the existing prepare route.',
  },
  {
    key: 'start',
    index: '05',
    title: 'Run launch',
    description: 'Start the parallel simulation engine and redirect to the live run view.',
  },
]

const fileInput = ref(null)
const currentStep = ref(1)
const isDragOver = ref(false)
const launchBusy = ref(false)
const lostFileWarning = ref('')

const files = ref([])

const form = reactive({
  scenario: '',
  useCase: 'Policy',
  country: 'Bangladesh',
  segments: ['Urban working class'],
  agentScale: '100',
  customAgentCount: '',
  outputs: ['PDF report'],
})

const payment = reactive({
  checkoutOpened: false,
  confirmed: false,
})

const launch = reactive({
  stage: 'idle',
  progress: 0,
  message: '',
  error: '',
  projectId: '',
  graphId: '',
  graphTaskId: '',
  simulationId: '',
  prepareTaskId: '',
  prepareComplete: false,
  started: false,
  fileNames: [],
  activity: [],
})

const currentStepMeta = computed(() => steps.find((step) => step.id === currentStep.value) || steps[0])
const segmentsLabel = computed(() => (form.segments.length ? form.segments.join(', ') : 'No segments selected'))
const outputsLabel = computed(() => (form.outputs.length ? form.outputs.join(', ') : 'Live dashboard only'))
const targetAgentsLabel = computed(() => getTargetAgentsLabel(form.agentScale, form.customAgentCount))
const estimatedCostLabel = computed(() => getAgentEstimateLabel(form.agentScale))

const metadataRequirement = computed(() => {
  return `[OPS Wizard Metadata]
Use case: ${form.useCase}
Country: ${form.country}
Segments: ${form.segments.join(', ') || 'None selected'}
Target agents: ${targetAgentsLabel.value}
Requested outputs: ${form.outputs.join(', ') || 'None selected'}
[/OPS Wizard Metadata]

Scenario:
${form.scenario.trim()}`
})

const launchHeadline = computed(() => {
  if (launch.error) {
    return 'Launch needs attention.'
  }
  if (launch.stage === 'done') {
    return 'Simulation is live. Redirecting now.'
  }
  return 'OPS is orchestrating the existing simulation pipeline.'
})

const stepIsValid = (step) => {
  if (step === 1) {
    return form.scenario.trim().length > 0
  }

  if (step === 2) {
    return Boolean(form.country) && form.segments.length > 0
  }

  if (step === 3) {
    if (form.agentScale !== 'custom') {
      return true
    }
    return Number(form.customAgentCount) > 0
  }

  if (step === 4) {
    return stepIsValid(1) && stepIsValid(2) && stepIsValid(3)
  }

  return true
}

const canJumpToStep = (targetStep) => {
  if (targetStep <= currentStep.value) {
    return true
  }
  for (let step = 1; step < targetStep; step += 1) {
    if (!stepIsValid(step)) {
      return false
    }
  }
  return true
}

const jumpToStep = (targetStep) => {
  if (canJumpToStep(targetStep)) {
    currentStep.value = targetStep
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const goNext = () => {
  if (stepIsValid(currentStep.value) && currentStep.value < 4) {
    currentStep.value += 1
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const goBack = () => {
  if (currentStep.value > 1) {
    currentStep.value -= 1
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const triggerFilePicker = () => {
  fileInput.value?.click()
}

const addFiles = (incomingFiles) => {
  const allowed = incomingFiles.filter((file) => {
    const extension = file.name.split('.').pop()?.toLowerCase()
    return ['pdf', 'md', 'txt'].includes(extension)
  })

  if (allowed.length > 0) {
    files.value = [...files.value, ...allowed]
    lostFileWarning.value = ''
  }
}

const handleFileSelect = (event) => {
  addFiles(Array.from(event.target.files || []))
  event.target.value = ''
}

const handleDragOver = () => {
  isDragOver.value = true
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const handleDrop = (event) => {
  isDragOver.value = false
  addFiles(Array.from(event.dataTransfer?.files || []))
}

const removeFile = (index) => {
  files.value.splice(index, 1)
}

const toggleSegment = (value) => {
  if (form.segments.includes(value)) {
    form.segments = form.segments.filter((item) => item !== value)
    return
  }
  form.segments = [...form.segments, value]
}

const toggleOutput = (value) => {
  if (form.outputs.includes(value)) {
    form.outputs = form.outputs.filter((item) => item !== value)
    return
  }
  form.outputs = [...form.outputs, value]
}

const openCheckout = () => {
  if (!checkoutUrl) {
    return
  }

  payment.checkoutOpened = true
  window.open(checkoutUrl, '_blank', 'noopener,noreferrer')
}

const addLaunchActivity = (message) => {
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  launch.activity = [
    ...launch.activity,
    { id: `${Date.now()}-${launch.activity.length}`, time, message },
  ].slice(-18)
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const updateLaunchProgress = (value) => {
  launch.progress = Math.max(0, Math.min(100, value))
}

const launchPhaseClass = (phaseKey) => {
  const state = launchPhaseLabel(phaseKey).toLowerCase()
  return {
    active: state === 'running',
    done: state === 'done',
    error: state === 'error',
  }
}

const launchPhaseLabel = (phaseKey) => {
  if (launch.error && launch.stage === phaseKey) {
    return 'Error'
  }

  if (phaseKey === 'ontology') {
    if (launch.projectId) return 'Done'
    if (launch.stage === 'ontology') return 'Running'
    return 'Pending'
  }

  if (phaseKey === 'graph') {
    if (launch.graphId) return 'Done'
    if (launch.stage === 'graph') return 'Running'
    return 'Pending'
  }

  if (phaseKey === 'simulation') {
    if (launch.simulationId) return 'Done'
    if (launch.stage === 'simulation') return 'Running'
    return 'Pending'
  }

  if (phaseKey === 'prepare') {
    if (launch.prepareComplete) return 'Done'
    if (launch.stage === 'prepare') return 'Running'
    return 'Pending'
  }

  if (phaseKey === 'start') {
    if (launch.started || launch.stage === 'done') return 'Done'
    if (launch.stage === 'start') return 'Running'
    return 'Pending'
  }

  return 'Pending'
}

const resetLaunchState = () => {
  launch.stage = 'idle'
  launch.progress = 0
  launch.message = ''
  launch.error = ''
  launch.projectId = ''
  launch.graphId = ''
  launch.graphTaskId = ''
  launch.simulationId = ''
  launch.prepareTaskId = ''
  launch.prepareComplete = false
  launch.started = false
  launch.fileNames = []
  launch.activity = []
}

const extractErrorMessage = (error) => {
  if (error?.response?.data?.error) {
    return error.response.data.error
  }
  if (error?.message) {
    return error.message
  }
  return 'Unknown launch error'
}

const beginLaunch = async () => {
  if (!checkoutUrl || !payment.confirmed || launchBusy.value) {
    return
  }

  resetLaunchState()
  currentStep.value = 5
  launch.fileNames = files.value.map((file) => file.name)
  addLaunchActivity('Checkout confirmed. Preparing the OPS launch sequence.')
  await resumeLaunch()
}

const submitOntology = async () => {
  launch.stage = 'ontology'
  launch.error = ''
  launch.message = files.value.length > 0
    ? 'Submitting the scenario brief and attached source material.'
    : 'Submitting the scenario brief to the ontology generator.'
  updateLaunchProgress(10)
  addLaunchActivity(launch.message)

  const formData = new FormData()
  files.value.forEach((file) => formData.append('files', file))
  formData.append('simulation_requirement', metadataRequirement.value)

  const response = await generateOntology(formData)
  launch.projectId = response.data.project_id
  launch.message = `Scenario intake complete for project ${launch.projectId}.`
  updateLaunchProgress(18)
  addLaunchActivity(launch.message)
}

const startGraphBuild = async () => {
  launch.stage = 'graph'
  launch.error = ''
  launch.message = 'Starting the scenario graph build.'
  updateLaunchProgress(22)
  addLaunchActivity(launch.message)

  const response = await buildGraph({ project_id: launch.projectId })
  launch.graphTaskId = response.data.task_id
  addLaunchActivity(`Graph build task started: ${launch.graphTaskId}`)
}

const waitForGraphBuild = async () => {
  launch.stage = 'graph'

  while (true) {
    const response = await getTaskStatus(launch.graphTaskId)
    const task = response.data

    launch.message = task.message || 'Building the scenario graph.'
    updateLaunchProgress(22 + Math.round((task.progress || 0) * 0.28))

    if (task.status === 'completed') {
      const project = await getProject(launch.projectId)
      launch.graphId = project.data.graph_id
      launch.message = 'Scenario graph completed.'
      updateLaunchProgress(50)
      addLaunchActivity(`Scenario graph ready: ${launch.graphId}`)
      return
    }

    if (task.status === 'failed') {
      throw new Error(task.error || 'Graph build failed')
    }

    await sleep(2000)
  }
}

const createSimulationRecord = async () => {
  launch.stage = 'simulation'
  launch.message = 'Creating the simulation record.'
  updateLaunchProgress(58)
  addLaunchActivity(launch.message)

  const response = await createSimulation({
    project_id: launch.projectId,
    graph_id: launch.graphId,
    enable_twitter: true,
    enable_reddit: true,
  })

  launch.simulationId = response.data.simulation_id
  launch.message = `Simulation record created: ${launch.simulationId}`
  updateLaunchProgress(64)
  addLaunchActivity(launch.message)
}

const requestPrepare = async () => {
  launch.stage = 'prepare'
  launch.message = 'Preparing population profiles and environment state.'
  updateLaunchProgress(68)
  addLaunchActivity(launch.message)

  const response = await prepareSimulation({
    simulation_id: launch.simulationId,
    use_llm_for_profiles: true,
    parallel_profile_count: 5,
  })

  if (response.data?.already_prepared) {
    launch.prepareComplete = true
    launch.message = 'Preparation already existed. Reusing the prepared population state.'
    updateLaunchProgress(90)
    addLaunchActivity(launch.message)
    return
  }

  launch.prepareTaskId = response.data.task_id
  addLaunchActivity(`Preparation task started: ${launch.prepareTaskId}`)
}

const waitForPrepare = async () => {
  launch.stage = 'prepare'

  while (true) {
    const response = await getPrepareStatus({
      task_id: launch.prepareTaskId,
      simulation_id: launch.simulationId,
    })
    const data = response.data

    launch.message = data.message || 'Preparing the simulation environment.'
    updateLaunchProgress(68 + Math.round((data.progress || 0) * 0.22))

    if (data.status === 'completed' || data.status === 'ready' || data.already_prepared) {
      launch.prepareComplete = true
      launch.message = 'Population preparation completed.'
      updateLaunchProgress(92)
      addLaunchActivity(launch.message)
      return
    }

    if (data.status === 'failed') {
      throw new Error(data.error || 'Simulation preparation failed')
    }

    await sleep(2000)
  }
}

const launchSimulationRun = async () => {
  launch.stage = 'start'
  launch.message = 'Starting the live simulation run.'
  updateLaunchProgress(96)
  addLaunchActivity(launch.message)

  const response = await startSimulation({
    simulation_id: launch.simulationId,
    platform: 'parallel',
    force: true,
    enable_graph_memory_update: true,
  })

  launch.started = true
  launch.stage = 'done'
  launch.message = 'Simulation engine is live. Redirecting to the run dashboard.'
  updateLaunchProgress(100)
  addLaunchActivity(`Simulation engine started (PID: ${response.data?.process_pid || '-'})`)
  clearStoredState()

  await router.push({
    name: 'SimulationRun',
    params: { simulationId: launch.simulationId },
  })
}

const resumeLaunch = async () => {
  if (launchBusy.value) {
    return
  }

  launchBusy.value = true
  launch.error = ''
  currentStep.value = 5

  try {
    if (!launch.projectId) {
      if (launch.fileNames.length > 0 && files.value.length === 0) {
        lostFileWarning.value = `Attached files were lost after refresh (${launch.fileNames.join(', ')}). Reattach them before retrying the launch.`
        throw new Error('Cannot resume before source uploads finish because the attached files are no longer available in the browser session.')
      }
      await submitOntology()
    }

    if (!launch.graphId) {
      if (!launch.graphTaskId) {
        await startGraphBuild()
      }
      await waitForGraphBuild()
    }

    if (!launch.simulationId) {
      await createSimulationRecord()
    }

    if (!launch.prepareComplete) {
      if (!launch.prepareTaskId) {
        await requestPrepare()
      }
      if (!launch.prepareComplete) {
        await waitForPrepare()
      }
    }

    if (!launch.started) {
      await launchSimulationRun()
    }
  } catch (error) {
    launch.error = extractErrorMessage(error)
    launch.message = 'OPS could not complete the current stage.'
    addLaunchActivity(`Launch error: ${launch.error}`)
  } finally {
    launchBusy.value = false
  }
}

const returnToReview = () => {
  currentStep.value = 4
}

const serializeState = () => {
  return {
    currentStep: currentStep.value,
    form: {
      scenario: form.scenario,
      useCase: form.useCase,
      country: form.country,
      segments: [...form.segments],
      agentScale: form.agentScale,
      customAgentCount: form.customAgentCount,
      outputs: [...form.outputs],
    },
    payment: {
      checkoutOpened: payment.checkoutOpened,
      confirmed: payment.confirmed,
    },
    launch: {
      stage: launch.stage,
      progress: launch.progress,
      message: launch.message,
      error: launch.error,
      projectId: launch.projectId,
      graphId: launch.graphId,
      graphTaskId: launch.graphTaskId,
      simulationId: launch.simulationId,
      prepareTaskId: launch.prepareTaskId,
      prepareComplete: launch.prepareComplete,
      started: launch.started,
      fileNames: [...launch.fileNames],
      activity: [...launch.activity],
    },
  }
}

const restoreState = () => {
  const raw = sessionStorage.getItem(STORAGE_KEY)
  if (!raw) {
    return
  }

  try {
    const saved = JSON.parse(raw)
    currentStep.value = saved.currentStep || 1

    if (saved.form) {
      form.scenario = saved.form.scenario || ''
      form.useCase = saved.form.useCase || 'Policy'
      form.country = saved.form.country || 'Bangladesh'
      form.segments = Array.isArray(saved.form.segments) ? saved.form.segments : ['Urban working class']
      form.agentScale = saved.form.agentScale || '100'
      form.customAgentCount = saved.form.customAgentCount || ''
      form.outputs = Array.isArray(saved.form.outputs) ? saved.form.outputs : ['PDF report']
    }

    if (saved.payment) {
      payment.checkoutOpened = Boolean(saved.payment.checkoutOpened)
      payment.confirmed = Boolean(saved.payment.confirmed)
    }

    if (saved.launch) {
      launch.stage = saved.launch.stage || 'idle'
      launch.progress = saved.launch.progress || 0
      launch.message = saved.launch.message || ''
      launch.error = saved.launch.error || ''
      launch.projectId = saved.launch.projectId || ''
      launch.graphId = saved.launch.graphId || ''
      launch.graphTaskId = saved.launch.graphTaskId || ''
      launch.simulationId = saved.launch.simulationId || ''
      launch.prepareTaskId = saved.launch.prepareTaskId || ''
      launch.prepareComplete = Boolean(saved.launch.prepareComplete)
      launch.started = Boolean(saved.launch.started)
      launch.fileNames = Array.isArray(saved.launch.fileNames) ? saved.launch.fileNames : []
      launch.activity = Array.isArray(saved.launch.activity) ? saved.launch.activity : []
    }

    if (launch.fileNames.length > 0 && files.value.length === 0 && !launch.projectId) {
      lostFileWarning.value = `Attached files were not restored after refresh (${launch.fileNames.join(', ')}). Reattach them before retrying the launch.`
    }
  } catch (error) {
    console.warn('Failed to restore wizard state:', error)
  }
}

const persistState = () => {
  if (launch.stage === 'done' && launch.started) {
    clearStoredState()
    return
  }
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(serializeState()))
}

const clearStoredState = () => {
  sessionStorage.removeItem(STORAGE_KEY)
}

watch(
  () => ({
    currentStep: currentStep.value,
    scenario: form.scenario,
    useCase: form.useCase,
    country: form.country,
    segments: [...form.segments],
    agentScale: form.agentScale,
    customAgentCount: form.customAgentCount,
    outputs: [...form.outputs],
    paymentCheckoutOpened: payment.checkoutOpened,
    paymentConfirmed: payment.confirmed,
    launchStage: launch.stage,
    launchProgress: launch.progress,
    launchMessage: launch.message,
    launchError: launch.error,
    projectId: launch.projectId,
    graphId: launch.graphId,
    graphTaskId: launch.graphTaskId,
    simulationId: launch.simulationId,
    prepareTaskId: launch.prepareTaskId,
    prepareComplete: launch.prepareComplete,
    started: launch.started,
    fileNames: [...launch.fileNames],
    activity: [...launch.activity],
  }),
  () => {
    persistState()
  },
  { deep: true }
)

onMounted(async () => {
  restoreState()

  if (currentStep.value === 5 && launch.stage !== 'idle' && launch.stage !== 'done' && !launch.started) {
    await resumeLaunch()
  }

  if (currentStep.value === 5 && launch.started && launch.simulationId) {
    await router.replace({
      name: 'SimulationRun',
      params: { simulationId: launch.simulationId },
    })
  }
})
</script>

<style scoped>
:root {
  --ops-ink: #0c111d;
  --ops-muted: #6b7280;
  --ops-accent: #c94b22;
  --ops-accent-soft: #f7d9cb;
  --ops-dark: #111827;
  --ops-success: #186b4e;
  --ops-error: #a83232;
  --font-display: 'Space Grotesk', 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

.ops-home {
  min-height: 100vh;
  background:
    radial-gradient(circle at top right, rgba(201, 75, 34, 0.08), transparent 30%),
    linear-gradient(180deg, #f8f5ec 0%, #f0eadf 100%);
  color: var(--ops-ink);
  font-family: var(--font-display);
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 32px;
  border-bottom: 1px solid rgba(12, 17, 29, 0.08);
  background: rgba(255, 253, 248, 0.78);
  backdrop-filter: blur(14px);
  position: sticky;
  top: 0;
  z-index: 20;
}

.brand-lockup {
  display: flex;
  align-items: center;
  gap: 14px;
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
  font-family: var(--font-mono);
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
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.brand-tagline {
  font-size: 0.75rem;
  color: var(--ops-muted);
  text-transform: uppercase;
  letter-spacing: 0.18em;
}

.repo-link {
  color: var(--ops-dark);
  text-decoration: none;
  font-family: var(--font-mono);
  font-size: 0.82rem;
  border-bottom: 1px solid transparent;
}

.repo-link:hover {
  border-color: var(--ops-dark);
}

.page-shell {
  max-width: 1480px;
  margin: 0 auto;
  padding: 40px 32px 72px;
}

.hero-panel {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(320px, 0.85fr);
  gap: 28px;
  align-items: stretch;
}

.hero-copy,
.hero-aside {
  background: rgba(255, 253, 248, 0.85);
  border: 1px solid rgba(17, 24, 39, 0.08);
  border-radius: 28px;
  padding: 32px;
  box-shadow: 0 25px 60px rgba(17, 24, 39, 0.06);
}

.hero-kicker {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  background: var(--ops-accent-soft);
  color: var(--ops-accent);
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.16em;
}

.hero-copy h1 {
  margin: 18px 0 12px;
  font-size: clamp(2.6rem, 5vw, 4.2rem);
  line-height: 1.02;
  letter-spacing: -0.05em;
}

.hero-copy p {
  max-width: 62ch;
  font-size: 1.02rem;
  line-height: 1.7;
  color: #3f4959;
}

.hero-aside {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 24px;
  background:
    linear-gradient(145deg, rgba(17, 24, 39, 0.95) 0%, rgba(38, 51, 75, 0.96) 100%);
  color: #fff;
  overflow: hidden;
}

.hero-card {
  max-width: 28ch;
}

.hero-card-label {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.62);
}

.hero-card-value {
  margin-top: 10px;
  font-size: 1.1rem;
  line-height: 1.5;
}

.hero-logo {
  width: min(100%, 420px);
  align-self: flex-end;
}

.wizard-layout {
  display: grid;
  grid-template-columns: minmax(320px, 360px) minmax(0, 1fr);
  gap: 28px;
  margin-top: 28px;
  align-items: start;
}

.wizard-rail {
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: sticky;
  top: 96px;
}

.rail-card,
.stage-card {
  background: rgba(255, 253, 248, 0.92);
  border: 1px solid rgba(17, 24, 39, 0.08);
  border-radius: 28px;
  box-shadow: 0 25px 60px rgba(17, 24, 39, 0.06);
}

.rail-card {
  padding: 22px;
}

.rail-heading {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: var(--ops-muted);
  margin-bottom: 16px;
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step-pill {
  width: 100%;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px;
  border: 1px solid rgba(17, 24, 39, 0.08);
  background: #fff;
  border-radius: 18px;
  cursor: pointer;
  text-align: left;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.step-pill:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.step-pill:not(:disabled):hover {
  transform: translateY(-1px);
  border-color: rgba(201, 75, 34, 0.4);
}

.step-pill.active {
  border-color: var(--ops-accent);
  box-shadow: 0 12px 28px rgba(201, 75, 34, 0.12);
}

.step-pill.complete {
  border-color: rgba(24, 107, 78, 0.4);
}

.step-pill-number {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: #f3efe5;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  font-weight: 700;
}

.step-pill.active .step-pill-number {
  background: var(--ops-accent);
  color: #fff;
}

.step-pill.complete .step-pill-number {
  background: var(--ops-success);
  color: #fff;
}

.step-pill-copy {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.step-pill-title {
  font-size: 0.96rem;
  font-weight: 700;
}

.step-pill-desc,
.rail-note,
.choice-meta,
.field-hint,
.upload-copy,
.estimate-copy,
.launch-state-note,
.launch-step-desc,
.launch-log-empty {
  color: var(--ops-muted);
  line-height: 1.55;
}

.summary-grid {
  display: grid;
  gap: 14px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(17, 24, 39, 0.08);
}

.summary-item:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.summary-label {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--ops-muted);
  text-transform: uppercase;
  letter-spacing: 0.14em;
}

.summary-value {
  font-size: 0.95rem;
  font-weight: 600;
  line-height: 1.5;
}

.summary-estimate .summary-value {
  color: var(--ops-accent);
}

.stage-card {
  padding: 28px;
}

.stage-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(17, 24, 39, 0.08);
}

.stage-step {
  font-family: var(--font-mono);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--ops-accent);
}

.stage-header h2 {
  margin: 8px 0 0;
  font-size: clamp(1.9rem, 3vw, 2.6rem);
  line-height: 1.05;
  letter-spacing: -0.04em;
}

.stage-progress {
  min-width: 280px;
  max-width: 320px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  color: var(--ops-muted);
  font-size: 0.9rem;
}

.stage-progress-bar,
.launch-progress-track {
  width: 100%;
  height: 10px;
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.08);
  overflow: hidden;
}

.stage-progress-fill,
.launch-progress-fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #c94b22 0%, #f0833a 100%);
  transition: width 0.25s ease;
}

.stage-body {
  padding: 28px 0;
}

.step-body {
  display: flex;
  flex-direction: column;
  gap: 26px;
}

.field-block {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-label-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: baseline;
}

.field-label {
  font-size: 0.92rem;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.field-meta {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--ops-muted);
}

.scenario-input,
.text-input,
.metadata-preview pre {
  width: 100%;
  border: 1px solid rgba(17, 24, 39, 0.12);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.9);
  color: var(--ops-dark);
}

.scenario-input,
.text-input {
  padding: 18px 20px;
  font-family: var(--font-display);
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical;
}

.scenario-input:focus,
.text-input:focus {
  outline: none;
  border-color: rgba(201, 75, 34, 0.5);
  box-shadow: 0 0 0 4px rgba(201, 75, 34, 0.12);
}

.two-column-grid,
.review-grid,
.launch-grid {
  display: grid;
  gap: 20px;
}

.two-column-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.chip-grid,
.pricing-grid,
.checkbox-grid {
  display: grid;
  gap: 14px;
}

.chip-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.chip-grid.compact {
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
}

.choice-chip,
.pricing-card,
.checkbox-card,
.estimate-card,
.review-card,
.launch-state-card,
.launch-log {
  border: 1px solid rgba(17, 24, 39, 0.08);
  background: rgba(255, 255, 255, 0.88);
  border-radius: 20px;
}

.choice-chip,
.pricing-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px;
  text-align: left;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.choice-chip:hover,
.pricing-card:hover {
  transform: translateY(-1px);
  border-color: rgba(201, 75, 34, 0.38);
  box-shadow: 0 16px 32px rgba(17, 24, 39, 0.06);
}

.choice-chip.selected,
.pricing-card.selected {
  border-color: var(--ops-accent);
  box-shadow: 0 18px 36px rgba(201, 75, 34, 0.12);
}

.choice-title {
  font-size: 1rem;
  font-weight: 700;
}

.upload-zone {
  min-height: 212px;
  padding: 22px;
  border: 1px dashed rgba(17, 24, 39, 0.18);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.75);
  transition: border-color 0.2s ease, background 0.2s ease, transform 0.2s ease;
  cursor: pointer;
}

.upload-zone.active {
  border-color: var(--ops-accent);
  background: rgba(247, 217, 203, 0.45);
  transform: translateY(-1px);
}

.upload-zone.populated {
  border-style: solid;
}

.hidden-input {
  display: none;
}

.upload-empty {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-start;
  justify-content: center;
  min-height: 160px;
}

.upload-title {
  font-size: 1.05rem;
  font-weight: 700;
}

.file-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-chip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 16px;
  background: #fff;
  border: 1px solid rgba(17, 24, 39, 0.08);
}

.file-chip-name {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  word-break: break-word;
}

.file-chip-remove {
  border: 0;
  background: transparent;
  color: var(--ops-accent);
  font-family: var(--font-mono);
  font-size: 0.8rem;
  cursor: pointer;
}

.field-warning,
.launch-error {
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(168, 50, 50, 0.08);
  border: 1px solid rgba(168, 50, 50, 0.2);
  color: var(--ops-error);
}

.checkbox-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.output-grid {
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.checkbox-card {
  display: flex;
  gap: 14px;
  padding: 18px;
  align-items: flex-start;
}

.checkbox-card input {
  margin-top: 4px;
  width: 18px;
  height: 18px;
  accent-color: var(--ops-accent);
}

.checkbox-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pricing-grid {
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.pricing-size {
  font-size: 1.24rem;
  font-weight: 700;
}

.pricing-estimate,
.estimate-price {
  font-family: var(--font-mono);
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--ops-accent);
}

.estimate-card {
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  justify-content: center;
}

.estimate-kicker,
.review-label,
.launch-progress-label,
.launch-kicker,
.launch-log-header {
  font-family: var(--font-mono);
  font-size: 0.74rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: var(--ops-muted);
}

.review-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.review-card,
.launch-state-card {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.review-scenario {
  white-space: pre-wrap;
}

.review-value {
  margin: 0;
  font-size: 1rem;
  line-height: 1.6;
  color: var(--ops-dark);
}

.review-panel {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(260px, 0.8fr);
  gap: 20px;
  padding: 22px;
  border-radius: 24px;
  background: rgba(17, 24, 39, 0.04);
}

.payment-actions {
  display: flex;
  flex-direction: column;
  gap: 14px;
  justify-content: center;
}

.confirm-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  font-size: 0.92rem;
}

.confirm-row input {
  margin-top: 3px;
  accent-color: var(--ops-accent);
}

.confirm-row.disabled {
  opacity: 0.58;
}

.metadata-preview pre {
  margin: 0;
  padding: 20px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  line-height: 1.7;
  overflow-x: auto;
}

.launch-body {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.launch-hero {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
}

.launch-hero h3 {
  margin: 8px 0 10px;
  font-size: clamp(1.6rem, 3vw, 2.2rem);
  line-height: 1.1;
}

.launch-hero p {
  margin: 0;
  color: #475467;
  line-height: 1.6;
}

.launch-progress-box {
  min-width: 150px;
  padding: 18px;
  border-radius: 18px;
  background: rgba(17, 24, 39, 0.04);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.launch-progress-value {
  font-family: var(--font-mono);
  font-size: 1.7rem;
  font-weight: 700;
}

.launch-steps {
  display: grid;
  gap: 12px;
}

.launch-step {
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr) auto;
  gap: 14px;
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid rgba(17, 24, 39, 0.08);
  background: rgba(255, 255, 255, 0.86);
}

.launch-step.active {
  border-color: rgba(201, 75, 34, 0.48);
  box-shadow: 0 16px 34px rgba(201, 75, 34, 0.08);
}

.launch-step.done {
  border-color: rgba(24, 107, 78, 0.38);
}

.launch-step.error {
  border-color: rgba(168, 50, 50, 0.32);
}

.launch-step-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: #f3efe5;
  font-family: var(--font-mono);
  font-weight: 700;
}

.launch-step.active .launch-step-index {
  background: var(--ops-accent);
  color: #fff;
}

.launch-step.done .launch-step-index {
  background: var(--ops-success);
  color: #fff;
}

.launch-step.error .launch-step-index {
  background: var(--ops-error);
  color: #fff;
}

.launch-step-copy {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.launch-step-title {
  font-size: 0.97rem;
  font-weight: 700;
}

.launch-step-state {
  align-self: center;
  font-family: var(--font-mono);
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--ops-muted);
}

.launch-error-title {
  font-weight: 700;
  margin-bottom: 6px;
}

.launch-error-copy {
  line-height: 1.6;
}

.launch-error-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.launch-grid {
  grid-template-columns: minmax(0, 1.25fr) minmax(260px, 0.75fr);
}

.launch-log {
  padding: 20px;
}

.launch-log-list {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.launch-log-item {
  display: grid;
  grid-template-columns: 64px minmax(0, 1fr);
  gap: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(17, 24, 39, 0.08);
}

.launch-log-item:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.launch-log-time {
  font-family: var(--font-mono);
  font-size: 0.74rem;
  color: var(--ops-muted);
}

.launch-log-text {
  line-height: 1.55;
  color: var(--ops-dark);
}

.launch-state-row {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(17, 24, 39, 0.08);
}

.launch-state-row:last-of-type {
  margin-bottom: 6px;
}

.primary-button,
.secondary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 52px;
  padding: 0 22px;
  border-radius: 999px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.primary-button {
  border: 1px solid var(--ops-accent);
  background: var(--ops-accent);
  color: #fff;
}

.primary-button:hover:not(:disabled),
.secondary-button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.primary-button:disabled,
.secondary-button:disabled {
  cursor: not-allowed;
  opacity: 0.52;
  transform: none;
}

.secondary-button {
  border: 1px solid rgba(17, 24, 39, 0.14);
  background: #fff;
  color: var(--ops-dark);
}

.stage-footer {
  display: flex;
  align-items: center;
  gap: 14px;
  padding-top: 18px;
  border-top: 1px solid rgba(17, 24, 39, 0.08);
}

.footer-spacer {
  flex: 1;
}

code {
  font-family: var(--font-mono);
  background: rgba(17, 24, 39, 0.05);
  padding: 2px 6px;
  border-radius: 8px;
}

@media (max-width: 1180px) {
  .hero-panel,
  .wizard-layout,
  .two-column-grid,
  .review-panel,
  .launch-grid {
    grid-template-columns: 1fr;
  }

  .wizard-rail {
    position: static;
  }

  .stage-header,
  .launch-hero {
    flex-direction: column;
  }

  .stage-progress,
  .launch-progress-box {
    min-width: 0;
    max-width: none;
    width: 100%;
  }
}

@media (max-width: 760px) {
  .topbar,
  .page-shell,
  .stage-card,
  .rail-card,
  .hero-copy,
  .hero-aside {
    padding-left: 18px;
    padding-right: 18px;
  }

  .topbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .review-grid,
  .pricing-grid,
  .chip-grid,
  .checkbox-grid,
  .launch-steps {
    grid-template-columns: 1fr;
  }

  .launch-step {
    grid-template-columns: 1fr;
  }

  .launch-step-state {
    justify-self: start;
  }

  .launch-log-item,
  .launch-state-row {
    grid-template-columns: 1fr;
  }
}
</style>
