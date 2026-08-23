<template>
  <div class="console-start-container">
    <nav class="navbar">
      <div class="nav-brand" @click="router.push('/')">{{ brandLabel }}</div>
      <div class="nav-links">
        <span class="session-email" v-if="authState.user?.email">{{ authState.user.email }}</span>
        <button v-if="authState.user" class="nav-action" type="button" @click="handleSignOut">Sign out</button>
        <button v-else class="nav-action" type="button" @click="router.push({ path: '/', query: { auth: 'signin', redirect: route.fullPath } })">Sign in</button>
        <a href="https://github.com/ripclass/OPS" target="_blank" rel="noreferrer" class="github-link">
          GitHub <span class="arrow">&gt;</span>
        </a>
      </div>
    </nav>

    <div class="main-content">
      <section class="hero-section" :style="heroSectionStyle">
        <div class="hero-left hero-copy-card">
          <div class="tag-row">
            <span class="orange-tag">{{ brandLabel }} Console</span>
            <span class="version-text">/ Scenario Intake</span>
          </div>

          <h1 class="main-title">
            System Ready
          </h1>

          <div class="hero-desc">
            <p>
              Start from a scenario brief, a policy note, a report, or public URLs.
            </p>
          </div>

          <div class="steps-container">
            <div class="steps-header">
              <span class="diamond-icon">◇</span> Workflow Steps
            </div>
            <div class="workflow-list">
              <div class="workflow-item" v-for="step in steps" :key="step.number">
                <span class="step-num">{{ step.number }}</span>
                <div class="step-info">
                  <div class="step-title">{{ step.title }}</div>
                  <div class="step-desc">{{ step.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="dashboard-section">
        <div class="right-panel full-width">
          <div class="console-box">
            <div v-if="isDemoRoute" class="console-section pack-section">
              <div class="console-header">
                <span class="console-label">00 / Scenario Pack</span>
                <span class="console-meta">Seven prepared Bangladesh scenarios</span>
              </div>
              <div class="pack-grid">
                <button
                  v-for="pick in DEMO_SCENARIO_PICKS"
                  :key="pick.countryCode"
                  class="pack-card"
                  :class="{ active: pick.countryCode === activePackCode }"
                  type="button"
                  @click="selectScenarioPack(pick.countryCode)"
                >
                  <span class="pack-card-label">{{ pick.label }}</span>
                  <span class="pack-card-detail">{{ pick.detail }}</span>
                </button>
              </div>
            </div>

            <div class="console-section">
              <div class="console-header">
                <span class="console-label">{{ isDemoRoute ? '01 / Reality Seeds' : '01 / Source Material' }}</span>
                <span class="console-meta">
                  {{ isDemoRoute ? 'Pre-attached for this scenario' : 'Optional Uploads: PDF, MD, MARKDOWN, TXT' }}
                </span>
              </div>

              <div
                class="upload-zone"
                :class="{ 'drag-over': isDragOver, 'has-files': files.length > 0 || isDemoRoute }"
                @dragover.prevent="handleDragOver"
                @dragleave.prevent="handleDragLeave"
                @drop.prevent="handleDrop"
                @click="triggerFileInput"
              >
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept=".pdf,.md,.markdown,.txt"
                  style="display: none"
                  :disabled="loading"
                  @change="handleFileSelect"
                />

                <div v-if="isDemoRoute" class="file-list">
                  <div
                    v-for="doc in visibleSeedDocs"
                    :key="doc.name"
                    class="file-item file-item--seed"
                  >
                    <span class="file-icon file-kind">{{ doc.kind }}</span>
                    <span class="file-name">
                      {{ doc.name }}
                      <span class="file-note">{{ doc.note }}</span>
                    </span>
                    <span class="file-attached">attached</span>
                  </div>

                  <div v-for="(file, index) in files" :key="`${file.name}-${index}`" class="file-item">
                    <span class="file-icon">DOC</span>
                    <span class="file-name">{{ file.name }}</span>
                    <button class="remove-btn" @click.stop="removeFile(index)">x</button>
                  </div>

                  <div class="seed-add-hint">Click to add your own files: PDF, MD, MARKDOWN, TXT.</div>
                </div>

                <template v-else>
                  <div v-if="files.length === 0" class="upload-placeholder">
                    <div class="upload-icon">^</div>
                    <div class="upload-title">Drag Files to Upload (Optional)</div>
                    <div class="upload-hint">
                      Or click to browse. You can continue with only the scenario prompt below.
                    </div>
                  </div>

                  <div v-else class="file-list">
                    <div v-for="(file, index) in files" :key="`${file.name}-${index}`" class="file-item">
                      <span class="file-icon">DOC</span>
                      <span class="file-name">{{ file.name }}</span>
                      <button class="remove-btn" @click.stop="removeFile(index)">x</button>
                    </div>
                  </div>
                </template>
              </div>
            </div>

            <div class="console-section url-section">
              <div class="console-header">
                <span class="console-label">&gt;_ 01B / Source URLs</span>
                <span class="console-meta">One public URL per line</span>
              </div>
              <div class="input-wrapper url-input-wrapper">
                <textarea
                  v-model="formData.sourceUrls"
                  class="code-input url-input"
                  rows="4"
                  :disabled="loading"
                  placeholder="https://example.com/news-article&#10;https://example.com/blog-post"
                ></textarea>
              </div>
            </div>

            <div class="console-divider">
              <span>Scenario Inputs</span>
            </div>

            <div class="console-section">
              <div class="console-header">
                <span class="console-label">&gt;_ 02 / Scenario Brief</span>
                <button
                  v-if="isDemoRoute"
                  class="draft-brief-btn"
                  type="button"
                  :disabled="typingBrief || loading"
                  @click="draftBriefForMe"
                >
                  {{ typingBrief ? 'Drafting...' : 'Draft the brief for me' }}
                </button>
              </div>
              <p v-if="isDemoRoute" class="draft-brief-hint">
                Fills a scripted example brief for the selected scenario. Edit it before you run.
              </p>
              <div class="input-wrapper">
                <textarea
                  v-model="formData.simulationRequirement"
                  class="code-input"
                  rows="6"
                  :disabled="loading"
                  :readonly="typingBrief"
                  placeholder="Describe the trigger you want to test. Example: The government announces a 40% rice price increase before Eid. How do low-income households in Dhaka respond?"
                ></textarea>
                <div class="model-badge">{{ engineLabel }}</div>
              </div>
            </div>

            <div class="console-section btn-section">
              <button
                class="start-engine-btn"
                :disabled="!canSubmit || loading || typingBrief"
                @click="startSimulation"
              >
                <span v-if="!loading">Continue to Population Setup</span>
                <span v-else>Initializing...</span>
                <span class="btn-arrow">-&gt;</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <HistoryDatabase v-if="!isDemoRoute" />
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import HistoryDatabase from '../components/HistoryDatabase.vue'
import { authState, signOut } from '../store/auth'
import { buildDemoQuery, initializeDemoFlow, setDemoScenario } from '../store/demoFlow'
import { DEMO_SCENARIO_PICKS, getDemoPackByCountryCode, resolveDemoPackKey } from '../content/demoFlowPacks'
import { getDraftedBrief, getSeedDocsForPack } from '../content/demoSeedDocs'
import { useDemoBrand } from '../composables/useDemoBrand'

const router = useRouter()
const route = useRoute()
const heroImageUrl = new URL('../assets/logo/ops_logo_left.png', import.meta.url).href
const { brandLabel, engineLabel } = useDemoBrand()

const steps = [
  {
    number: '01',
    title: 'Graph Build',
    description: 'Reality seed extraction, relationship mapping, and memory graph construction.',
  },
  {
    number: '02',
    title: 'Env Setup',
    description: 'Population generation, persona assignment, and world configuration.',
  },
  {
    number: '03',
    title: 'Start Simulation',
    description: 'Multi-agent rounds, memory updates, and cascade progression.',
  },
  {
    number: '04',
    title: 'Report Generation',
    description: 'Structured reporting grounded in the post-simulation environment.',
  },
  {
    number: '05',
    title: 'Deep Interaction',
    description: 'Question the report agent or interview simulated people.',
  },
]

const formData = ref({
  simulationRequirement: '',
  sourceUrls: '',
})

const files = ref([])
const loading = ref(false)
const isDragOver = ref(false)
const fileInput = ref(null)
const isDemoRoute = computed(() => route.path.startsWith('/demo'))

const canSubmit = computed(() => formData.value.simulationRequirement.trim() !== '')
const activePackCode = computed(() => {
  const raw = typeof route.query.country === 'string' ? route.query.country.trim().toUpperCase() : ''
  return raw || 'BD'
})

// Demo-only intake theater. The run has to be seen receiving its inputs, so the
// brief types itself in and the pack's reality seeds re-attach one at a time.
// Everything below is gated on isDemoRoute; /console keeps its plain behaviour.
const SEED_STAGGER_MS = 140
const TYPE_TICK_MS = 26
const PACK_TYPE_MS = 1000
const DRAFT_TYPE_MS = 1300

const typingBrief = ref(false)
const seedRevealCount = ref(Number.MAX_SAFE_INTEGER)

const activePackKey = computed(() => resolveDemoPackKey(activePackCode.value))
const packSeedDocs = computed(() => (isDemoRoute.value ? getSeedDocsForPack(activePackKey.value) : []))
const visibleSeedDocs = computed(() => packSeedDocs.value.slice(0, seedRevealCount.value))

const seedTimers = []
let briefTypeTimer = null

const scheduleSeed = (fn, delay) => {
  seedTimers.push(window.setTimeout(fn, delay))
}

const clearIntakeTimers = () => {
  seedTimers.splice(0).forEach((id) => window.clearTimeout(id))
  if (briefTypeTimer !== null) {
    window.clearInterval(briefTypeTimer)
    briefTypeTimer = null
  }
}

onBeforeUnmount(clearIntakeTimers)

const prefersReducedMotion = () => (
  typeof window !== 'undefined'
  && typeof window.matchMedia === 'function'
  && window.matchMedia('(prefers-reduced-motion: reduce)').matches
)

// Characters are batched per tick so a long brief lands in about the same time
// a short one does, instead of crawling.
const typeIntoBrief = (text, durationMs) => {
  if (briefTypeTimer !== null) {
    window.clearInterval(briefTypeTimer)
    briefTypeTimer = null
  }

  const total = text.length
  if (!total) {
    formData.value.simulationRequirement = ''
    return
  }

  if (prefersReducedMotion()) {
    formData.value.simulationRequirement = text
    return
  }

  const ticks = Math.max(1, Math.round(durationMs / TYPE_TICK_MS))
  const perTick = Math.max(1, Math.ceil(total / ticks))
  let index = 0

  typingBrief.value = true
  formData.value.simulationRequirement = ''
  briefTypeTimer = window.setInterval(() => {
    index = Math.min(total, index + perTick)
    formData.value.simulationRequirement = text.slice(0, index)
    if (index >= total) {
      window.clearInterval(briefTypeTimer)
      briefTypeTimer = null
      typingBrief.value = false
    }
  }, TYPE_TICK_MS)
}

// The count is passed in rather than read off the computed, because router
// .replace has not landed yet when the picker calls this and the computed would
// still describe the pack we are leaving.
const restageSeedDocs = (count) => {
  seedTimers.splice(0).forEach((id) => window.clearTimeout(id))

  if (!count || prefersReducedMotion()) {
    seedRevealCount.value = Number.MAX_SAFE_INTEGER
    return
  }

  seedRevealCount.value = 0
  for (let index = 0; index < count; index += 1) {
    scheduleSeed(() => {
      seedRevealCount.value = index + 1
    }, SEED_STAGGER_MS * (index + 1))
  }
}

const draftBriefForMe = () => {
  if (typingBrief.value || loading.value) {
    return
  }
  typeIntoBrief(getDraftedBrief(activePackKey.value), DRAFT_TYPE_MS)
}

// The picker only ever rewrites this page's own query and its own textarea. The
// landing CTA never lands here, it seeds the store and jumps straight to
// DemoGraph, so nothing below can reach that path.
const selectScenarioPack = (countryCode) => {
  const pack = getDemoPackByCountryCode(countryCode)

  router.replace({
    path: route.path,
    query: {
      ...route.query,
      country: countryCode,
      scenario: undefined,
    },
  })

  if (!isDemoRoute.value) {
    formData.value.simulationRequirement = pack.intake.defaultScenario
    return
  }

  restageSeedDocs(getSeedDocsForPack(resolveDemoPackKey(countryCode)).length)
  typeIntoBrief(pack.intake.defaultScenario, PACK_TYPE_MS)
}
const heroSectionStyle = computed(() => ({
  '--hero-image': `url("${heroImageUrl}")`,
}))

watch(
  () => route.query.scenario,
  value => {
    if (typeof value === 'string' && value.trim()) {
      formData.value.simulationRequirement = value.trim()
    }
  },
  { immediate: true }
)

// Arriving at /demo with nothing in the box left the primary button disabled
// and the visitor guessing. The demo has a brief for whichever pack is
// selected, so type it in and let them change it or run it. /console keeps its
// empty box, because there the brief is the whole point of the page.
onMounted(() => {
  if (!isDemoRoute.value || formData.value.simulationRequirement.trim()) {
    return
  }
  typeIntoBrief(getDemoPackByCountryCode(activePackCode.value).intake.defaultScenario, PACK_TYPE_MS)
})

const triggerFileInput = () => {
  if (!loading.value) {
    fileInput.value?.click()
  }
}

const normalizeSourceUrls = (rawValue) => {
  return String(rawValue || '')
    .split(/\r?\n/)
    .map((value) => value.trim())
    .filter(Boolean)
}

const addFiles = (newFiles) => {
  const validFiles = newFiles.filter((file) => {
    const ext = file.name.split('.').pop()?.toLowerCase()
    return ['pdf', 'md', 'markdown', 'txt'].includes(ext)
  })
  files.value.push(...validFiles)
}

const handleFileSelect = (event) => {
  addFiles(Array.from(event.target.files || []))
}

const handleDragOver = () => {
  if (!loading.value) {
    isDragOver.value = true
  }
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const handleDrop = (event) => {
  isDragOver.value = false
  if (loading.value) {
    return
  }
  addFiles(Array.from(event.dataTransfer.files || []))
}

const removeFile = (index) => {
  files.value.splice(index, 1)
}

const startSimulation = () => {
  if (!canSubmit.value || loading.value) {
    return
  }

  if (isDemoRoute.value) {
    initializeDemoFlow({
      scenario: formData.value.simulationRequirement,
      country: typeof route.query.country === 'string' ? route.query.country : '',
    }).then(() => {
      setDemoScenario(formData.value.simulationRequirement)
      router.push({
        name: 'DemoGraph',
        query: buildDemoQuery({
          scenario: formData.value.simulationRequirement,
        }),
      })
    })
    return
  }

  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(
      files.value,
      formData.value.simulationRequirement,
      undefined,
      normalizeSourceUrls(formData.value.sourceUrls)
    )
    router.push({
      name: 'Process',
      params: { projectId: 'new' },
    })
  })
}

const handleSignOut = async () => {
  await signOut()
  router.push('/')
}
</script>

<style scoped>
/* These live on the component root, not on :root. Vue compiles a scoped
   selector to :root[data-v-...], which matches nothing, so every var() below
   used to resolve to nothing: the orange tag lost its background, the mono
   labels fell back to the inherited sans, and every `border: 1px solid
   var(--border)` computed to no border at all. Both font families are loaded
   globally in index.html. */
.console-start-container {
  --black: #000000;
  --white: #ffffff;
  --orange: #ff4500;
  --gray-text: #666666;
  --border: #e5e5e5;
  --font-mono: 'JetBrains Mono', monospace;
  --font-sans: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
  min-height: 100vh;
  background: var(--white);
  font-family: var(--font-sans);
  color: var(--black);
}

.navbar {
  height: 60px;
  background: var(--white);
  color: var(--black);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  border-bottom: 1px solid var(--border);
}

.nav-brand {
  font-family: var(--font-mono);
  font-weight: 800;
  letter-spacing: 1px;
  font-size: 1.2rem;
  cursor: pointer;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 12px;
}

.session-email {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: #666;
}

.nav-action {
  border: 1px solid var(--border);
  background: var(--white);
  color: var(--black);
  padding: 8px 12px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  cursor: pointer;
}

.github-link {
  color: var(--black);
  text-decoration: none;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: opacity 0.2s;
}

.github-link:hover {
  opacity: 0.75;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px;
}

.hero-section {
  display: flex;
  align-items: flex-start;
  margin-bottom: 40px;
  position: relative;
  min-height: 300px;
  padding: 24px 0;
  overflow: hidden;
  background-image: var(--hero-image);
  background-position: right top;
  background-repeat: no-repeat;
  background-size: 340px;
}

.hero-left {
  flex: 0 1 720px;
}

.hero-copy-card {
  position: relative;
  z-index: 1;
  max-width: 720px;
}

.tag-row {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
}

.orange-tag {
  background: var(--orange);
  color: var(--white);
  padding: 4px 10px;
  font-weight: 700;
  letter-spacing: 1px;
  font-size: 0.75rem;
}

.version-text {
  color: #666;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.main-title {
  font-size: 4rem;
  line-height: 1.1;
  font-weight: 520;
  margin: 0 0 18px;
  letter-spacing: -2px;
  color: var(--black);
}

.hero-desc {
  font-size: 1.05rem;
  line-height: 1.8;
  color: #303030;
  max-width: 620px;
  margin-bottom: 28px;
}

.steps-container {
  border: 1px solid var(--border);
  padding: 30px;
  position: relative;
  max-width: 640px;
}

.steps-header {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.diamond-icon {
  font-size: 1.2rem;
  line-height: 1;
}

.workflow-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.workflow-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.step-num {
  font-family: var(--font-mono);
  font-weight: 700;
  color: var(--black);
  opacity: 0.3;
}

.step-info {
  flex: 1;
}

.step-title {
  font-weight: 520;
  font-size: 1rem;
  margin-bottom: 4px;
}

.step-desc {
  font-size: 0.85rem;
  color: var(--gray-text);
}

.dashboard-section {
  display: flex;
  gap: 60px;
  border-top: 1px solid var(--border);
  padding-top: 32px;
  align-items: flex-start;
}

.right-panel {
  flex: 1;
}

.full-width {
  width: 100%;
}

.console-box {
  border: 1px solid #ccc;
  padding: 8px;
}

.console-section {
  padding: 20px;
}

.console-section.btn-section {
  padding-top: 0;
}

.url-section {
  padding-top: 0;
}

/* The two spans butt straight up against each other once the row is narrow
   enough for space-between to have no space left to give. */
.console-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px 14px;
  margin-bottom: 15px;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: #666;
}

.pack-section {
  padding-bottom: 0;
}

.pack-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 8px;
}

