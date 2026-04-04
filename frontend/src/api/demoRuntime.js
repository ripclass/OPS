import { DEMO_DEFAULT_PACK_KEY, DEMO_PACKS, getDemoPack, resolveDemoPackKey } from '../content/demoFlowPacks'
import { demoState } from '../store/demoFlow'

const RUNTIME_STORAGE_KEY = 'murmur_demo_runtime_v2'
const REPORT_TIMELINE_DURATION_MS = 9000
const SIMULATION_DURATION_MS = 12000
const PREPARE_DURATION_MS = 7000
const DEMO_MIN_AGENT_COUNT = 100

function getStorage() {
  if (typeof window === 'undefined') {
    return null
  }
  return window.sessionStorage
}

function loadRuntime() {
  const storage = getStorage()
  if (!storage) {
    return {}
  }

  const raw = storage.getItem(RUNTIME_STORAGE_KEY)
  if (!raw) {
    return {}
  }

  try {
    return JSON.parse(raw)
  } catch {
    storage.removeItem(RUNTIME_STORAGE_KEY)
    return {}
  }
}

function saveRuntime(runtime) {
  const storage = getStorage()
  if (!storage) {
    return
  }

  storage.setItem(RUNTIME_STORAGE_KEY, JSON.stringify(runtime))
}

function withRuntime(packKey, updater) {
  const runtime = loadRuntime()
  const nextPackState = updater({
    prepareTaskId: null,
    prepareStartedAt: null,
    preparedAt: null,
    simulationStartedAt: null,
    simulationStoppedAt: null,
    reportGeneratedAt: null,
    ...runtime[packKey],
  })

  runtime[packKey] = nextPackState
  saveRuntime(runtime)
  return nextPackState
}

function getPackKeyFromIdentifier(value) {
  const match = String(value || '').match(/^demo_([^_]+)_(project|graph|sim|report|prepare)$/)
  return match?.[1] || null
}

function getCurrentPackKey() {
  return resolveDemoPackKey(demoState.countryCode || 'BD')
}

function getPackForIdentifier(value) {
  const key = getPackKeyFromIdentifier(value) || getCurrentPackKey() || DEMO_DEFAULT_PACK_KEY
  return getDemoPack(key)
}

function getIdsForPack(pack) {
  return {
    projectId: `demo_${pack.key}_project`,
    graphId: `demo_${pack.key}_graph`,
    simulationId: pack.population.simulationId || `demo_${pack.key}_sim`,
    reportId: `demo_${pack.key}_report`,
    prepareTaskId: `demo_${pack.key}_prepare`,
  }
}

function createTimestamp(baseDate, offsetMs) {
  return new Date(baseDate.getTime() + offsetMs).toISOString()
}

function createProjectData(pack) {
  const ids = getIdsForPack(pack)
  const scenario = demoState.scenario || pack.intake.defaultScenario

  return {
    project_id: ids.projectId,
    graph_id: ids.graphId,
    status: 'graph_completed',
    simulation_requirement: scenario,
    ontology: {
      entity_types: pack.graph.entityTypes.map(name => ({
        name,
        description: `${name} entities extracted from the ${pack.countryLabel} demo pack.`,
        attributes: [
          { name: 'region', type: 'string', description: pack.countryLabel },
          { name: 'salience', type: 'number', description: 'Relative scenario relevance' },
        ],
        examples: pack.population.personas.slice(0, 2).map(persona => persona.name),
      })),
      edge_types: pack.graph.relationTypes.map(name => ({
        name,
        description: `${name} relation inferred in the ${pack.countryLabel} scenario graph.`,
        source_targets: [
          { source: 'Government Notice', target: 'Household cluster' },
          { source: 'Student Pages', target: 'Rumor Chain' },
        ],
      })),
    },
  }
}

