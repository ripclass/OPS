<template>
  <div class="ops-results-page">
    <OpsProductHeader
      active-view="results"
      :simulation-id="simulationId"
      :report-id="currentReportId"
      section-label="OPS Flow · Results"
    >
      <template #actions>
        <div class="header-actions">
          <button type="button" class="ghost-btn" @click="goToRunView">
            Back to live dashboard
          </button>
          <button type="button" class="ghost-btn" @click="goToExpertView">
            Expert view
          </button>
          <button type="button" class="ghost-btn" :disabled="isRefreshing" @click="refreshResults">
            {{ isRefreshing ? 'Refreshing...' : 'Refresh results' }}
          </button>
          <button type="button" class="ghost-btn" :disabled="!reportReady" @click="downloadPdfReport">
            Download PDF report
          </button>
          <button type="button" class="ghost-btn" :disabled="!feedItems.length" @click="downloadCsv">
            Download CSV
          </button>
          <button
            type="button"
            class="primary-btn"
            :disabled="!calendlyUrl"
            @click="openDebrief"
          >
            Request debrief call
          </button>
        </div>
      </template>
    </OpsProductHeader>

    <main class="results-shell">
      <section class="hero-panel">
        <div class="hero-copy">
          <div class="hero-kicker">OPS Flow · Results</div>
          <h1>{{ reportOutlineTitle }}</h1>
          <p>{{ scenarioSummary }}</p>
          <div class="hero-chips">
            <span v-if="wizardMetadata.useCase" class="meta-chip">{{ wizardMetadata.useCase }}</span>
            <span v-if="wizardMetadata.runType" class="meta-chip">{{ wizardMetadata.runType }}</span>
            <span v-if="geographyLabel" class="meta-chip">{{ geographyLabel }}</span>
            <span v-if="wizardMetadata.segments" class="meta-chip">{{ wizardMetadata.segments }}</span>
            <span v-if="reportReady" class="meta-chip subtle">Completed {{ completedAtLabel }}</span>
            <span v-else class="meta-chip subtle">Generating report...</span>
          </div>
        </div>

        <div class="hero-status-card">
          <div class="status-row">
            <div>
              <div class="status-label">Report status</div>
              <div class="status-value" :class="reportStatusTone">{{ reportStatusLabel }}</div>
            </div>
            <div class="status-meta">{{ reportPhaseLabel }}</div>
          </div>

          <div class="progress-track">
            <div class="progress-fill" :style="{ width: `${reportProgressPercent}%` }"></div>
          </div>

          <div class="status-grid">
            <div class="status-item">
              <span class="status-item-label">Report ID</span>
              <span class="status-item-value">{{ currentReportId }}</span>
            </div>
            <div class="status-item">
              <span class="status-item-label">Simulation</span>
              <span class="status-item-value">{{ simulationId || 'Loading...' }}</span>
            </div>
            <div class="status-item">
              <span class="status-item-label">Sections</span>
              <span class="status-item-value">{{ sectionCountLabel }}</span>
            </div>
            <div class="status-item">
              <span class="status-item-label">Last sync</span>
              <span class="status-item-value">{{ lastRefreshLabel }}</span>
            </div>
          </div>

          <div v-if="!calendlyUrl" class="status-note">
            Set <code>VITE_CALENDLY_URL</code> to enable debrief booking from the results screen.
          </div>
        </div>
      </section>

      <section class="results-layout">
        <div class="results-main">
          <section v-if="errorMessage" class="error-banner">
            <div class="error-title">Results warning</div>
            <div class="error-copy">{{ errorMessage }}</div>
          </section>

          <section class="summary-card">
            <div class="panel-heading">
              <div>
                <div class="panel-kicker">Analyst summary</div>
                <h2>What the run says</h2>
              </div>
              <span class="panel-caption">Rendered from the report outline and markdown output</span>
            </div>

            <div v-if="reportReady" class="summary-body">
              <p class="summary-lead">{{ reportSummary }}</p>

              <div v-if="reportOutlineSections.length" class="outline-list">
                <div v-for="(section, index) in reportOutlineSections" :key="section.title || index" class="outline-item">
                  <div class="outline-index">{{ String(index + 1).padStart(2, '0') }}</div>
                  <div>
                    <div class="outline-title">{{ section.title }}</div>
                    <div class="outline-desc">{{ section.description || 'Section generated in the final report.' }}</div>
                  </div>
                </div>
              </div>

              <div v-if="reportPreviewHtml" class="markdown-preview" v-html="reportPreviewHtml"></div>
            </div>

            <div v-else class="loading-panel">
              <div class="loading-dot"></div>
              <span>The report agent is still assembling the final narrative. This page will refresh automatically.</span>
            </div>
          </section>

          <section class="feed-panel printable-report">
            <div class="panel-heading">
              <div>
                <div class="panel-kicker">Top reactions</div>
                <h2>Top 10 agent posts</h2>
              </div>
              <span class="panel-caption">Bangla text with English interpretation underneath</span>
            </div>

            <div v-if="!topPosts.length" class="feed-empty">
              Top posts will appear after the report and action streams become available.
            </div>

            <div v-else class="feed-list">
              <article v-for="item in topPosts" :key="item.id" class="feed-card" :class="{ amplifier: item.isAmplifier }">
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
        </div>

        <aside class="results-rail">
          <section class="continuity-strip">
            <article class="continuity-card">
              <span class="continuity-label">Use case</span>
              <span class="continuity-value">{{ wizardMetadata.useCase || 'Scenario run' }}</span>
            </article>
            <article class="continuity-card">
              <span class="continuity-label">Geography</span>
              <span class="continuity-value">{{ populationLabel }}</span>
            </article>
            <article class="continuity-card">
              <span class="continuity-label">Outputs</span>
              <span class="continuity-value">{{ requestedOutputsLabel }}</span>
            </article>
            <article class="continuity-card">
              <span class="continuity-label">Flow stage</span>
              <span class="continuity-value">{{ resultsStageLabel }}</span>
            </article>
          </section>

          <section class="stat-grid">
            <article class="stat-card">
              <div class="stat-label">Total agents</div>
              <div class="stat-value">{{ formatNumber(totalAgents) }}</div>
              <div class="stat-note">Profiles available for this completed run</div>
            </article>
            <article class="stat-card">
              <div class="stat-label">Sharing rate</div>
              <div class="stat-value">{{ sharingRateLabel }}</div>
              <div class="stat-note">Share-active agents divided by total responding agents</div>
            </article>
            <article class="stat-card accent">
              <div class="stat-label">Total cascade reach</div>
              <div class="stat-value">{{ formatNumber(totalReachEstimate) }}</div>
              <div class="stat-note">Estimated downstream reach from visible public activity</div>
            </article>
            <article class="stat-card">
              <div class="stat-label">Dominant emotion</div>
              <div class="stat-value">{{ dominantEmotion }}</div>
              <div class="stat-note">Most common derived emotional tone in public posts</div>
            </article>
            <article class="stat-card">
              <div class="stat-label">Top amplifiers</div>
              <div class="stat-value">{{ topAmplifierNames }}</div>
              <div class="stat-note">Highest weighted nodes by reach and share behavior</div>
            </article>
            <article class="stat-card">
              <div class="stat-label">Silent majority</div>
              <div class="stat-value">{{ formatNumber(silentMajorityCount) }}</div>
              <div class="stat-note">Profiles with no visible public action in the captured run data</div>
            </article>
          </section>

          <section class="heatmap-card">
            <div class="panel-heading">
              <div>
                <div class="panel-kicker">Regional signal</div>
                <h2>District heat map placeholder</h2>
              </div>
              <span class="panel-caption">Bangladesh placeholder until district-level metadata is explicit in the backend</span>
            </div>

            <div class="heatmap-shell">
              <div class="map-shape">
                <div
                  v-for="district in districtHeatmap"
                  :key="district.name"
                  class="district-node"
                  :class="district.tone"
                >
                  <span class="district-name">{{ district.name }}</span>
                  <span class="district-value">{{ district.count }}</span>
                </div>
              </div>

              <div class="heatmap-legend">
                <div v-for="district in districtHeatmap" :key="`${district.name}-legend`" class="legend-row">
                  <span>{{ district.name }}</span>
                  <div class="legend-bar">
                    <div class="legend-fill" :style="{ width: `${district.percent}%` }"></div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </aside>
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
  getRunStatusDetail,
  getSimulation,
  getSimulationProfiles,
} from '../api/simulation'
import {
  getReport,
  getReportProgress,
  getReportSections,
} from '../api/report'
import OpsProductHeader from '../components/OpsProductHeader.vue'

