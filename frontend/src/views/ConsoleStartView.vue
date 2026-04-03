<template>
  <div class="console-start-container">
    <nav class="navbar">
      <div class="nav-brand" @click="router.push('/')">OPS</div>
      <div class="nav-links">
        <span class="session-email" v-if="authState.user?.email">{{ authState.user.email }}</span>
        <button class="nav-action" type="button" @click="handleSignOut">Sign out</button>
        <a href="https://github.com/ripclass/OPS" target="_blank" rel="noreferrer" class="github-link">
          GitHub <span class="arrow">&gt;</span>
        </a>
      </div>
    </nav>

    <div class="main-content">
      <section class="hero-section" :style="heroSectionStyle">
        <div class="hero-left hero-copy-card">
          <div class="tag-row">
            <span class="orange-tag">OPS Console</span>
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
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">01 / Source Material</span>
                <span class="console-meta">Optional Uploads: PDF, MD, MARKDOWN, TXT</span>
              </div>

              <div
                class="upload-zone"
                :class="{ 'drag-over': isDragOver, 'has-files': files.length > 0 }"
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
              </div>
              <div class="input-wrapper">
                <textarea
                  v-model="formData.simulationRequirement"
                  class="code-input"
                  rows="6"
                  :disabled="loading"
                  placeholder="Describe the trigger you want to test. Example: The government announces a 40% rice price increase before Eid. How do low-income households in Dhaka respond?"
                ></textarea>
                <div class="model-badge">Engine: OPS / OASIS</div>
              </div>
            </div>

            <div class="console-section btn-section">
              <button
                class="start-engine-btn"
                :disabled="!canSubmit || loading"
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

      <HistoryDatabase />
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import HistoryDatabase from '../components/HistoryDatabase.vue'
import { authState, signOut } from '../store/auth'

const router = useRouter()
const heroImageUrl = new URL('../assets/logo/ops_logo_left.png', import.meta.url).href

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

const canSubmit = computed(() => formData.value.simulationRequirement.trim() !== '')
const heroSectionStyle = computed(() => ({
  '--hero-image': `url("${heroImageUrl}")`,
}))

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
:root {
  --black: #000000;
  --white: #ffffff;
  --orange: #ff4500;
  --gray-text: #666666;
  --border: #e5e5e5;
  --font-mono: 'JetBrains Mono', monospace;
  --font-sans: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
}

.console-start-container {
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

.console-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: #666;
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
    padding: 0 18px;
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

  .main-title {
    font-size: 2.8rem;
  }

  .main-content {
    padding: 20px 16px;
  }
}
</style>