function buildTopicPool(pack) {
  const seedTopics = [
    'food prices',
    'household budgeting',
    'relief queues',
    'rumor chains',
    'student pages',
    'institutional trust',
    'market signals',
    'community pressure',
    'household silence',
    'remittance timing',
    'public complaint',
    'delayed relief',
    'queue photos',
    'price board updates',
    'local media framing',
    'neighborhood calls',
    'voice note circulation',
    'festival timing',
  ]

  const dynamicTopics = [
    ...pack.population.notes,
    ...pack.report.sections.map(section => section.title),
  ].map(value => String(value || '').trim()).filter(Boolean)

  return Array.from(new Set([...seedTopics, ...dynamicTopics]))
}

function createProfiles(pack) {
  const topicPool = buildTopicPool(pack)
  const anchors = pack.population.personas

  return Array.from({ length: DEMO_MIN_AGENT_COUNT }, (_, index) => {
    const anchor = anchors[index % anchors.length]
    const clusterIndex = Math.floor(index / anchors.length)
    const username = clusterIndex === 0
      ? anchor.name
      : `${anchor.name} ${String(clusterIndex + 1).padStart(2, '0')}`
    const handleBase = username.toLowerCase().replace(/[^a-z0-9]+/g, '_')
    const interested_topics = Array.from({ length: 4 }, (_unused, topicIndex) => {
      return topicPool[(index + topicIndex * 3) % topicPool.length]
    })

    return {
      id: index,
      agent_id: index,
      username,
      name: `${handleBase}_${String(index + 1).padStart(3, '0')}`,
      profession: anchor.role,
      bio: `${anchor.detail}. ${anchor.trait}. Cluster ${clusterIndex + 1} follows the ${pack.countryLabel} ${pack.key} shock pattern.`,
      interested_topics,
      entity_type: 'Person',
    }
  })
}

function createSimulationConfig(pack) {
  const profiles = createProfiles(pack)

  return {
    time_config: {
      total_simulation_hours: 20,
      minutes_per_round: 30,
      agents_per_hour_min: 8,
      agents_per_hour_max: 16,
      peak_hours: [7, 8, 19, 20],
      peak_activity_multiplier: 1.8,
      work_hours: [9, 10, 11, 12, 13, 14, 15, 16, 17],
      work_activity_multiplier: 1.2,
      morning_hours: [6, 7, 8],
      morning_activity_multiplier: 1.35,
      off_peak_hours: [1, 2, 3, 4],
      off_peak_activity_multiplier: 0.45,
    },
    agent_configs: profiles.map((profile, index) => ({
      agent_id: index,
      entity_name: profile.username,
      entity_type: profile.entity_type,
      bio: profile.bio,
      interested_topics: profile.interested_topics,
    })),
    twitter_config: {
      recency_weight: 0.33,
      popularity_weight: 0.22,
      relevance_weight: 0.45,
      viral_threshold: 0.62,
      echo_chamber_strength: 0.58,
    },
    reddit_config: {
      recency_weight: 0.28,
      popularity_weight: 0.31,
      relevance_weight: 0.41,
      viral_threshold: 0.55,
      echo_chamber_strength: 0.64,
    },
    generation_reasoning:
      'OPS selected anchor agents who absorb shocks privately, amplify them publicly, and mediate trust through local networks.|The configuration emphasizes household arithmetic, rumor relays, institutional delay, and public narrative escalation.',
    event_config: {
      narrative_direction: pack.report.summary,
      hot_topics: ['food prices', 'queues', 'trust', 'relief'],
      initial_posts: pack.simulation.actions.slice(0, 3).map((action, index) => ({
        id: index + 1,
        platform: action.platform === 'community' ? 'reddit' : 'twitter',
        content: action.text,
      })),
    },
  }
}