const props = defineProps({
  reportId: String,
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
const bangladeshRegions = [
  { name: 'Dhaka', patterns: [/dhaka/i] },
  { name: 'Chattogram', patterns: [/chattogram/i, /chittagong/i] },
  { name: 'Sylhet', patterns: [/sylhet/i, /sylheti/i] },
  { name: 'Khulna', patterns: [/khulna/i] },
  { name: 'Rajshahi', patterns: [/rajshahi/i] },
  { name: 'Barishal', patterns: [/barishal/i, /barisal/i] },
  { name: 'Rangpur', patterns: [/rangpur/i] },
  { name: 'Mymensingh', patterns: [/mymensingh/i] },
]

const currentReportId = computed(() => props.reportId || route.params.reportId)
const calendlyUrl = (import.meta.env.VITE_CALENDLY_URL || '').trim()

const reportData = ref(null)
const reportProgress = ref(null)
const reportSections = ref([])
const simulationData = ref(null)
const projectData = ref(null)
const rawActions = ref([])
const profileIndex = ref({})
const agentStatsIndex = ref({})
const simulationId = ref('')

const isLoading = ref(true)
const isRefreshing = ref(false)
const errorMessage = ref('')
const lastRefreshAt = ref(null)

let pollTimer = null

function parseWizardMetadata(text) {
  const source = String(text || '')
  const match = source.match(/\[OPS Wizard Metadata\]([\s\S]*?)\[\/OPS Wizard Metadata\]/)
  if (!match) return {}

  const metadata = {}
  const lines = match[1]
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)

  for (const line of lines) {
    const separator = line.indexOf(':')
    if (separator === -1) continue
    const label = line.slice(0, separator).trim().toLowerCase()
    const value = line.slice(separator + 1).trim()
    if (!value) continue
    if (label === 'use case') metadata.useCase = value
    if (label === 'country' || label === 'origin country') metadata.originCountry = value
    if (label === 'origin countries') metadata.originCountries = value
    if (label === 'run type') metadata.runType = value
    if (label === 'audience region') metadata.audienceRegion = value
    if (label === 'corridor') metadata.corridor = value
    if (label === 'segments') metadata.segments = value
    if (label === 'target agents') metadata.targetAgents = value
    if (label === 'requested outputs') metadata.outputs = value
  }

  return metadata
}

function extractScenarioText(text) {
  const source = String(text || '').trim()
  if (!source) {
    return 'The OPS report is being assembled. Scenario details will appear here once project metadata is available.'
  }

  const scenarioMatch = source.match(/Scenario:\s*([\s\S]*)$/)
  const body = scenarioMatch
    ? scenarioMatch[1].trim()
    : source.replace(/\[OPS Wizard Metadata\][\s\S]*?\[\/OPS Wizard Metadata\]/g, '').trim()

  if (!body) {
    return 'The OPS report is being assembled. Scenario details will appear here once project metadata is available.'
  }

  return body.length > 280 ? `${body.slice(0, 277).trim()}...` : body
}

function toLookupKeys(value) {
  if (value === null || value === undefined) return []
  const normalized = String(value).trim()
  if (!normalized) return []
  const lowered = normalized.toLowerCase()
  return lowered === normalized ? [normalized] : [normalized, lowered]
}

function mergeProfiles(profiles) {
  const grouped = {}
  profiles.forEach((profile, index) => {
    const anchor =
      profile.user_id ??
      profile.agent_id ??
      profile.username ??
      profile.user_name ??
      profile.name

    const anchorKey = anchor === undefined || anchor === null ? null : String(anchor)
    const groupKey = anchorKey || `${profile.name || 'agent'}-${index}`
    grouped[groupKey] = {
      ...(grouped[groupKey] || {}),
      ...profile,
    }
  })

  const nextIndex = {}
  Object.values(grouped).forEach((merged) => {
    const keys = [
      ...toLookupKeys(merged.user_id),
      ...toLookupKeys(merged.agent_id),
      ...toLookupKeys(merged.username),
      ...toLookupKeys(merged.user_name),
      ...toLookupKeys(merged.name),
    ]
    keys.forEach((key) => {
      nextIndex[key] = merged
    })
  })

  profileIndex.value = nextIndex
}

function buildAgentStatsIndex(stats) {
  const nextIndex = {}
  ;(stats || []).forEach((item) => {
    ;[...toLookupKeys(item.agent_id), ...toLookupKeys(item.agent_name)].forEach((key) => {
      nextIndex[key] = item
    })
  })
  agentStatsIndex.value = nextIndex
}

function resolveProfile(action) {
  const candidates = [...toLookupKeys(action?.agent_id), ...toLookupKeys(action?.agent_name)]
  for (const key of candidates) {
    if (profileIndex.value[key]) return profileIndex.value[key]
  }
  return null
}

function resolveAgentStats(action) {
  const candidates = [...toLookupKeys(action?.agent_id), ...toLookupKeys(action?.agent_name)]
  for (const key of candidates) {
    if (agentStatsIndex.value[key]) return agentStatsIndex.value[key]
  }
  return null
}

function safeDate(value) {
  if (!value) return null
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

function formatTime(value) {
  const parsed = safeDate(value)
  if (!parsed) return '--'
  return parsed.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

function formatDateTime(value) {
  const parsed = safeDate(value)
  if (!parsed) return 'In progress'
  return parsed.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

function formatNumber(value) {
  const numeric = Number(value || 0)
  return new Intl.NumberFormat('en-US').format(Number.isFinite(numeric) ? numeric : 0)
}

function extractActionText(action) {
  const args = action?.action_args || {}
  return args.content || args.quote_content || args.original_content || args.post_content || args.comment_content || ''
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
  if (!source) return 'No public text was captured for this action.'

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

  themeMatchers.forEach(([pattern, label]) => {
    if (pattern.test(source)) themes.push(label)
  })

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

  if (influenceRadius > 0) return influenceRadius * shareMultiplier
  if (followerCount > 0) return Math.round(followerCount * 0.35 * shareMultiplier)
  if (friendCount > 0) return Math.round(friendCount * 0.6 * shareMultiplier)
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
  if (!action) return false
  if (publicActionTypes.has(action.action_type)) return true
  return Boolean(extractActionText(action))
}

function isShareLike(action) {
  return shareActionTypes.has(String(action?.action_type || '').toUpperCase())
}

function inferRegion(profile, itemText) {
  const corpus = [
    profile?.persona,
    profile?.bio,
    profile?.dialect,
    profile?.country,
    itemText,
  ]
    .filter(Boolean)
    .join(' ')

  for (const region of bangladeshRegions) {
    if (region.patterns.some((pattern) => pattern.test(corpus))) {
      return region.name
    }
  }
  return null
}

function renderMarkdown(content) {
  if (!content) return ''
  const processed = content
    .replace(/^# .+\n+/, '')
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre class="md-code"><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code class="md-inline">$1</code>')
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    .replace(/^\- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
    .replace(/\n\n/g, '</p><p>')

  return `<p>${processed}</p>`
    .replace(/<p><h/g, '<h')
    .replace(/<\/h([2-4])><\/p>/g, '</h$1>')
    .replace(/<p><ul>/g, '<ul>')
    .replace(/<\/ul><\/p>/g, '</ul>')
    .replace(/<\/li>\s*<li>/g, '</li><li>')
}

async function fetchProfiles() {
  if (!simulationId.value) return

  const responses = await Promise.allSettled([
    getSimulationProfiles(simulationId.value, 'reddit'),
    getSimulationProfiles(simulationId.value, 'twitter'),
  ])

  const profiles = []
  responses.forEach((response) => {
    if (response.status === 'fulfilled') {
      profiles.push(...(response.value.data?.profiles || []))
    }
  })
  mergeProfiles(profiles)
}

async function loadSimulationBundle() {
  if (!simulationId.value) return

  const [simulationResponse, detailResponse, statsResponse] = await Promise.allSettled([
    getSimulation(simulationId.value),
    getRunStatusDetail(simulationId.value),
    getAgentStats(simulationId.value),
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
  }

  if (detailResponse.status === 'fulfilled') {
    rawActions.value = detailResponse.value.data?.all_actions || []
  }

  if (statsResponse.status === 'fulfilled') {
    buildAgentStatsIndex(statsResponse.value.data?.stats || [])
  }

  await fetchProfiles()
}

async function refreshResults() {
  if (!currentReportId.value || isRefreshing.value) return
  isRefreshing.value = true
  errorMessage.value = ''

  try {
    const [reportResponse, progressResponse, sectionsResponse] = await Promise.allSettled([
      getReport(currentReportId.value),
      getReportProgress(currentReportId.value),
      getReportSections(currentReportId.value),
    ])

    if (reportResponse.status === 'fulfilled') {
      reportData.value = reportResponse.value.data
      simulationId.value = reportData.value?.simulation_id || simulationId.value
    } else if (!reportData.value) {
      errorMessage.value = 'The report is still being initialized. This page will keep polling automatically.'
    }

    if (progressResponse.status === 'fulfilled') {
      reportProgress.value = progressResponse.value.data
    }

    if (sectionsResponse.status === 'fulfilled') {
      reportSections.value = sectionsResponse.value.data?.sections || []
    }

    if (simulationId.value) {
      await loadSimulationBundle()
    }

    lastRefreshAt.value = new Date().toISOString()
    if (reportReady.value) {
      stopPolling()
    }
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isRefreshing.value = false
  }
}

function startPolling() {
  if (pollTimer) return
  pollTimer = setInterval(() => {
    refreshResults()
  }, 5000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function downloadPdfReport() {
  if (!reportReady.value) return
  window.print()
}

function downloadCsv() {
  if (!feedItems.value.length) return

  const headers = [
    'agent_name',
    'age',
    'location',
    'occupation',
    'emotion',
    'share_count',
    'estimated_reach',
    'platform',
    'round',
    'time',
    'bangla_post',
    'english_translation',
  ]

  const rows = feedItems.value.map((item) => [
    item.name,
    item.ageLabel,
    item.location,
    item.occupation,
    item.emotion,
    item.shareCount,
    item.estimatedReach,
    item.platformLabel,
    item.round,
    item.timeLabel,
    item.originalText,
    item.translation,
  ])

  const csv = [headers, ...rows]
    .map((row) =>
      row
        .map((value) => `"${String(value ?? '').replace(/"/g, '""')}"`)
        .join(',')
    )
    .join('\n')

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${currentReportId.value || 'ops-results'}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

function openDebrief() {
  if (!calendlyUrl) return
  window.open(calendlyUrl, '_blank', 'noopener,noreferrer')
}

function goToRunView() {
  if (simulationId.value) {
    router.push({ name: 'SimulationRun', params: { simulationId: simulationId.value } })
    return
  }
  router.push('/')
}

function goToExpertView() {
  if (currentReportId.value) {
    router.push({ name: 'Interaction', params: { reportId: currentReportId.value } })
    return
  }
  router.push('/')
}

const wizardMetadata = computed(() => parseWizardMetadata(projectData.value?.simulation_requirement || reportData.value?.simulation_requirement || ''))
const scenarioSummary = computed(() => extractScenarioText(projectData.value?.simulation_requirement || reportData.value?.simulation_requirement || ''))
const geographyLabel = computed(() => {
  if (wizardMetadata.value.corridor) {
    return wizardMetadata.value.corridor
  }
  if (wizardMetadata.value.audienceRegion && wizardMetadata.value.originCountry) {
    return `${wizardMetadata.value.originCountry} diaspora in ${wizardMetadata.value.audienceRegion}`
  }
  if (wizardMetadata.value.originCountries) {
    return wizardMetadata.value.originCountries
  }
  return wizardMetadata.value.originCountry || ''
})
const populationLabel = computed(() => {
  const country = geographyLabel.value || 'South Asia'
  const segments = wizardMetadata.value.segments || 'General population'
  return `${country} / ${segments}`
})
const requestedOutputsLabel = computed(() => wizardMetadata.value.outputs || 'PDF report, CSV export')

const reportReady = computed(() => String(reportData.value?.status || '').toLowerCase() === 'completed')
const reportStatusLabel = computed(() => {
  const raw = String(reportData.value?.status || reportProgress.value?.status || 'generating')
  return raw.charAt(0).toUpperCase() + raw.slice(1)
})

const reportStatusTone = computed(() => {
  if (reportReady.value) return 'success'
  if (String(reportData.value?.status || '').toLowerCase() === 'failed') return 'error'
  return 'live'
})

const reportProgressPercent = computed(() => {
  const explicit = Number(reportProgress.value?.progress)
  if (Number.isFinite(explicit)) {
    return Math.max(0, Math.min(100, explicit))
  }

  const totalSections = Number(reportData.value?.outline?.sections?.length || 0)
  const generatedSections = Number(reportSections.value.length || 0)
  if (reportReady.value) return 100
  if (totalSections > 0) return Math.max(15, Math.min(90, (generatedSections / totalSections) * 100))
  return 12
})

const reportPhaseLabel = computed(() => {
  if (reportReady.value) return 'Final report assembled'
  return reportProgress.value?.message || 'Report agent is synthesizing the run'
})
const resultsStageLabel = computed(() => (reportReady.value ? 'Completed insight report' : 'Generating insight report'))

const reportOutlineTitle = computed(() => reportData.value?.outline?.title || projectData.value?.name || 'OPS Simulation Results')
const reportSummary = computed(() => {
  if (reportData.value?.outline?.summary) return reportData.value.outline.summary
  const markdown = String(reportData.value?.markdown_content || '').trim()
  if (!markdown) return 'The report summary will appear here once generation is complete.'
  const lines = markdown.split(/\r?\n/).map((line) => line.trim()).filter(Boolean)
  const firstContentLine = lines.find((line) => !line.startsWith('#'))
  return firstContentLine || 'The report summary will appear here once generation is complete.'
})

const reportOutlineSections = computed(() => reportData.value?.outline?.sections || [])
const reportPreviewHtml = computed(() => {
  const markdown = String(reportData.value?.markdown_content || '').trim()
  if (!markdown) return ''
  return renderMarkdown(markdown.length > 2500 ? `${markdown.slice(0, 2500).trim()}...` : markdown)
})

const sectionCountLabel = computed(() => {
  const total = reportData.value?.outline?.sections?.length || reportSections.value.length || 0
  const current = reportSections.value.length || (reportReady.value ? total : 0)
  return total ? `${current}/${total}` : 'Pending'
})

const completedAtLabel = computed(() => formatDateTime(reportData.value?.completed_at))
const lastRefreshLabel = computed(() => (lastRefreshAt.value ? formatTime(lastRefreshAt.value) : 'Waiting...'))

const shareCountsByAgent = computed(() => {
  const counts = {}
  rawActions.value.forEach((action) => {
    const key = actionLookupKey(action)
    if (isShareLike(action)) counts[key] = (counts[key] || 0) + 1
  })
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
  const unique = new Set(rawActions.value.filter((action) => isShareLike(action)).map((action) => actionLookupKey(action)))
  return unique.size
})

const totalAgents = computed(() => {
  const uniqueProfiles = new Set(Object.values(profileIndex.value).map((profile) => profile.user_id ?? profile.name))
  if (uniqueProfiles.size) return uniqueProfiles.size
  return simulationData.value?.profiles_count || simulationData.value?.entities_count || 0
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
        timestamp: safeDate(action.timestamp)?.getTime() || 0,
      }
    })
    .sort((a, b) => {
      if (b.estimatedReach !== a.estimatedReach) return b.estimatedReach - a.estimatedReach
      return b.timestamp - a.timestamp
    })
})

const topAmplifiers = computed(() => {
  const agents = []
  const seen = new Set()

  rawActions.value.forEach((action) => {
    const lookupKey = actionLookupKey(action)
    if (seen.has(lookupKey)) return
    seen.add(lookupKey)

    const profile = resolveProfile(action)
    const stats = resolveAgentStats(action)
    const shareCount = shareCountsByAgent.value[lookupKey] || 0
    agents.push({
      lookupKey,
      name: profile?.name || action.agent_name || 'Unknown agent',
      profession: profile?.profession || 'Resident',
      location: profile?.country || 'South Asia',
      reach: estimateReach(profile, stats, shareCount),
      score: buildAmplifierScore(profile, stats, shareCount),
    })
  })

  return agents.sort((a, b) => b.score - a.score).slice(0, 5)
})

const amplifierLookup = computed(() => new Set(topAmplifiers.value.map((agent) => agent.lookupKey)))

const topPosts = computed(() =>
  feedItems.value.slice(0, 10).map((item) => ({
    ...item,
    isAmplifier: amplifierLookup.value.has(item.lookupKey),
  }))
)

const totalReachEstimate = computed(() => {
  let total = 0
  const seen = new Set()
  rawActions.value.forEach((action) => {
    const lookupKey = actionLookupKey(action)
    if (seen.has(lookupKey)) return
    seen.add(lookupKey)
    const profile = resolveProfile(action)
    const stats = resolveAgentStats(action)
    total += estimateReach(profile, stats, shareCountsByAgent.value[lookupKey] || 0)
  })
  return total
})
const sharingRateLabel = computed(() => {
  if (!respondedAgentsCount.value) return '0%'
  return `${Math.round((sharingAgentsCount.value / respondedAgentsCount.value) * 100)}%`
})

const emotionDistribution = computed(() => {
  const counts = Object.fromEntries(emotionBuckets.map((bucket) => [bucket, 0]))
  const seen = new Set()
  feedItems.value.forEach((item) => {
    if (seen.has(item.lookupKey)) return
    seen.add(item.lookupKey)
    counts[item.emotion] = (counts[item.emotion] || 0) + 1
  })
  return counts
})

const dominantEmotion = computed(() => {
  const entries = Object.entries(emotionDistribution.value).sort((a, b) => b[1] - a[1])
  return entries[0]?.[1] ? entries[0][0] : 'Pending'
})

const topAmplifierNames = computed(() => {
  if (!topAmplifiers.value.length) return 'Pending'
  return topAmplifiers.value.slice(0, 3).map((item) => item.name).join(', ')
})

const silentMajorityCount = computed(() => Math.max(0, totalAgents.value - respondedAgentsCount.value))

const districtHeatmap = computed(() => {
  const counts = Object.fromEntries(bangladeshRegions.map((region) => [region.name, 0]))
  topPosts.value.forEach((item) => {
    const profile = Object.values(profileIndex.value).find((candidate) => candidate.name === item.name)
    const region = inferRegion(profile, item.originalText)
    if (region) counts[region] += 1
  })
  const maxCount = Math.max(1, ...Object.values(counts))

  return bangladeshRegions.map((region, index) => {
    const count = counts[region.name]
    const percent = (count / maxCount) * 100
    const tone = percent > 70 ? 'hot' : percent > 35 ? 'warm' : percent > 0 ? 'cool' : 'cold'
    return {
      name: region.name,
      count,
      percent,
      tone,
      order: index,
    }
  })
})

onMounted(async () => {
  try {
    await refreshResults()
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
.ops-results-page {
  min-height: 100vh;
  color: var(--ops-ink);
  font-family: var(--ops-font-display);
}

.brand-lockup,
.header-actions,
.hero-chips,
.feed-meta,
.feed-footer,
.feed-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
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
.status-label,
.status-item-label,
.stat-label,
.panel-caption,
.copy-label,
.hero-kicker,
.panel-kicker,
.error-title {
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.brand-tagline,
.status-label,
.status-item-label,
.panel-caption,
.copy-label,
.error-copy,
.stat-note,
.status-note,
.feed-meta,
.feed-footer {
  color: #6b675b;
}

.ghost-btn,
.primary-btn {
  border-radius: 999px;
  padding: 10px 18px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}

.ghost-btn {
  border: 1px solid var(--ops-border-strong);
  background: rgba(255, 255, 255, 0.88);
  color: var(--ops-ink-soft);
}

.primary-btn {
  border: 1px solid var(--ops-accent);
  background: var(--ops-accent);
  color: #fff;
}

.ghost-btn:disabled,
.primary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.results-shell {
  width: min(1400px, calc(100vw - 40px));
  margin: 0 auto;
  padding: 30px 0 44px;
}

.hero-panel,
.results-layout,
.stat-grid,
.results-grid,
.feed-copy,
.status-grid,
.heatmap-shell {
  display: grid;
  gap: 18px;
}

.hero-panel {
  grid-template-columns: minmax(0, 1.1fr) minmax(320px, 440px);
  gap: 24px;
}

.results-layout {
  grid-template-columns: minmax(0, 1.1fr) minmax(320px, 420px);
  margin-top: 24px;
  align-items: start;
}

.results-main,
.results-rail {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-copy,
.hero-status-card,
.stat-card,
.summary-card,
.heatmap-card,
.feed-panel,
.error-banner {
  border: 1px solid var(--ops-border);
  border-radius: 28px;
  background: var(--ops-surface);
  box-shadow: var(--ops-shadow);
}

.hero-copy,
.hero-status-card,
.stat-card,
.summary-card,
.heatmap-card,
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
.summary-lead,
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
  background: rgba(17, 24, 39, 0.05);
  color: var(--ops-ink-soft);
}

.hero-status-card,
.summary-card,
.heatmap-card {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.status-row,
.panel-heading,
.outline-item,
.feed-topline {
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

.status-value.live { color: var(--ops-accent); }
.status-value.success { color: var(--ops-success); }
.status-value.error { color: var(--ops-error); }

.status-meta {
  max-width: 180px;
  text-align: right;
  font-size: 13px;
  color: #4a5560;
  line-height: 1.5;
}

.progress-track,
.legend-bar {
  overflow: hidden;
  border-radius: 999px;
  background: #ebe6d9;
}

.progress-track {
  height: 14px;
}

.progress-fill,
.legend-fill {
  height: 100%;
  border-radius: inherit;
}

.progress-fill {
  background: linear-gradient(90deg, var(--ops-accent) 0%, #f0833a 100%);
}

.status-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.status-item,
.outline-item,
.feed-card,
.copy-block,
.district-node {
  border-radius: 18px;
}

.status-item,
.outline-item {
  padding: 14px 16px;
  background: #faf7ef;
}

.status-note code {
  font-family: 'JetBrains Mono', monospace;
}

.continuity-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.continuity-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px;
  border-radius: 20px;
  border: 1px solid var(--ops-border);
  background: rgba(255, 255, 255, 0.84);
  box-shadow: var(--ops-shadow-tight);
}

.continuity-label {
  font-family: var(--ops-font-mono);
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: var(--ops-muted);
}

.continuity-value {
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.5;
}

.stat-value {
  margin-top: 14px;
  font-size: clamp(2rem, 3vw, 3rem);
  line-height: 0.95;
  font-weight: 800;
}

.stat-card.accent {
  background: linear-gradient(135deg, rgba(17, 24, 39, 0.96), rgba(201, 75, 34, 0.92));
  color: #fff;
}

.stat-card.accent .stat-label,
.stat-card.accent .stat-note {
  color: rgba(255, 255, 255, 0.8);
}

.outline-list,
.feed-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.outline-index {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: #111;
  color: #fff;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
}

.outline-title {
  font-size: 15px;
  font-weight: 700;
}

.outline-desc {
  margin-top: 6px;
  color: #686255;
  font-size: 13px;
  line-height: 1.6;
}

.markdown-preview {
  margin-top: 18px;
  padding: 20px;
  border-radius: 20px;
  background: #fcfbf7;
  border: 1px solid rgba(16, 16, 16, 0.06);
}

.markdown-preview :deep(h2),
.markdown-preview :deep(h3),
.markdown-preview :deep(h4) {
  margin: 18px 0 8px;
}

.markdown-preview :deep(p),
.markdown-preview :deep(li),
.markdown-preview :deep(blockquote) {
  font-size: 14px;
  line-height: 1.75;
  color: #333;
}

.loading-panel,
.feed-empty {
  border-radius: 20px;
  border: 1px dashed rgba(16, 16, 16, 0.12);
  padding: 24px;
  background: #fcfbf7;
  color: #696458;
  line-height: 1.7;
}

.loading-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #0f5a89;
  margin-bottom: 12px;
  animation: pulse 1.1s infinite ease-in-out;
}

.heatmap-shell {
  grid-template-columns: minmax(0, 1fr);
}

.map-shape {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.district-node {
  padding: 14px;
  min-height: 82px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border: 1px solid rgba(16, 16, 16, 0.08);
}

.district-node.hot { background: rgba(183, 50, 57, 0.14); }
.district-node.warm { background: rgba(225, 166, 59, 0.16); }
.district-node.cool { background: rgba(15, 90, 137, 0.12); }
.district-node.cold { background: rgba(71, 95, 122, 0.07); }

.district-name {
  font-size: 13px;
  font-weight: 700;
}

.district-value {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.04em;
}

.legend-row {
  display: grid;
  grid-template-columns: 110px minmax(0, 1fr);
  gap: 10px;
  align-items: center;
}

.legend-bar {
  height: 10px;
}

.legend-fill {
  background: linear-gradient(90deg, var(--ops-accent) 0%, #f0833a 100%);
}

.feed-card {
  padding: 22px;
  background: #fbfaf6;
  border: 1px solid rgba(16, 16, 16, 0.08);
}

.feed-card.amplifier {
  background: linear-gradient(135deg, rgba(201, 75, 34, 0.08), rgba(255, 255, 255, 0.96));
  border-color: rgba(201, 75, 34, 0.22);
}

.feed-name-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.feed-name-row h3 {
  margin: 0;
  font-size: 22px;
}

.feed-meta span:not(:last-child)::after {
  content: '·';
  margin-left: 10px;
}

.emotion-badge.worried { background: rgba(225, 166, 59, 0.15); color: #93650a; }
.emotion-badge.angry { background: rgba(183, 50, 57, 0.14); color: #8c1c24; }
.emotion-badge.resigned { background: rgba(136, 123, 106, 0.18); color: #625446; }
.emotion-badge.calm { background: rgba(31, 111, 93, 0.14); color: #175546; }
.emotion-badge.other { background: rgba(71, 95, 122, 0.12); color: #364a60; }

.platform-badge { background: #f0eadc; color: #584b35; }
.amp-badge { background: var(--ops-accent-soft); color: var(--ops-accent); }

.feed-copy {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 18px;
}

.copy-block {
  padding: 18px;
  background: #fff;
  border: 1px solid rgba(16, 16, 16, 0.06);
}

.copy-block.translation {
  background: #f5f7fb;
}

.error-banner {
  padding: 18px 22px;
  border-color: rgba(164, 42, 42, 0.16);
  background: rgba(164, 42, 42, 0.05);
}

.results-main .summary-card,
.results-main .feed-panel,
.results-main .error-banner,
.results-rail .continuity-strip,
.results-rail .stat-grid,
.results-rail .heatmap-card {
  margin-top: 0;
}

.results-rail .continuity-strip,
.results-rail .stat-grid {
  grid-template-columns: 1fr;
}

@keyframes pulse {
  50% { opacity: 0.45; }
}

@media (max-width: 1080px) {
  .hero-panel,
  .results-layout,
  .continuity-strip,
  .stat-grid,
  .results-grid,
  .feed-copy {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .results-header {
    flex-direction: column;
    align-items: flex-start;
    padding: 18px 12px;
  }

  .results-shell {
    width: calc(100vw - 24px);
  }

  .hero-copy,
  .hero-status-card,
  .stat-card,
  .summary-card,
  .heatmap-card,
  .feed-panel {
    border-radius: 22px;
    padding: 18px;
  }
}

@media print {
  :deep(.ops-product-header),
  .error-banner,
  .feed-empty {
    display: none !important;
  }

  .ops-results-page {
    background: #fff;
  }

  .results-shell {
    width: 100%;
    padding: 0;
  }
}
</style>
