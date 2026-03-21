<template>
  <div class="ops-run-dashboard">
    <header class="dashboard-header">
      <div class="brand-lockup">
        <button type="button" class="back-link" @click="goBackToSetup">
          Back to configuration
        </button>
        <div class="brand-mark">OPS</div>
        <div class="brand-copy">
          <div class="brand-name">Organic Population Simulation</div>
          <div class="brand-tagline">How South Asia actually responds</div>
        </div>
      </div>

      <div class="header-actions">
        <button type="button" class="ghost-btn" :disabled="isRefreshing" @click="refreshDashboard">
          {{ isRefreshing ? 'Refreshing...' : 'Refresh now' }}
        </button>
        <button
          v-if="isRunnable && !isStarting"
          type="button"
          class="ghost-btn"
          :disabled="isStopping"
          @click="handleStopSimulation"
        >
          {{ isStopping ? 'Stopping...' : 'Stop run' }}
        </button>
        <button
          v-if="isCompleted"
          type="button"
          class="primary-btn"
          :disabled="isGeneratingReport"
          @click="handleGenerateReport"
        >
          {{ isGeneratingReport ? 'Preparing report...' : 'Generate insight report' }}
        </button>
      </div>
    </header>

    <main class="dashboard-shell">
      <section class="hero-panel">
        <div class="hero-copy">
          <div class="hero-kicker">Live Simulation Dashboard</div>
          <h1>{{ projectData?.name || `OPS Run ${simulationId}` }}</h1>
          <p>{{ scenarioSummary }}</p>

          <div class="hero-chips">
            <span v-if="wizardMetadata.useCase" class="meta-chip">{{ wizardMetadata.useCase }}</span>
            <span v-if="wizardMetadata.country" class="meta-chip">{{ wizardMetadata.country }}</span>
            <span v-if="wizardMetadata.segments" class="meta-chip">{{ wizardMetadata.segments }}</span>
            <span v-if="wizardMetadata.targetAgents" class="meta-chip">
              {{ wizardMetadata.targetAgents }} agents
            </span>
            <span class="meta-chip subtle">Polling every 5s</span>
          </div>
        </div>

        <div class="hero-status-card">
          <div class="status-row">
            <div>
              <div class="status-label">Run status</div>
              <div class="status-value" :class="statusToneClass">{{ statusLabel }}</div>
            </div>
            <div class="status-percent">{{ progressLabel }}</div>
          </div>

          <div class="progress-track">
            <div class="progress-fill" :style="{ width: `${progressPercent}%` }"></div>
          </div>

          <div class="status-grid">
            <div class="status-item">
              <span class="status-item-label">Elapsed</span>
              <span class="status-item-value">{{ elapsedLabel }}</span>
            </div>
            <div class="status-item">
              <span class="status-item-label">Time remaining</span>
              <span class="status-item-value">{{ etaLabel }}</span>
            </div>
            <div class="status-item">
              <span class="status-item-label">Rounds</span>
              <span class="status-item-value">{{ roundLabel }}</span>
            </div>
            <div class="status-item">
              <span class="status-item-label">Last sync</span>
              <span class="status-item-value">{{ lastRefreshLabel }}</span>
            </div>
          </div>

          <div class="platform-strip">
            <div
              v-for="platform in platformCards"
              :key="platform.key"
              class="platform-card"
              :class="platform.state"
            >
              <div class="platform-title">{{ platform.label }}</div>
              <div class="platform-detail">{{ platform.detail }}</div>
            </div>
          </div>
        </div>
      </section>

      <section v-if="errorMessage" class="error-banner">
        <div class="error-title">Dashboard warning</div>
        <div class="error-copy">{{ errorMessage }}</div>
      </section>

      <section class="stat-grid">
        <article class="stat-card">
          <div class="stat-label">Agents responded</div>
          <div class="stat-value">{{ formatNumber(respondedAgentsCount) }}</div>
          <div class="stat-note">Unique agents with public actions in this run</div>
        </article>
        <article class="stat-card">
          <div class="stat-label">Sharing news</div>
          <div class="stat-value">{{ formatNumber(sharingAgentsCount) }}</div>
          <div class="stat-note">Agents actively reposting, quoting, or broadcasting</div>
        </article>
        <article class="stat-card accent">
          <div class="stat-label">Total reach</div>
          <div class="stat-value">{{ formatNumber(totalReachEstimate) }}</div>
          <div class="stat-note">Estimated secondary reach from visible public activity</div>
        </article>
      </section>

      <section class="dashboard-grid">
        <article class="emotion-card">
          <div class="panel-heading">
            <div>
              <div class="panel-kicker">Pulse</div>
              <h2>Emotion distribution</h2>
            </div>
            <span class="panel-caption">Derived from live post text and action patterns</span>
          </div>

          <div class="emotion-stack">
            <div v-for="item in emotionDistribution" :key="item.label" class="emotion-row">
              <div class="emotion-head">
                <span>{{ item.label }}</span>
                <span>{{ item.count }}</span>
              </div>
              <div class="emotion-track">
                <div
                  class="emotion-fill"
                  :class="item.tone"
                  :style="{ width: `${item.percent}%` }"
                ></div>
              </div>
            </div>
          </div>
        </article>

        <article class="amplifier-card">
          <div class="panel-heading">
            <div>
              <div class="panel-kicker">Network pressure</div>
              <h2>Amplifier nodes</h2>
            </div>
            <span class="panel-caption">Weighted by reach, intensity, and share behavior</span>
          </div>

          <div v-if="topAmplifiers.length" class="amplifier-list">
            <div v-for="agent in topAmplifiers" :key="agent.lookupKey" class="amplifier-row">
              <div>
                <div class="amplifier-name">{{ agent.name }}</div>
                <div class="amplifier-meta">
                  {{ agent.profession }} / {{ agent.location }} / {{ formatNumber(agent.reach) }} reach
                </div>
              </div>
              <div class="amplifier-score">{{ Math.round(agent.score) }}</div>
            </div>
          </div>
          <div v-else class="empty-panel">
            Amplifier scoring will appear once agent actions begin streaming in.
          </div>
        </article>
      </section>

      <section class="feed-panel">
        <div class="panel-heading">
          <div>
            <div class="panel-kicker">Live feed</div>
            <h2>Agent posts and shares</h2>
          </div>
          <span class="panel-caption">Bangla text with an English summary below</span>
        </div>

        <div v-if="isLoading && !feedItems.length" class="feed-empty">
          Waiting for the first wave of responses...
        </div>

        <div v-else-if="!feedItems.length" class="feed-empty">
          No public posts have been recorded yet. The dashboard will refresh automatically.
        </div>

        <div v-else class="feed-list">
          <article
            v-for="item in feedItems"
            :key="item.id"
            class="feed-card"
            :class="{ amplifier: item.isAmplifier }"
          >
            <div class="feed-topline">
              <div>
                <div class="feed-name-row">
                  <h3>{{ item.name }}</h3>
                  <span v-if="item.isAmplifier" class="amp-badge">Amplifier node</span>
                </div>
                <div class="feed-meta">
                  <span>{{ item.ageLabel }}</span>
                  <span>{{ item.location }}</span>
                  <span>{{ item.occupation }}</span>
                </div>
              </div>

              <div class="feed-badges">
                <span class="emotion-badge" :class="item.emotionTone">{{ item.emotion }}</span>
                <span class="platform-badge">{{ item.platformLabel }}</span>
                <span class="share-badge">{{ formatNumber(item.shareCount) }} shares</span>
              </div>
            </div>

            <div class="feed-copy">
              <div class="copy-block">
                <div class="copy-label">Bangla post</div>
                <p>{{ item.originalText }}</p>
              </div>

              <div class="copy-block translation">
                <div class="copy-label">English translation</div>
                <p>{{ item.translation }}</p>
              </div>
            </div>

            <div class="feed-footer">
              <span>Estimated reach {{ formatNumber(item.estimatedReach) }}</span>
              <span>Round {{ item.round }}</span>
              <span>{{ item.timeLabel }}</span>
            </div>
          </article>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProject } from '../api/graph'