function createSimulationActions(pack) {
  const baseTime = new Date('2026-04-04T10:45:00.000+06:00')
  const profiles = createProfiles(pack)
  const plazaSeeds = pack.simulation.actions.filter(action => action.platform === 'plaza')
  const communitySeeds = pack.simulation.actions.filter(action => action.platform === 'community')
  const tails = [
    'Queue photos begin circulating before the official explanation lands.',
    'Neighbors compare prices by voice note and assume the worst first.',
    'Screenshots move faster than relief language.',
    'Quiet household arithmetic becomes public talk by the evening.',
    'People ask whether the next transfer will still be enough.',
    'Market boards make the shock visible before policy copy does.',
  ]

  const buildPlatformActions = (platform, totalCount, seeds, actionTypeCycle) => {
    return Array.from({ length: totalCount }, (_unused, index) => {
      const seed = seeds[index % seeds.length]
      const profile = profiles[(index * 7 + (platform === 'twitter' ? 3 : 11)) % profiles.length]
      const round_num = Math.min(40, Math.floor((index / totalCount) * 40) + 1)
      const tail = tails[index % tails.length]
      const content = `${seed.text} ${tail}`
      const action_type = actionTypeCycle[index % actionTypeCycle.length]
      const actionId = `${pack.key}_${platform}_action_${index + 1}`
      const actionArgs = {
        content,
        original_content: seed.text,
        original_author_name: seed.actor,
        post_author_name: seed.actor,
      }

      return {
        id: actionId,
        platform,
        agent_id: profile.agent_id,
        agent_name: profile.username,
        action_type,
        action_args: action_type === 'CREATE_POST'
          ? { content }
          : action_type === 'REPOST'
            ? {
                original_content: seed.text,
                original_author_name: seed.actor,
              }
            : action_type === 'QUOTE_POST'
              ? {
                  quote_content: content,
                  original_content: seed.text,
                  original_author_name: seed.actor,
                }
              : action_type === 'CREATE_COMMENT'
                ? {
                    content,
                    post_id: `${pack.key}_thread_${(index % 18) + 1}`,
                  }
                : action_type === 'LIKE_POST'
                  ? {
                      post_content: seed.text,
                      post_author_name: seed.actor,
                    }
                  : actionArgs,
        round_num,
        timestamp: createTimestamp(baseTime, (platform === 'twitter' ? index : index + pack.simulation.communityA.acts) * 2300),
      }
    })
  }

  const twitterActions = buildPlatformActions(
    'twitter',
    pack.simulation.communityA.acts,
    plazaSeeds,
    ['CREATE_POST', 'QUOTE_POST', 'REPOST', 'CREATE_POST', 'LIKE_POST']
  )

  const redditActions = buildPlatformActions(
    'reddit',
    pack.simulation.communityB.acts,
    communitySeeds,
    ['CREATE_POST', 'CREATE_COMMENT', 'CREATE_POST', 'LIKE_POST', 'CREATE_COMMENT']
  )

  return [...twitterActions, ...redditActions].sort((left, right) => {
    return new Date(left.timestamp).getTime() - new Date(right.timestamp).getTime()
  })
}

function createReportOutline(pack) {
  return {
    title: pack.report.title,
    summary: pack.report.summary,
    sections: pack.report.sections.map(section => ({
      title: section.title,
    })),
  }
}

function createReportSections(pack) {
  return pack.report.sections.map((section, index) => ({
    section_index: index + 1,
    title: section.title,
    content: section.paragraphs.join('\n\n'),
  }))
}

