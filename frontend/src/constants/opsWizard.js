export const USE_CASE_OPTIONS = [
  { value: 'Policy', label: 'Policy', description: 'Pre-test reaction to public decisions and institutional announcements.' },
  { value: 'Health', label: 'Health', description: 'Forecast response to campaigns, shortages, outbreaks, or care access shifts.' },
  { value: 'Brand', label: 'Brand', description: 'Model demand shocks, reputation swings, and commercial rumor spread.' },
  { value: 'Crisis', label: 'Crisis', description: 'Track narrative escalation under social, political, or security stress.' },
  { value: 'Disaster', label: 'Disaster', description: 'Map behavioral shifts during floods, shortages, displacement, or warning events.' },
]

export const COUNTRY_OPTIONS = [
  { value: 'Bangladesh', label: 'Bangladesh', description: 'Population response across districts, cities, and rural communities.' },
  { value: 'India', label: 'India', description: 'Layered regional response across class, language, and state-level contexts.' },
  { value: 'Pakistan', label: 'Pakistan', description: 'Behavior under political, household, and media network pressure.' },
  { value: 'Diaspora', label: 'Diaspora', description: 'Cross-border publics, migrant workers, and family-linked influence flows.' },
]

export const SEGMENT_OPTIONS = [
  { value: 'Rural', label: 'Rural', description: 'Village and peri-rural communities with strong local network effects.' },
  { value: 'Urban working class', label: 'Urban working class', description: 'Day-wage and lower-income households in dense urban environments.' },
  { value: 'Middle class', label: 'Middle class', description: 'Aspirational families balancing cost pressure and institutional trust.' },
  { value: 'Corporate', label: 'Corporate', description: 'Professionals whose public signaling carries higher reputational risk.' },
  { value: 'Migration workers', label: 'Migration workers', description: 'Internal and overseas workers shaped by remittance and family obligations.' },
  { value: 'Students', label: 'Students', description: 'High-reactivity youth segments with fast peer-network propagation.' },
  { value: 'Women', label: 'Women', description: 'Gendered response dynamics across household, safety, and reputation concerns.' },
  { value: 'Elderly', label: 'Elderly', description: 'Older publics with different trust patterns and slower but durable spread.' },
]

export const OUTPUT_OPTIONS = [
  { value: 'PDF report', label: 'PDF report', description: 'Download a structured narrative report after the run.' },
  { value: 'CSV export', label: 'CSV export', description: 'Export tabular output for downstream analysis or dashboards.' },
]

export const AGENT_COUNT_OPTIONS = [
  { value: '100', label: '100 agents', description: 'Rapid directional test for one scenario slice.', estimateLabel: '$499' },
  { value: '1000', label: '1,000 agents', description: 'Segment-level read with broader cascade behavior.', estimateLabel: '$1499' },
  { value: '10000', label: '10,000 agents', description: 'Large scenario stress test across multiple publics.', estimateLabel: '$4999' },
  { value: 'custom', label: 'Custom', description: 'Manual scoping for higher-scale or bespoke deployments.', estimateLabel: 'Contact us' },
]

export const getAgentEstimateLabel = (agentScale) => {
  const option = AGENT_COUNT_OPTIONS.find((item) => item.value === agentScale)
  return option?.estimateLabel || 'Contact us'
}

export const getTargetAgentsLabel = (agentScale, customAgentCount) => {
  if (agentScale === 'custom') {
    const normalized = String(customAgentCount || '').trim()
    return normalized ? `${normalized} (custom)` : 'Custom'
  }

  const option = AGENT_COUNT_OPTIONS.find((item) => item.value === agentScale)
  return option ? option.label : '100 agents'
}
