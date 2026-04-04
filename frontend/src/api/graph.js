import service, { requestWithRetry } from './index'
import {
  buildDemoGraph,
  getDemoGraphData,
  getDemoProject,
  getDemoTaskStatus,
  isDemoRequest,
} from './demoRuntime'

/**
 * Generate the ontology (upload documents and simulated requirements)
 * @param {Object} data - contains files, simulation_requirement, project_name, etc.
 * @returns {Promise}
 */
export function generateOntology(formData) {
  return requestWithRetry(() => 
    service({
      url: '/api/graph/ontology/generate',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  )
}

/**
 * Build the graph
 * @param {Object} data - contains project_id, graph_name, etc.
 * @returns {Promise}
 */
export function buildGraph(data) {
  if (isDemoRequest(data?.project_id)) {
    return Promise.resolve(buildDemoGraph(data))
  }

  return requestWithRetry(() =>
    service({
      url: '/api/graph/build',
      method: 'post',
      data
    })
  )
}

/**
 * Query task status
 * @param {String} taskId - task ID
 * @returns {Promise}
 */
export function getTaskStatus(taskId) {
  if (isDemoRequest(taskId)) {
    return Promise.resolve(getDemoTaskStatus(taskId))
  }

  return service({
    url: `/api/graph/task/${taskId}`,
    method: 'get'
  })
}

/**
 * Get graph data
 * @param {String} graphId - graph ID
 * @returns {Promise}
 */
export function getGraphData(graphId) {
  if (isDemoRequest(graphId)) {
    return Promise.resolve(getDemoGraphData(graphId))
  }

  return service({
    url: `/api/graph/data/${graphId}`,
    method: 'get'
  })
}

/**
 * Get project information
 * @param {String} projectId - project ID
 * @returns {Promise}
 */
export function getProject(projectId) {
  if (isDemoRequest(projectId)) {
    return Promise.resolve(getDemoProject(projectId))
  }

  return service({
    url: `/api/graph/project/${projectId}`,
    method: 'get'
  })
}