function createReportAgentLogs(pack) {
  const baseTime = new Date('2026-04-04T11:24:00.000+06:00')
  const outline = createReportOutline(pack)
  const logs = [
    {
      timestamp: createTimestamp(baseTime, 0),
      action: 'report_start',
      details: {
        simulation_id: getIdsForPack(pack).simulationId,
        simulation_requirement: demoState.scenario || pack.intake.defaultScenario,
      },
    },
    {
      timestamp: createTimestamp(baseTime, 900),
      action: 'planning_start',
      details: { message: 'Planning report outline...' },
    },
    {
      timestamp: createTimestamp(baseTime, 1900),
      action: 'planning_complete',
      details: {
        message: 'Outline ready.',
        outline,
      },
    },
  ]

  pack.report.workbench.forEach((item, index) => {
    logs.push({
      timestamp: createTimestamp(baseTime, 2600 + index * 800),
      action: 'tool_call',
      details: {
        tool_name: item.label,
        prompt: item.detail,
      },
    })
    logs.push({
      timestamp: createTimestamp(baseTime, 3000 + index * 800),
      action: 'tool_result',
      details: {
        tool_name: item.label,
        result: item.detail,
      },
    })
  })

  pack.report.sections.forEach((section, index) => {
    logs.push({
      timestamp: createTimestamp(baseTime, 6200 + index * 1200),
      action: 'section_start',
      section_index: index + 1,
      section_title: section.title,
      details: {
        message: `Generating ${section.title}...`,
      },
    })
    logs.push({
      timestamp: createTimestamp(baseTime, 6900 + index * 1200),
      action: 'section_complete',
      section_index: index + 1,
      section_title: section.title,
      details: {
        content: section.paragraphs.join('\n\n'),
      },
    })
  })

  logs.push({
    timestamp: createTimestamp(baseTime, 9800),
    action: 'report_complete',
    details: { message: 'Report complete.' },
  })

  return logs
}

function createConsoleLogs(pack) {
  const base = [
    'INFO: Planning report outline',
    'INFO: Resolving high-salience population memories',
    'INFO: Running quick search against active graph state',
    'INFO: Compiling report sections',
    'INFO: Static demo report package complete',
  ]

  return pack.report.workbench.map((item, index) => `INFO: ${item.label} - ${item.detail}`).concat(base)
}

function getVisibleCount(elapsedMs, durationMs, totalItems) {
  if (totalItems <= 0) {
    return 0
  }

  const progress = Math.max(0, Math.min(1, elapsedMs / durationMs))
  return Math.max(1, Math.ceil(progress * totalItems))
}

function getRuntimeState(pack) {
  const runtime = loadRuntime()
  return runtime[pack.key] || {}
}

function getPrepareElapsed(runtime) {
  if (!runtime.prepareStartedAt) {
    return 0
  }
  return Date.now() - runtime.prepareStartedAt
}

function ensureReportStarted(pack) {
  const runtime = getRuntimeState(pack)
  if (!runtime.reportGeneratedAt) {
    withRuntime(pack.key, current => ({
      ...current,
      reportGeneratedAt: Date.now() - REPORT_TIMELINE_DURATION_MS,
    }))
  }
}

export function isDemoRequest(value) {
  return String(value || '').startsWith('demo_')
}

export function getDemoProject(projectId) {
  const pack = getPackForIdentifier(projectId)
  return {
    success: true,
    data: createProjectData(pack),
  }
}

export function getDemoGraphData(graphId) {
  const pack = getPackForIdentifier(graphId)
  return {
    success: true,
    data: pack.graph.graphData,
  }
}

export function createDemoSimulation(projectId) {
  const pack = getPackForIdentifier(projectId)
  const ids = getIdsForPack(pack)
  return {
    success: true,
    data: {
      simulation_id: ids.simulationId,
      project_id: ids.projectId,
      graph_id: ids.graphId,
    },
  }
}

export function getDemoSimulation(simulationId) {
  const pack = getPackForIdentifier(simulationId)
  const ids = getIdsForPack(pack)
  const runtime = getRuntimeState(pack)

  let status = 'created'
  if (runtime.preparedAt) {
    status = 'ready'
  }
  if (runtime.simulationStartedAt) {
    status = runtime.simulationStoppedAt ? 'completed' : 'running'
  }

  return {
    success: true,
    data: {
      simulation_id: ids.simulationId,
      project_id: ids.projectId,
      status,
    },
  }
}