.pack-card {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 12px 14px;
  border: 1px solid #ddd;
  background: #fafafa;
  color: var(--black);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.pack-card:hover {
  border-color: #999;
}

.pack-card.active {
  border-color: var(--black);
  background: var(--white);
}

.pack-card-label {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.pack-card-detail {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  line-height: 1.45;
  color: #777;
}

.pack-card.active .pack-card-detail {
  color: #555;
}

.upload-zone {
  border: 1px dashed #ccc;
  min-height: 200px;
  overflow-y: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
}

.upload-zone.has-files {
  align-items: flex-start;
}

.upload-zone.drag-over,
.upload-zone:hover {
  background: #f0f0f0;
  border-color: #999;
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  width: 40px;
  height: 40px;
  border: 1px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
  color: #999;
}

.upload-title {
  font-weight: 500;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.upload-hint {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: #999;
}

.file-list {
  width: 100%;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  background: var(--white);
  padding: 8px 12px;
  border: 1px solid #eee;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  gap: 10px;
}

.file-icon {
  font-size: 0.72rem;
  color: #999;
}

.file-name {
  flex: 1;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  color: #999;
}

.file-item--seed {
  align-items: flex-start;
  border-color: #ddd;
  animation: seed-in 0.2s ease-out both;
}

@keyframes seed-in {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

.file-kind {
  flex: none;
  min-width: 42px;
  padding: 2px 5px;
  border: 1px solid #ccc;
  color: #555;
  font-size: 0.65rem;
  letter-spacing: 0.5px;
  text-align: center;
}

.file-item--seed .file-name {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
  overflow-wrap: anywhere;
}

.file-note {
  font-size: 0.7rem;
  color: #999;
}

.file-attached {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: none;
  font-size: 0.68rem;
  color: #999;
}

/* Drawn rather than set as a glyph, so no font substitutes an emoji tick. */
.file-attached::before {
  content: '';
  width: 4px;
  height: 8px;
  border-right: 2px solid #ff4500;
  border-bottom: 2px solid #ff4500;
  transform: translateY(-1px) rotate(45deg);
}

.seed-add-hint {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: #999;
  padding-top: 2px;
}

.draft-brief-btn {
  border: 1px solid #ddd;
  background: var(--white);
  color: var(--black);
  padding: 4px 10px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  letter-spacing: 0.3px;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}

.draft-brief-btn:not(:disabled):hover {
  border-color: #ff4500;
  color: #ff4500;
}

.draft-brief-btn:disabled {
  color: #aaa;
  cursor: progress;
}

.draft-brief-hint {
  margin: -8px 0 12px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #999;
}

@media (prefers-reduced-motion: reduce) {
  .file-item--seed {
    animation: none;
  }
}

.console-divider {
  display: flex;
  align-items: center;
  margin: 10px 0;
}

.console-divider::before,
.console-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #eee;
}

.console-divider span {
  padding: 0 15px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #bbb;
  letter-spacing: 1px;
}

.input-wrapper {
  position: relative;
  border: 1px solid #ddd;
  background: #fafafa;
}

.url-input-wrapper {
  min-height: 132px;
}

.code-input {
  width: 100%;
  border: none;
  background: transparent;
  padding: 20px;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  min-height: 150px;
}

.url-input {
  min-height: 120px;
}

.model-badge {
  position: absolute;
  bottom: 10px;
  right: 15px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #aaa;
}

.start-engine-btn {
  width: 100%;
  background: var(--black);
  color: var(--white);
  border: none;
  padding: 20px;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 1.1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 1px;
}

/* Two glyphs that have to stay one mark: once the label wrapped, the ">" was
   being carried onto the next line on its own. */
.btn-arrow {
  flex: none;
  white-space: nowrap;
}

.start-engine-btn:not(:disabled):hover {
  background: var(--orange);
}

.start-engine-btn:disabled {
  background: #e5e5e5;
  color: #999;
  cursor: not-allowed;
}

@media (max-width: 1024px) {
  .main-content {
    padding: 28px 20px;
  }

  .hero-section {
    background-size: 220px;
    background-position: right top;
  }
}

@media (max-width: 768px) {
  .navbar {
    padding: 12px 16px;
    height: auto;
    min-height: 60px;
    flex-wrap: wrap;
    gap: 12px;
  }

  .nav-links {
    width: 100%;
    justify-content: flex-end;
    flex-wrap: wrap;
  }

  .nav-action,
  .github-link {
    min-height: 40px;
    display: flex;
    align-items: center;
  }

  .main-title {
    font-size: 2.8rem;
  }

  .main-content {
    padding: 20px 16px;
  }

  /* The logo is anchored to the right of the hero, and at this width the hero
     is narrower than the logo. It was printing straight through the title. */
  .hero-section {
    background-image: none;
    min-height: 0;
    margin-bottom: 28px;
    padding: 8px 0 0;
  }

  .steps-container {
    padding: 20px 16px;
  }

  .workflow-item {
    gap: 14px;
  }

  /* 8px of box plus 20px of section on each side left the inputs barely wider
     than their own labels. */
  .console-section {
    padding: 16px 12px;
  }

  .console-box {
    padding: 4px;
  }

  .pack-grid {
    grid-template-columns: 1fr;
  }

  .file-list {
    padding: 12px;
  }

  .file-item {
    font-size: 0.8rem;
    gap: 8px;
  }

  .code-input {
    padding: 14px;
    min-height: 130px;
    font-size: 0.85rem;
  }

  .start-engine-btn {
    padding: 16px 14px;
    font-size: 0.95rem;
    letter-spacing: 0.5px;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .main-title {
    font-size: 2.2rem;
    letter-spacing: -1px;
  }

  .hero-desc {
    font-size: 0.95rem;
    line-height: 1.65;
  }
}
</style>
