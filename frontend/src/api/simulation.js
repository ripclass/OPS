import service, { requestWithRetry } from './index'
import {
  createDemoSimulation,
  getDemoConfig,
  getDemoPrepareStatus,
  getDemoProfiles,
  getDemoRunStatus,
  getDemoRunStatusDetail,
  getDemoSimulation,
  interviewDemoAgents,
  isDemoRequest,
  prepareDemoSimulation,
  startDemoSimulation,
  stopDemoSimulation,
} from './demoRuntime'

/**
 * Create simulation
 * @param {Object} data - { project_id, graph_id?, enable_twitter?, enable_reddit? }
 */
export const createSimulation = (data) => {
  if (isDemoRequest(data?.project_id) || isDemoRequest(data?.graph_id)) {
    return Promise.resolve(createDemoSimulation(data?.project_id || data?.graph_id))
  }

  return requestWithRetry(() => service.post('/api/simulation/create', data), 3, 1000)
}

/**
 * Prepare the simulation environment (asynchronous task)
 * @param {Object} data - { simulation_id, entity_types?, use_llm_for_profiles?, parallel_profile_count?, force_regenerate? }
 */
export const prepareSimulation = (data) => {
  if (isDemoRequest(data?.simulation_id)) {
    return Promise.resolve(prepareDemoSimulation(data))
  }

  return requestWithRetry(() => service.post('/api/simulation/prepare', data), 3, 1000)
}

/**
 * Query the preparation task progress
 * @param {Object} data - { task_id?, simulation_id? }
 */
export const getPrepareStatus = (data) => {
  if (isDemoRequest(data?.simulation_id) || isDemoRequest(data?.task_id)) {
    return Promise.resolve(getDemoPrepareStatus(data))
  }

  return service.post('/api/simulation/prepare/status', data)
}

/**
 * Get simulated state
 * @param {string} simulationId
 */
export const getSimulation = (simulationId) => {
  if (isDemoRequest(simulationId)) {
    return Promise.resolve(getDemoSimulation(simulationId))
  }

  return service.get(`/api/simulation/${simulationId}`)
}

/**
 * Retrieve simulated Agent Profiles
 * @param {string} simulationId
 * @param {string} platform - 'reddit' | 'twitter'
 */
export const getSimulationProfiles = (simulationId, platform = 'reddit') => {
  return service.get(`/api/simulation/${simulationId}/profiles`, { params: { platform } })
}

/**
 * Real-time retrieval of generating Agent Profiles
 * @param {string} simulationId
 * @param {string} platform - 'reddit' | 'twitter'
 */
export const getSimulationProfilesRealtime = (simulationId, platform = 'reddit') => {
  if (isDemoRequest(simulationId)) {
    return Promise.resolve(getDemoProfiles(simulationId))
  }

  return service.get(`/api/simulation/${simulationId}/profiles/realtime`, { params: { platform } })
}

/**
 * Get simulated configuration
 * @param {string} simulationId
 */
export const getSimulationConfig = (simulationId) => {
  return service.get(`/api/simulation/${simulationId}/config`)
}

/**
 * Real-time retrieval of the simulation configuration in progress
 * @param {string} simulationId
 * @returns {Promise} Returns configuration information, including metadata and configuration content
 */
export const getSimulationConfigRealtime = (simulationId) => {
  if (isDemoRequest(simulationId)) {
    return Promise.resolve(getDemoConfig(simulationId))
  }

  return service.get(`/api/simulation/${simulationId}/config/realtime`)
}

/**
 * List all simulations
 * @param {string} projectId - optional, filter by project ID
 */
export const listSimulations = (projectId) => {
  const params = projectId ? { project_id: projectId } : {}
  return service.get('/api/simulation/list', { params })
}

/**
 * Start Simulation
 * @param {Object} data - { simulation_id, platform?, max_rounds?, enable_graph_memory_update? }
 */