export function prepareDemoSimulation({ simulation_id }) {
  const pack = getPackForIdentifier(simulation_id)
  const ids = getIdsForPack(pack)
  const profiles = createProfiles(pack)

  withRuntime(pack.key, current => ({
    ...current,
    prepareTaskId: ids.prepareTaskId,
    prepareStartedAt: Date.now(),
    preparedAt: null,
  }))

  return {
    success: true,
    data: {
      task_id: ids.prepareTaskId,
      expected_entities_count: profiles.length,
      entity_types: [...new Set(profiles.map(profile => profile.entity_type))],
    },
  }
}

export function getDemoPrepareStatus({ task_id, simulation_id }) {
  const pack = getPackForIdentifier(task_id || simulation_id)
  const ids = getIdsForPack(pack)
  const runtime = getRuntimeState(pack)
  const elapsed = getPrepareElapsed(runtime)

  if (!runtime.prepareStartedAt) {
    return {
      success: true,
      data: {
        task_id: ids.prepareTaskId,
        already_prepared: Boolean(runtime.preparedAt),
        status: runtime.preparedAt ? 'ready' : 'pending',
        progress: runtime.preparedAt ? 100 : 0,
      },
    }
  }

  if (elapsed >= PREPARE_DURATION_MS) {
    withRuntime(pack.key, current => ({
      ...current,
      preparedAt: current.preparedAt || Date.now(),
    }))

    return {
      success: true,
      data: {
        task_id: ids.prepareTaskId,
        status: 'completed',
        already_prepared: true,
        progress: 100,
        progress_detail: {
          current_stage_name: 'Environment Ready',
          current_stage: 'ready',
          stage_index: 4,
          total_stages: 4,
          current_item: createProfiles(pack).length,
          total_items: createProfiles(pack).length,
          item_description: 'Static demo environment loaded.',
        },
      },
    }
  }

  if (elapsed >= PREPARE_DURATION_MS * 0.75) {
    return {
      success: true,
      data: {
        task_id: ids.prepareTaskId,
        status: 'running',
        progress: 86,
        progress_detail: {
          current_stage_name: 'Simulation Parameter Synthesis',
          current_stage: 'config',
          stage_index: 3,
          total_stages: 4,
          current_item: 1,
          total_items: 1,
          item_description: 'Generating time, platform, and event parameters.',
        },
      },
    }
  }

  return {
    success: true,
    data: {
      task_id: ids.prepareTaskId,
      status: 'running',
      progress: 48,
      progress_detail: {
        current_stage_name: 'Persona Generation',
        current_stage: 'profiles',
        stage_index: 2,
        total_stages: 4,
        current_item: Math.max(1, Math.floor(createProfiles(pack).length * 0.6)),
        total_items: createProfiles(pack).length,
        item_description: 'Assigning public personas and behavioral traits.',
      },
    },
  }
}

export function getDemoProfiles(simulationId) {
  const pack = getPackForIdentifier(simulationId)
  const profiles = createProfiles(pack)
  const runtime = getRuntimeState(pack)
  const elapsed = getPrepareElapsed(runtime)

  let visibleProfiles = profiles
  if (runtime.prepareStartedAt && !runtime.preparedAt) {
    visibleProfiles = profiles.slice(0, getVisibleCount(elapsed, PREPARE_DURATION_MS * 0.75, profiles.length))
  }

  return {
    success: true,
    data: {
      profiles: visibleProfiles,
      total_expected: profiles.length,
    },
  }
}