import {
  getAgentStats,
  getRunStatus,
  getRunStatusDetail,
  getSimulation,
  getSimulationConfig,
  getSimulationProfiles,
  startSimulation,
  stopSimulation,
} from '../api/simulation'
import { generateReport } from '../api/report'

const props = defineProps({
  simulationId: String,
})

const route = useRoute()
const router = useRouter()

const publicActionTypes = new Set([
  'CREATE_POST',
  'CREATE_COMMENT',
  'QUOTE_POST',
  'REPOST',
  'UPVOTE_POST',
  'DOWNVOTE_POST',
])
const shareActionTypes = new Set(['REPOST', 'QUOTE_POST'])
const emotionBuckets = ['Worried', 'Angry', 'Resigned', 'Calm', 'Other']

const simulationId = computed(() => props.simulationId || route.params.simulationId)
const maxRoundsOverride = computed(() => {
  const raw = route.query.maxRounds
  return raw ? Number.parseInt(raw, 10) : null
})

const simulationData = ref(null)
const projectData = ref(null)
const minutesPerRound = ref(30)
const runStatus = ref({})
const rawActions = ref([])
const agentStatsIndex = ref({})
const profileIndex = ref({})

const isLoading = ref(true)
const isRefreshing = ref(false)
const isStarting = ref(false)
const isStopping = ref(false)
const isGeneratingReport = ref(false)
const errorMessage = ref('')
const lastRefreshAt = ref(null)
const lastObservedNow = ref(Date.now())
const hasAttemptedAutoStart = ref(false)

let pollTimer = null

function parseWizardMetadata(text) {
  const source = String(text || '')
  const match = source.match(/\[OPS Wizard Metadata\]([\s\S]*?)\[\/OPS Wizard Metadata\]/)
  if (!match) {
    return {}
  }

  const metadata = {}
  const lines = match[1]
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)

  for (const line of lines) {
    const separator = line.indexOf(':')
    if (separator === -1) {
      continue
    }

    const label = line.slice(0, separator).trim().toLowerCase()
    const value = line.slice(separator + 1).trim()
    if (!value) {
      continue
    }

    if (label === 'use case') metadata.useCase = value
    if (label === 'country') metadata.country = value
    if (label === 'segments') metadata.segments = value
    if (label === 'target agents') metadata.targetAgents = value
    if (label === 'requested outputs') metadata.outputs = value
  }

  return metadata
}