export const startSimulation = (data) => {
  if (isDemoRequest(data?.simulation_id)) {
    return Promise.resolve(startDemoSimulation(data))
  }

  return requestWithRetry(() => service.post('/api/simulation/start', data), 3, 1000)
}

/**
 * Stop Simulation
 * @param {Object} data - { simulation_id }
 */
export const stopSimulation = (data) => {
  if (isDemoRequest(data?.simulation_id)) {
    return Promise.resolve(stopDemoSimulation(data))
  }

  return service.post('/api/simulation/stop', data)
}

/**
 * Get the real-time simulation run status
 * @param {string} simulationId
 */
export const getRunStatus = (simulationId) => {
  if (isDemoRequest(simulationId)) {
    return Promise.resolve(getDemoRunStatus(simulationId))
  }

  return service.get(`/api/simulation/${simulationId}/run-status`)
}

/**
 * Get detailed simulation run status (including recent actions)
 * @param {string} simulationId
 */
export const getRunStatusDetail = (simulationId) => {
  if (isDemoRequest(simulationId)) {
    return Promise.resolve(getDemoRunStatusDetail(simulationId))
  }

  return service.get(`/api/simulation/${simulationId}/run-status/detail`)
}

/**
 * Retrieve posts from the simulation
 * @param {string} simulationId
 * @param {string} platform - 'reddit' | 'twitter'
 * @param {number} limit - Number of results to return
 * @param {number} offset - offset amount
 */
export const getSimulationPosts = (simulationId, platform = 'reddit', limit = 50, offset = 0) => {
  return service.get(`/api/simulation/${simulationId}/posts`, {
    params: { platform, limit, offset }
  })
}

/**
 * Get simulated timeline (aggregated by rounds)
 * @param {string} simulationId
 * @param {number} startRound - Starting round
 * @param endRound - endRound - End round of the simulation
 */
export const getSimulationTimeline = (simulationId, startRound = 0, endRound = null) => {
  const params = { start_round: startRound }
  if (endRound !== null) {
    params.end_round = endRound
  }
  return service.get(`/api/simulation/${simulationId}/timeline`, { params })
}

/**
 * Retrieve agent statistics
 * @param {string} simulationId
 */
export const getAgentStats = (simulationId) => {
  return service.get(`/api/simulation/${simulationId}/agent-stats`)
}

/**
 * Fetch historical actions performed by agents
 * @param {string} simulationId
 * @param {Object} params - { limit, offset, platform, agent_id, round_num }
 */
export const getSimulationActions = (simulationId, params = {}) => {
  return service.get(`/api/simulation/${simulationId}/actions`, { params })
}

/**
 * Close the simulation environment (graceful exit)
 * @param {Object} data - { simulation_id, timeout? }
 */
export const closeSimulationEnv = (data) => {
  if (isDemoRequest(data?.simulation_id)) {
    return Promise.resolve({
      success: true,
      data: {
        closed: true,
      },
    })
  }

  return service.post('/api/simulation/close-env', data)
}

/**
 * Get the state of the simulation environment
 * @param {Object} data - { simulation_id }
 */
export const getEnvStatus = (data) => {
  if (isDemoRequest(data?.simulation_id)) {
    return Promise.resolve({
      success: true,
      data: {
        env_alive: false,
      },
    })
  }

  return service.post('/api/simulation/env-status', data)
}

/**
 * Batch interview agents
 * @param {Object} data - { simulation_id, interviews: [{ agent_id, prompt }] }
 */
export const interviewAgents = (data) => {
  if (isDemoRequest(data?.simulation_id)) {
    return Promise.resolve(interviewDemoAgents(data))
  }

  return requestWithRetry(() => service.post('/api/simulation/interview/batch', data), 3, 1000)
}

/**
 * Retrieve a list of historical simulations with project details
 * Used for displaying historical projects on the home page
 * @param limit - Limit the number of results returned
 */
export const getSimulationHistory = (limit = 20) => {
  return service.get('/api/simulation/history', { params: { limit } })
}