export function getDemoConfig(simulationId) {
  const pack = getPackForIdentifier(simulationId)
  const runtime = getRuntimeState(pack)
  const config = createSimulationConfig(pack)

  if (!runtime.prepareStartedAt || runtime.preparedAt) {
    return {
      success: true,
      data: {
        config_generated: true,
        config,
        summary: {
          total_agents: config.agent_configs.length,
          simulation_hours: config.time_config.total_simulation_hours,
          initial_posts_count: config.event_config.initial_posts.length,
          hot_topics_count: config.event_config.hot_topics.length,
          has_twitter_config: true,
          has_reddit_config: true,
        },
      },
    }
  }

  const elapsed = getPrepareElapsed(runtime)
  if (elapsed < PREPARE_DURATION_MS * 0.7) {
    return {
      success: true,
      data: {
        config_generated: false,
        generation_stage: 'generating_profiles',
      },
    }
  }

  return {
    success: true,
    data: {
      config_generated: false,
      generation_stage: 'generating_config',
    },
  }
}

export function startDemoSimulation({ simulation_id }) {
  const pack = getPackForIdentifier(simulation_id)
  withRuntime(pack.key, current => ({
    ...current,
    simulationStartedAt: Date.now(),
    simulationStoppedAt: null,
    reportGeneratedAt: null,
  }))

  return {
    success: true,
    data: {
      runner_status: 'running',
      twitter_running: true,
      reddit_running: true,
      twitter_completed: false,
      reddit_completed: false,
      twitter_current_round: 1,
      reddit_current_round: 1,
      twitter_actions_count: 0,
      reddit_actions_count: 0,
      total_rounds: 40,
      force_restarted: true,
      process_pid: 'DEMO',
    },
  }
}

function getSimulationProgress(pack) {
  const runtime = getRuntimeState(pack)
  if (!runtime.simulationStartedAt) {
    return 0
  }
  if (runtime.simulationStoppedAt) {
    return 1
  }
  return Math.max(0, Math.min(1, (Date.now() - runtime.simulationStartedAt) / SIMULATION_DURATION_MS))
}

export function getDemoRunStatus(simulationId) {
  const pack = getPackForIdentifier(simulationId)
  const progress = getSimulationProgress(pack)
  const totalRounds = 40
  const twitterActs = pack.simulation.communityA.acts
  const redditActs = pack.simulation.communityB.acts
  const currentRound = Math.max(1, Math.round(progress * totalRounds))
  const completed = progress >= 1

  return {
    success: true,
    data: {
      runner_status: completed ? 'completed' : 'running',
      twitter_running: !completed,
      reddit_running: !completed,
      twitter_completed: completed,
      reddit_completed: completed,
      twitter_current_round: completed ? totalRounds : currentRound,
      reddit_current_round: completed ? totalRounds : currentRound,
      twitter_actions_count: Math.round(twitterActs * progress),
      reddit_actions_count: Math.round(redditActs * progress),
      total_rounds: totalRounds,
    },
  }
}

export function getDemoRunStatusDetail(simulationId) {
  const pack = getPackForIdentifier(simulationId)
  const actions = createSimulationActions(pack)
  const runtime = getRuntimeState(pack)

  let visibleActions = actions
  if (runtime.simulationStartedAt && !runtime.simulationStoppedAt) {
    const elapsed = Date.now() - runtime.simulationStartedAt
    visibleActions = actions.slice(0, getVisibleCount(elapsed, SIMULATION_DURATION_MS, actions.length))
  }

  return {
    success: true,
    data: {
      all_actions: visibleActions,
    },
  }
}

export function stopDemoSimulation({ simulation_id }) {
  const pack = getPackForIdentifier(simulation_id)
  withRuntime(pack.key, current => ({
    ...current,
    simulationStoppedAt: Date.now(),
  }))

  return {
    success: true,
    data: {
      stopped: true,
    },
  }
}

export function generateDemoReport({ simulation_id }) {
  const pack = getPackForIdentifier(simulation_id)
  const ids = getIdsForPack(pack)

  withRuntime(pack.key, current => ({
    ...current,
    reportGeneratedAt: Date.now(),
  }))

  return {
    success: true,
    data: {
      report_id: ids.reportId,
    },
  }
}