function extractScenarioText(text) {
  const source = String(text || '').trim()
  if (!source) {
    return 'The run is initializing. Scenario details will appear here once the project metadata loads.'
  }

  const scenarioMatch = source.match(/Scenario:\s*([\s\S]*)$/)
  const body = scenarioMatch
    ? scenarioMatch[1].trim()
    : source.replace(/\[OPS Wizard Metadata\][\s\S]*?\[\/OPS Wizard Metadata\]/g, '').trim()

  if (!body) {
    return 'The run is initializing. Scenario details will appear here once the project metadata loads.'
  }

  return body.length > 280 ? `${body.slice(0, 277).trim()}...` : body
}

function toLookupKeys(value) {
  if (value === null || value === undefined) {
    return []
  }
  const normalized = String(value).trim()
  if (!normalized) {
    return []
  }
  const lowered = normalized.toLowerCase()
  return lowered === normalized ? [normalized] : [normalized, lowered]
}

function mergeProfiles(profiles) {
  const grouped = {}
  for (const profile of profiles) {
    const anchor =
      profile.user_id ??
      profile.agent_id ??
      profile.username ??
      profile.user_name ??
      profile.name

    const anchorKey = anchor === undefined || anchor === null ? null : String(anchor)
    const groupKey = anchorKey || `${profile.name || 'agent'}-${profiles.indexOf(profile)}`
    grouped[groupKey] = {
      ...(grouped[groupKey] || {}),
      ...profile,
    }
  }

  const nextIndex = {}
  for (const merged of Object.values(grouped)) {
    const keys = [
      ...toLookupKeys(merged.user_id),
      ...toLookupKeys(merged.agent_id),
      ...toLookupKeys(merged.username),
      ...toLookupKeys(merged.user_name),
      ...toLookupKeys(merged.name),
    ]
    for (const key of keys) {
      nextIndex[key] = merged
    }
  }

  profileIndex.value = nextIndex
}

function buildAgentStatsIndex(stats) {
  const nextIndex = {}
  for (const item of stats || []) {
    for (const key of [...toLookupKeys(item.agent_id), ...toLookupKeys(item.agent_name)]) {
      nextIndex[key] = item
    }
  }
  agentStatsIndex.value = nextIndex
}

function resolveProfile(action) {
  const candidates = [...toLookupKeys(action?.agent_id), ...toLookupKeys(action?.agent_name)]
  for (const key of candidates) {
    if (profileIndex.value[key]) {
      return profileIndex.value[key]
    }
  }
  return null
}

function resolveAgentStats(action) {
  const candidates = [...toLookupKeys(action?.agent_id), ...toLookupKeys(action?.agent_name)]
  for (const key of candidates) {
    if (agentStatsIndex.value[key]) {
      return agentStatsIndex.value[key]
    }
  }
  return null
}

