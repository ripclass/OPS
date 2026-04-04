import service, { requestWithRetry } from './index'
import {
  chatWithDemoReport,
  generateDemoReport,
  getDemoAgentLog,
  getDemoConsoleLog,
  getDemoReport,
  getDemoReportProgress,
  getDemoReportSections,
  isDemoRequest,
} from './demoRuntime'

/**
 * Start report generation
 * @param {Object} data - { simulation_id, force_regenerate? }
 */
export const generateReport = (data) => {
  if (isDemoRequest(data?.simulation_id)) {
    return Promise.resolve(generateDemoReport(data))
  }

  return requestWithRetry(() => service.post('/api/report/generate', data), 3, 1000)
}

/**
 * Get report generation status
 * @param {string} reportId
 */
export const getReportStatus = (reportId) => {
  return service.get(`/api/report/generate/status`, { params: { report_id: reportId } })
}

/**
 * Get Agent log (incremental)
 * @param {string} reportId
 * @param {number} fromLine - start line for fetching logs
 */
export const getAgentLog = (reportId, fromLine = 0) => {
  if (isDemoRequest(reportId)) {
    return Promise.resolve(getDemoAgentLog(reportId, fromLine))
  }

  return service.get(`/api/report/${reportId}/agent-log`, { params: { from_line: fromLine } })
}

/**
 * Get console log (incremental)
 * @param {string} reportId
 * @param {number} fromLine - start line for fetching logs
 */
export const getConsoleLog = (reportId, fromLine = 0) => {
  if (isDemoRequest(reportId)) {
    return Promise.resolve(getDemoConsoleLog(reportId, fromLine))
  }

  return service.get(`/api/report/${reportId}/console-log`, { params: { from_line: fromLine } })
}

/**
 * Get report details
 * @param {string} reportId
 */
export const getReport = (reportId) => {
  if (isDemoRequest(reportId)) {
    return Promise.resolve(getDemoReport(reportId))
  }

  return service.get(`/api/report/${reportId}`)
}

/**
 * Get live report progress
 * @param {string} reportId
 */
export const getReportProgress = (reportId) => {
  if (isDemoRequest(reportId)) {
    return Promise.resolve(getDemoReportProgress(reportId))
  }

  return service.get(`/api/report/${reportId}/progress`)
}

/**
 * Get generated report sections
 * @param {string} reportId
 */
export const getReportSections = (reportId) => {
  if (isDemoRequest(reportId)) {
    return Promise.resolve(getDemoReportSections(reportId))
  }

  return service.get(`/api/report/${reportId}/sections`)
}

/**
 * Communicate with Report Agent
 * @param {Object} data - { simulation_id, message, chat_history? }
 */
export const chatWithReport = (data) => {
  if (isDemoRequest(data?.simulation_id)) {
    return Promise.resolve(chatWithDemoReport(data))
  }

  return requestWithRetry(() => service.post('/api/report/chat', data), 3, 1000)
}