function getReportElapsed(pack) {
  const runtime = getRuntimeState(pack)
  if (!runtime.reportGeneratedAt) {
    return REPORT_TIMELINE_DURATION_MS
  }
  return Date.now() - runtime.reportGeneratedAt
}

export function getDemoReport(reportId) {
  const pack = getPackForIdentifier(reportId)
  ensureReportStarted(pack)
  const ids = getIdsForPack(pack)
  const elapsed = getReportElapsed(pack)

  return {
    success: true,
    data: {
      report_id: ids.reportId,
      simulation_id: ids.simulationId,
      status: elapsed >= REPORT_TIMELINE_DURATION_MS ? 'completed' : 'processing',
      outline: createReportOutline(pack),
    },
  }
}

export function getDemoReportProgress(reportId) {
  const pack = getPackForIdentifier(reportId)
  ensureReportStarted(pack)
  const elapsed = getReportElapsed(pack)

  return {
    success: true,
    data: {
      status: elapsed >= REPORT_TIMELINE_DURATION_MS ? 'completed' : 'processing',
    },
  }
}

export function getDemoReportSections(reportId) {
  const pack = getPackForIdentifier(reportId)
  ensureReportStarted(pack)
  const elapsed = getReportElapsed(pack)
  const sections = createReportSections(pack)

  if (elapsed < REPORT_TIMELINE_DURATION_MS * 0.75) {
    return {
      success: true,
      data: {
        sections: [],
        is_complete: false,
      },
    }
  }

  return {
    success: true,
    data: {
      sections,
      is_complete: true,
    },
  }
}

export function getDemoAgentLog(reportId, fromLine = 0) {
  const pack = getPackForIdentifier(reportId)
  ensureReportStarted(pack)
  const elapsed = getReportElapsed(pack)
  const logs = createReportAgentLogs(pack)
  const visibleCount = getVisibleCount(elapsed, REPORT_TIMELINE_DURATION_MS, logs.length)
  const visibleLogs = logs.slice(0, visibleCount)

  return {
    success: true,
    data: {
      from_line: fromLine,
      logs: visibleLogs.slice(fromLine),
    },
  }
}

export function getDemoConsoleLog(reportId, fromLine = 0) {
  const pack = getPackForIdentifier(reportId)
  ensureReportStarted(pack)
  const logs = createConsoleLogs(pack)

  return {
    success: true,
    data: {
      from_line: fromLine,
      logs: logs.slice(fromLine),
    },
  }
}

export function chatWithDemoReport({ simulation_id, message }) {
  const pack = getPackForIdentifier(simulation_id)
  const prompt = String(message || '').toLowerCase()

  let response = pack.report.summary
  if (prompt.includes('spread') || prompt.includes('amplif')) {
    response = 'The issue spreads when local public pages and rumor relays convert private household strain into a legitimacy problem.'
  } else if (prompt.includes('trust')) {
    response = 'Institutional trust weakens when relief language arrives after people have already built their own explanation for the shock.'
  } else if (prompt.includes('first') || prompt.includes('earliest')) {
    response = 'The first signal is domestic adjustment: rationing, delay, and silence before visible complaint.'
  }

  return {
    success: true,
    data: {
      response,
    },
  }
}

export function interviewDemoAgents({ simulation_id, interviews = [] }) {
  const pack = getPackForIdentifier(simulation_id)
  const profiles = createProfiles(pack)
  const results = {}

  interviews.forEach((interview) => {
    const agentId = Number.parseInt(String(interview.agent_id), 10) || 0
    const interviewPack = pack.interaction.interviewAgents[agentId] || pack.interaction.interviewAgents[0]
    const profile = profiles[agentId] || profiles[0]
    results[`reddit_${agentId}`] = {
      response: interviewPack?.response || `${profile.username} would answer from the perspective encoded in the static demo pack.`,
    }
  })

  return {
    success: true,
    data: {
      result: {
        results,
      },
    },
  }
}