function safeDate(value) {
  if (!value) {
    return null
  }
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

function formatDuration(ms) {
  if (!ms || ms <= 0) {
    return '0m'
  }

  const totalSeconds = Math.max(0, Math.round(ms / 1000))
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60

  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  if (minutes > 0) {
    return `${minutes}m ${seconds}s`
  }
  return `${seconds}s`
}

function formatTime(value) {
  const parsed = safeDate(value)
  if (!parsed) {
    return '--'
  }
  return parsed.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

function formatNumber(value) {
  const numeric = Number(value || 0)
  return new Intl.NumberFormat('en-US').format(Number.isFinite(numeric) ? numeric : 0)
}

function extractActionText(action) {
  const args = action?.action_args || {}
  return (
    args.content ||
    args.quote_content ||
    args.original_content ||
    args.post_content ||
    args.comment_content ||
    ''
  )
}

function containsBangla(text) {
  return /[\u0980-\u09FF]/.test(text || '')
}

function inferEmotion(text, actionType = '') {
  const content = String(text || '').toLowerCase()
  const type = String(actionType || '').toUpperCase()

  if (
    /রাগ|ক্ষোভ|anger|angry|betray|outrage|protest|corrupt|unfair|shame/i.test(content) ||
    type === 'DOWNVOTE_POST'
  ) {
    return 'Angry'
  }

  if (
    /চিন্তা|উদ্বেগ|ভয়|ভয়|কষ্ট|worry|worried|fear|anxiety|pressure|stress|cost|price|hardship/i.test(content) ||
    type === 'REPOST'
  ) {
    return 'Worried'
  }

  if (/চলতে হবে|কি আর|মেনে|সহ্য|resign|resigned|helpless|nothing to do|survive somehow/i.test(content)) {
    return 'Resigned'
  }

  if (
    /শান্ত|আশা|ভরসা|স্বস্তি|calm|relief|hope|support|manageable|stable/i.test(content) ||
    type === 'UPVOTE_POST'
  ) {
    return 'Calm'
  }

  return 'Other'
}

function emotionToneClass(emotion) {
  return {
    Worried: 'worried',
    Angry: 'angry',
    Resigned: 'resigned',
    Calm: 'calm',
    Other: 'other',
  }[emotion] || 'other'
}

function buildEnglishSummary(text, emotion) {
  const source = String(text || '').trim()
  if (!source) {
    return 'No public text was captured for this action.'
  }

  if (!containsBangla(source)) {
    return source.length > 220 ? `${source.slice(0, 217).trim()}...` : source
  }

  const themes = []
  const themeMatchers = [
    [/চাল|rice/i, 'rice prices'],
    [/দাম|মূল্য|price/i, 'price pressure'],
    [/সরকার|government/i, 'the government'],
    [/ভর্তুকি|subsid/i, 'relief subsidy'],
    [/ছেলে|মেয়ে|শিক্ষা|পড়াশোনা|পড়াশোনা|education/i, "children's education"],
    [/সংসার|পরিবার|family/i, 'family finances'],
    [/কাজ|রোজগার|income|wage|salary/i, 'income stability'],
    [/গুজব|rumou?r|unverified/i, 'unverified information'],
    [/বাজার|market/i, 'market conditions'],
  ]

  for (const [pattern, label] of themeMatchers) {
    if (pattern.test(source)) {
      themes.push(label)
    }
  }

  const uniqueThemes = [...new Set(themes)]
  const lead = {
    Worried: 'Expresses worry about',
    Angry: 'Expresses anger about',
    Resigned: 'Shows resignation about',
    Calm: 'Takes a calmer tone on',
    Other: 'Publicly comments on',
  }[emotion] || 'Publicly comments on'

  if (uniqueThemes.length) {
    return `${lead} ${uniqueThemes.join(', ')}.`
  }

  return 'Public Bangla post reacting to the scenario and its impact on daily life.'
}

function estimateReach(profile, stats, shareCount) {
  const influenceRadius = Number(profile?.influence_radius || 0)
  const followerCount = Number(profile?.follower_count || 0)
  const friendCount = Number(profile?.friend_count || 0)
  const statsActions = Number(stats?.total_actions || 0)
  const shareMultiplier = Math.max(1, Number(shareCount || 0))

  if (influenceRadius > 0) {
    return influenceRadius * shareMultiplier
  }
  if (followerCount > 0) {
    return Math.round(followerCount * 0.35 * shareMultiplier)
  }
  if (friendCount > 0) {
    return Math.round(friendCount * 0.6 * shareMultiplier)
  }
  return Math.max(15, statsActions * 18)
}

function buildAmplifierScore(profile, stats, shareCount) {
  const reach = estimateReach(profile, stats, shareCount)
  const intensity = Number(profile?.fb_intensity || 0)
  const totalActions = Number(stats?.total_actions || 0)
  return reach + intensity * 20 + totalActions * 12 + Number(shareCount || 0) * 35
}

function actionLookupKey(action) {
  return String(action?.agent_id ?? action?.agent_name ?? 'unknown')
}

function isFeedAction(action) {
  if (!action) {
    return false
  }
  if (publicActionTypes.has(action.action_type)) {
    return true
  }
  return Boolean(extractActionText(action))
}

function isShareLike(action) {
  return shareActionTypes.has(String(action?.action_type || '').toUpperCase())
}

function checkPlatformsCompleted(status) {
  if (!status) {
    return false
  }

  const twitterEnabled = Boolean(simulationData.value?.enable_twitter)
  const redditEnabled = Boolean(simulationData.value?.enable_reddit)

  if (twitterEnabled && !status.twitter_completed) {
    return false
  }
  if (redditEnabled && !status.reddit_completed) {
    return false
  }

  return twitterEnabled || redditEnabled
}

async function fetchProfiles() {
  const responses = await Promise.allSettled([
    getSimulationProfiles(simulationId.value, 'reddit'),
    getSimulationProfiles(simulationId.value, 'twitter'),
  ])

  const profiles = []
  for (const response of responses) {
    if (response.status === 'fulfilled') {
      profiles.push(...(response.value.data?.profiles || []))
    }
  }

  mergeProfiles(profiles)
}

async function loadBaseData() {
  const [simulationResponse, configResponse] = await Promise.allSettled([
    getSimulation(simulationId.value),
    getSimulationConfig(simulationId.value),
  ])

  if (simulationResponse.status === 'fulfilled') {
    simulationData.value = simulationResponse.value.data
    if (simulationData.value?.project_id) {
      try {
        const projectResponse = await getProject(simulationData.value.project_id)
        projectData.value = projectResponse.data
      } catch (error) {
        errorMessage.value = `Project metadata failed to load: ${error.message}`
      }
    }
  } else {
    errorMessage.value = `Simulation metadata failed to load: ${simulationResponse.reason?.message || 'Unknown error'}`
  }

  if (configResponse.status === 'fulfilled') {
    const configuredMinutes = Number(configResponse.value.data?.time_config?.minutes_per_round || 30)
    minutesPerRound.value = configuredMinutes > 0 ? configuredMinutes : 30
  }
}

async function refreshLiveData({ includeProfiles = false } = {}) {
  if (!simulationId.value || isRefreshing.value) {
    return
  }

  isRefreshing.value = true
  lastObservedNow.value = Date.now()

  try {
    const promises = [
      getRunStatus(simulationId.value),
      getRunStatusDetail(simulationId.value),
      getAgentStats(simulationId.value),
    ]

    if (includeProfiles) {
      promises.push(fetchProfiles())
    }

    const responses = await Promise.allSettled(promises)
    const [statusResponse, detailResponse, statsResponse] = responses

    if (statusResponse.status === 'fulfilled') {
      runStatus.value = {
        ...runStatus.value,
        ...statusResponse.value.data,
      }
      errorMessage.value = ''
    }

    if (detailResponse.status === 'fulfilled') {
      rawActions.value = detailResponse.value.data?.all_actions || []
      runStatus.value = {
        ...runStatus.value,
        ...detailResponse.value.data,
      }
    }

    if (statsResponse.status === 'fulfilled') {
      buildAgentStatsIndex(statsResponse.value.data?.stats || [])
    }

    if (responses.some((item) => item.status === 'rejected')) {
      const firstError = responses.find((item) => item.status === 'rejected')
      errorMessage.value = firstError?.reason?.message || 'One or more live dashboard requests failed.'
    }

    lastRefreshAt.value = new Date().toISOString()

    if (isCompleted.value) {
      stopPolling()
    }
  } finally {
    isRefreshing.value = false
  }
}

async function doStartSimulation() {
  if (!simulationId.value || isStarting.value) {
    return
  }

  isStarting.value = true
  errorMessage.value = ''

  try {
    const payload = {
      simulation_id: simulationId.value,
    }
    if (maxRoundsOverride.value) {
      payload.max_rounds = maxRoundsOverride.value
    }

    const response = await startSimulation(payload)
    runStatus.value = {
      ...runStatus.value,
      ...(response.data || {}),
    }
    await refreshLiveData()
  } catch (error) {
    errorMessage.value = `Simulation start failed: ${error.message}`
  } finally {
    isStarting.value = false
  }
}

async function maybeAutoStart() {
  const liveStatus = String(runStatus.value?.runner_status || '').toLowerCase()
  const simulationStatus = String(simulationData.value?.status || '').toLowerCase()

  if (hasAttemptedAutoStart.value) {
    return
  }

  if (
    liveStatus === 'running' ||
    simulationStatus === 'running' ||
    runStatus.value?.twitter_running ||
    runStatus.value?.reddit_running
  ) {
    return
  }

  if (
    liveStatus === 'completed' ||
    liveStatus === 'stopped' ||
    simulationStatus === 'completed' ||
    simulationStatus === 'stopped'
  ) {
    return
  }

  hasAttemptedAutoStart.value = true
  await doStartSimulation()
}

function startPolling() {
  if (pollTimer) {
    return
  }

  pollTimer = setInterval(() => {
    refreshLiveData()
  }, 5000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function refreshDashboard() {
  await refreshLiveData({ includeProfiles: Object.keys(profileIndex.value).length === 0 })
}

async function handleStopSimulation() {
  if (!simulationId.value || isStopping.value) {
    return
  }

  isStopping.value = true
  try {
    await stopSimulation({ simulation_id: simulationId.value })
    await refreshLiveData()
  } catch (error) {
    errorMessage.value = `Simulation stop failed: ${error.message}`
  } finally {
    isStopping.value = false
  }
}

async function handleGenerateReport() {
  if (!simulationId.value || isGeneratingReport.value) {
    return
  }

  isGeneratingReport.value = true
  try {
    const response = await generateReport({
      simulation_id: simulationId.value,
      force_regenerate: true,
    })
    router.push({ name: 'Report', params: { reportId: response.data?.report_id } })
  } catch (error) {
    errorMessage.value = `Report generation failed: ${error.message}`
  } finally {
    isGeneratingReport.value = false
  }
}

function goBackToSetup() {
  router.push({ name: 'Simulation', params: { simulationId: simulationId.value } })
}

const wizardMetadata = computed(() => parseWizardMetadata(projectData.value?.simulation_requirement || ''))
const scenarioSummary = computed(() => extractScenarioText(projectData.value?.simulation_requirement || projectData.value?.analysis_summary || ''))

const progressPercent = computed(() => {
  const raw = Number(runStatus.value?.progress_percent || 0)
  if (!Number.isFinite(raw)) {
    return 0
  }
  return Math.max(0, Math.min(100, raw))
})

const progressLabel = computed(() => `${progressPercent.value.toFixed(0)}%`)

const statusLabel = computed(() => {
  if (isStarting.value) return 'Launching'
  if (isStopping.value) return 'Stopping'
  const state = String(runStatus.value?.runner_status || simulationData.value?.status || 'idle')
  return state.charAt(0).toUpperCase() + state.slice(1)
})

const statusToneClass = computed(() => {
  if (statusLabel.value === 'Completed') return 'success'
  if (statusLabel.value === 'Stopped') return 'stopped'
  if (statusLabel.value === 'Failed' || statusLabel.value === 'Error') return 'error'
  return 'live'
})

const isRunnable = computed(() => {
  const state = String(runStatus.value?.runner_status || simulationData.value?.status || '').toLowerCase()
  return state === 'running' || runStatus.value?.twitter_running || runStatus.value?.reddit_running
})

const isCompleted = computed(() => {
  const state = String(runStatus.value?.runner_status || simulationData.value?.status || '').toLowerCase()
  return state === 'completed' || state === 'stopped' || checkPlatformsCompleted(runStatus.value)
})

const currentRound = computed(() => {
  const candidates = [
    Number(runStatus.value?.current_round || 0),
    Number(runStatus.value?.twitter_current_round || 0),
    Number(runStatus.value?.reddit_current_round || 0),
  ]
  return Math.max(...candidates)
})

const totalRounds = computed(() => Number(runStatus.value?.total_rounds || maxRoundsOverride.value || 0))
const roundLabel = computed(() => (totalRounds.value ? `${currentRound.value} / ${totalRounds.value}` : `${currentRound.value}`))

const elapsedMs = computed(() => {
  const startedAt = safeDate(runStatus.value?.started_at)
  if (!startedAt) {
    return 0
  }
  return Math.max(0, lastObservedNow.value - startedAt.getTime())
})

const elapsedLabel = computed(() => formatDuration(elapsedMs.value))

const etaLabel = computed(() => {
  if (isCompleted.value) {
    return 'Completed'
  }
  if (!progressPercent.value || progressPercent.value <= 0) {
    return 'Estimating...'
  }
  const totalEstimate = elapsedMs.value / (progressPercent.value / 100)
  return formatDuration(Math.max(0, totalEstimate - elapsedMs.value))
})

const lastRefreshLabel = computed(() => (lastRefreshAt.value ? formatTime(lastRefreshAt.value) : 'Waiting...'))

const platformCards = computed(() => {
  const cards = []

  if (simulationData.value?.enable_twitter) {
    cards.push({
      key: 'twitter',
      label: 'Info Plaza',
      state: runStatus.value?.twitter_completed ? 'completed' : runStatus.value?.twitter_running ? 'active' : 'idle',
      detail: runStatus.value?.twitter_completed
        ? 'Completed'
        : runStatus.value?.twitter_running
          ? `Round ${runStatus.value?.twitter_current_round || 0}`
          : 'Queued',
    })
  }

  if (simulationData.value?.enable_reddit) {
    cards.push({
      key: 'reddit',
      label: 'Topic Community',
      state: runStatus.value?.reddit_completed ? 'completed' : runStatus.value?.reddit_running ? 'active' : 'idle',
      detail: runStatus.value?.reddit_completed
        ? 'Completed'
        : runStatus.value?.reddit_running
          ? `Round ${runStatus.value?.reddit_current_round || 0}`
          : 'Queued',
    })
  }

  return cards
})

const shareCountsByAgent = computed(() => {
  const counts = {}
  for (const action of rawActions.value) {
    const key = actionLookupKey(action)
    if (isShareLike(action)) {
      counts[key] = (counts[key] || 0) + 1
    }
  }
  return counts
})

const respondedAgentsCount = computed(() => {
  const unique = new Set(
    rawActions.value
      .filter((action) => String(action.action_type || '').toUpperCase() !== 'DO_NOTHING')
      .map((action) => actionLookupKey(action))
  )
  return unique.size
})

const sharingAgentsCount = computed(() => {
  const unique = new Set(
    rawActions.value.filter((action) => isShareLike(action)).map((action) => actionLookupKey(action))
  )
  return unique.size
})

const topAmplifiers = computed(() => {
  const agents = []
  const seen = new Set()

  for (const action of rawActions.value) {
    const lookupKey = actionLookupKey(action)
    if (seen.has(lookupKey)) {
      continue
    }
    seen.add(lookupKey)

    const profile = resolveProfile(action)
    const stats = resolveAgentStats(action)
    const shareCount = shareCountsByAgent.value[lookupKey] || 0
    const score = buildAmplifierScore(profile, stats, shareCount)
    const reach = estimateReach(profile, stats, shareCount)

    agents.push({
      lookupKey,
      name: profile?.name || action.agent_name || 'Unknown agent',
      profession: profile?.profession || 'Resident',
      location: profile?.country || 'South Asia',
      reach,
      score,
    })
  }

  return agents.sort((a, b) => b.score - a.score).slice(0, 5)
})

const amplifierLookup = computed(() => new Set(topAmplifiers.value.map((agent) => agent.lookupKey)))

const totalReachEstimate = computed(() => {
  let total = 0
  const seen = new Set()
  for (const action of rawActions.value) {
    const lookupKey = actionLookupKey(action)
    if (seen.has(lookupKey)) {
      continue
    }
    seen.add(lookupKey)
    const profile = resolveProfile(action)
    const stats = resolveAgentStats(action)
    total += estimateReach(profile, stats, shareCountsByAgent.value[lookupKey] || 0)
  }
  return total
})

const feedItems = computed(() => {
  return rawActions.value
    .filter((action) => isFeedAction(action))
    .map((action) => {
      const profile = resolveProfile(action)
      const stats = resolveAgentStats(action)
      const originalText = extractActionText(action) || 'No public text was recorded for this action.'
      const emotion = inferEmotion(originalText, action.action_type)
      const lookupKey = actionLookupKey(action)
      const shareCount = shareCountsByAgent.value[lookupKey] || 0
      const estimatedReach = estimateReach(profile, stats, shareCount)

      return {
        id:
          action.id ||
          `${action.timestamp || 'no-time'}-${action.platform || 'unknown'}-${lookupKey}-${action.action_type || 'action'}`,
        lookupKey,
        name: profile?.name || action.agent_name || 'Unknown agent',
        ageLabel: profile?.age ? `Age ${profile.age}` : 'Age n/a',
        location: profile?.country || 'South Asia',
        occupation: profile?.profession || 'Community member',
        emotion,
        emotionTone: emotionToneClass(emotion),
        platformLabel: action.platform === 'twitter' ? 'Info Plaza' : 'Topic Community',
        shareCount,
        originalText,
        translation: buildEnglishSummary(originalText, emotion),
        estimatedReach,
        round: action.round_num || 0,
        timeLabel: formatTime(action.timestamp),
        isAmplifier: amplifierLookup.value.has(lookupKey),
        timestamp: safeDate(action.timestamp)?.getTime() || 0,
      }
    })
    .sort((a, b) => b.timestamp - a.timestamp)
    .slice(0, 36)
})

const emotionDistribution = computed(() => {
  const counts = Object.fromEntries(emotionBuckets.map((bucket) => [bucket, 0]))
  const seenAgents = new Set()

  for (const item of feedItems.value) {
    if (seenAgents.has(item.lookupKey)) {
      continue
    }
    seenAgents.add(item.lookupKey)
    counts[item.emotion] = (counts[item.emotion] || 0) + 1
  }

  const maxCount = Math.max(1, ...Object.values(counts))
  return emotionBuckets.map((label) => ({
    label,
    count: counts[label],
    percent: (counts[label] / maxCount) * 100,
    tone: emotionToneClass(label),
  }))
})

onMounted(async () => {
  try {
    await loadBaseData()
    await refreshLiveData({ includeProfiles: true })
    await maybeAutoStart()
    startPolling()
  } finally {
    isLoading.value = false
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.ops-run-dashboard {
  min-height: 100vh;
  background:
    radial-gradient(circle at top right, rgba(10, 78, 122, 0.08), transparent 30%),
    linear-gradient(180deg, #f7f5ee 0%, #ffffff 48%, #fbfaf6 100%);
  color: #101010;
  font-family: 'Space Grotesk', 'Noto Sans', system-ui, sans-serif;
}

.dashboard-header {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 20px 32px;
  backdrop-filter: blur(18px);
  background: rgba(247, 245, 238, 0.9);
  border-bottom: 1px solid rgba(16, 16, 16, 0.08);
}

.brand-lockup,
.header-actions,
.feed-topline,
.feed-name-row,
.feed-badges,
.hero-chips,
.platform-strip,
.feed-meta,
.feed-footer {
  display: flex;
  flex-wrap: wrap;
}

.brand-lockup {
  align-items: center;
  gap: 14px;
}

.back-link {
  border: none;
  background: transparent;
  color: #4f4b40;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
}

.brand-mark {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  background: #111;
  color: #fff;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.brand-name {
  font-size: 16px;
  font-weight: 700;
}

.brand-tagline,
.status-item-label,
.stat-label,
.copy-label,
.panel-caption,
.error-title,
.hero-kicker,
.panel-kicker,
.status-label,
.platform-title {
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.brand-tagline,
.status-label,
.status-item-label,
.error-copy,
.stat-note,
.panel-caption,
.copy-label,
.feed-meta,
.feed-footer,
.platform-detail {
  color: #6b675b;
}

.ghost-btn,
.primary-btn {
  border-radius: 999px;
  padding: 10px 18px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.ghost-btn {
  border: 1px solid rgba(16, 16, 16, 0.1);
  background: rgba(255, 255, 255, 0.84);
}

.primary-btn {
  border: 1px solid #111;
  background: #111;
  color: #fff;
}

.ghost-btn:disabled,
.primary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dashboard-shell {
  width: min(1400px, calc(100vw - 40px));
  margin: 0 auto;
  padding: 30px 0 44px;
}

.hero-panel,
.dashboard-grid,
.stat-grid,
.feed-copy,
.status-grid {
  display: grid;
  gap: 18px;
}

.hero-panel {
  grid-template-columns: minmax(0, 1.1fr) minmax(320px, 440px);
  gap: 24px;
}

.hero-copy,
.hero-status-card,
.stat-card,
.emotion-card,
.amplifier-card,
.feed-panel,
.error-banner {
  border: 1px solid rgba(16, 16, 16, 0.08);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 22px 40px rgba(17, 17, 17, 0.05);
}

.hero-copy,
.hero-status-card,
.stat-card,
.emotion-card,
.amplifier-card,
.feed-panel {
  padding: 24px;
}

.hero-copy h1,
.panel-heading h2,
.feed-name-row h3,
.status-value,
.stat-value {
  letter-spacing: -0.04em;
}

.hero-copy h1 {
  margin: 14px 0;
  font-size: clamp(2.2rem, 5vw, 4rem);
  line-height: 0.96;
}

.hero-copy p,
.copy-block p {
  line-height: 1.75;
}

.meta-chip,
.amp-badge,
.emotion-badge,
.platform-badge,
.share-badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 7px 11px;
  font-size: 11px;
  font-weight: 700;
}

.meta-chip {
  background: #f0ead6;
  color: #3e3a2d;
}

.meta-chip.subtle,
.share-badge {
  background: #eef2f7;
  color: #46566a;
}

.hero-status-card,
.emotion-card,
.amplifier-card {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.status-row,
.panel-heading,
.amplifier-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.status-value {
  margin-top: 6px;
  font-size: 28px;
  font-weight: 800;
}

.status-value.live { color: #154c68; }
.status-value.success { color: #1b6e4b; }
.status-value.stopped { color: #7a5a20; }
.status-value.error { color: #a42a2a; }

.status-percent,
.amplifier-score {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
}

.status-percent {
  font-size: 24px;
}

.progress-track,
.emotion-track {
  overflow: hidden;
  border-radius: 999px;
  background: #ebe6d9;
}

.progress-track,
.emotion-track {
  height: 14px;
}

.progress-fill,
.emotion-fill {
  height: 100%;
  border-radius: inherit;
  transition: width 0.4s ease;
}

.progress-fill {
  background: linear-gradient(90deg, #0f5a89 0%, #3fa7a0 100%);
}

.status-grid,
.stat-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.status-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.status-item,
.amplifier-row,
.copy-block,
.feed-card {
  border-radius: 18px;
  background: #faf7ef;
}

.status-item,
.amplifier-row,
.copy-block {
  padding: 14px 16px;
}

.dashboard-grid {
  grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
  margin-top: 24px;
}

.stat-grid,
.feed-panel {
  margin-top: 24px;
}

.stat-value {
  margin-top: 14px;
  font-size: clamp(2rem, 3vw, 3rem);
  line-height: 0.95;
  font-weight: 800;
}

.stat-card.accent {
  background: linear-gradient(135deg, rgba(17, 17, 17, 0.94), rgba(15, 90, 137, 0.92));
  color: #fff;
}

.stat-card.accent .stat-label,
.stat-card.accent .stat-note {
  color: rgba(255, 255, 255, 0.8);
}

.emotion-stack,
.amplifier-list,
.feed-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.emotion-head,
.feed-topline {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.emotion-fill.worried,
.emotion-badge.worried { background: rgba(225, 166, 59, 0.15); color: #93650a; }
.emotion-fill.worried { background: linear-gradient(90deg, #e1a63b, #f3d27e); }
.emotion-fill.angry,
.emotion-badge.angry { background: rgba(183, 50, 57, 0.14); color: #8c1c24; }
.emotion-fill.angry { background: linear-gradient(90deg, #b73239, #df6671); }
.emotion-fill.resigned,
.emotion-badge.resigned { background: rgba(136, 123, 106, 0.18); color: #625446; }
.emotion-fill.resigned { background: linear-gradient(90deg, #887b6a, #bcae98); }
.emotion-fill.calm,
.emotion-badge.calm { background: rgba(31, 111, 93, 0.14); color: #175546; }
.emotion-fill.calm { background: linear-gradient(90deg, #1f6f5d, #58b6a2); }
.emotion-fill.other,
.emotion-badge.other { background: rgba(71, 95, 122, 0.12); color: #364a60; }
.emotion-fill.other { background: linear-gradient(90deg, #475f7a, #90a6bf); }

.feed-card {
  padding: 22px;
  border: 1px solid rgba(16, 16, 16, 0.08);
}

.feed-card.amplifier {
  background: linear-gradient(135deg, rgba(15, 90, 137, 0.08), rgba(255, 255, 255, 0.96));
  border-color: rgba(15, 90, 137, 0.22);
}

.feed-copy {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 18px;
}

.copy-block {
  background: #fff;
  border: 1px solid rgba(16, 16, 16, 0.06);
}

.copy-block.translation { background: #f5f7fb; }
.platform-badge { background: #f0eadc; color: #584b35; }
.amp-badge { background: #d9edf7; color: #0f5a89; }

.feed-empty,
.empty-panel {
  border-radius: 20px;
  border: 1px dashed rgba(16, 16, 16, 0.12);
  padding: 24px;
  background: #fcfbf7;
}

@media (max-width: 1080px) {
  .hero-panel,
  .dashboard-grid,
  .stat-grid,
  .feed-copy {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    padding: 18px 12px;
  }

  .dashboard-shell {
    width: calc(100vw - 24px);
  }

  .hero-copy,
  .hero-status-card,
  .stat-card,
  .emotion-card,
  .amplifier-card,
  .feed-panel {
    border-radius: 22px;
    padding: 18px;
  }
}
</style>
