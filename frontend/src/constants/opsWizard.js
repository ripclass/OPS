export const USE_CASE_OPTIONS = [
  { value: 'Policy', label: 'Policy', description: 'Pre-test reaction to public decisions and institutional announcements.' },
  { value: 'Health', label: 'Health', description: 'Forecast response to campaigns, shortages, outbreaks, or care access shifts.' },
  { value: 'Brand', label: 'Brand', description: 'Model demand shocks, reputation swings, and commercial rumor spread.' },
  { value: 'Crisis', label: 'Crisis', description: 'Track narrative escalation under social, political, or security stress.' },
  { value: 'Disaster', label: 'Disaster', description: 'Map behavioral shifts during floods, shortages, displacement, or warning events.' },
]

export const RUN_TYPE_OPTIONS = [
  { value: 'Domestic', label: 'Domestic', description: 'One-country public response inside a single national context.' },
  { value: 'Diaspora', label: 'Diaspora', description: 'Overseas communities linked to one origin country and family networks back home.' },
  { value: 'Corridor-based', label: 'Corridor-based', description: 'Sender and receiver behavior across remittance or mobility corridors.' },
  { value: 'Regional multi-country', label: 'Regional multi-country', description: 'Multi-country South Asia runs without forcing diaspora logic.' },
]

export const COUNTRY_OPTIONS = [
  { value: 'Bangladesh', label: 'Bangladesh', description: 'Population response across districts, cities, and rural communities.' },
  { value: 'India', label: 'India', description: 'Layered regional response across class, language, and state-level contexts.' },
  { value: 'Pakistan', label: 'Pakistan', description: 'Behavior under political, household, and media network pressure.' },
  { value: 'Nepal', label: 'Nepal', description: 'Mountain, urban, and migration-linked publics with strong local and overseas ties.' },
  { value: 'Sri Lanka', label: 'Sri Lanka', description: 'Island-wide response shaped by cost pressure, language, and political memory.' },
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

export const REGION_OPTIONS = [
  { value: 'GCC', label: 'GCC', description: 'Gulf Cooperation Council migration and remittance corridors.' },
  { value: 'UK', label: 'UK', description: 'South Asian diaspora communities in the United Kingdom.' },
  { value: 'EU', label: 'EU', description: 'European diaspora and cross-border professional networks.' },
  { value: 'North America', label: 'North America', description: 'Diaspora communities across the United States and Canada.' },
  { value: 'Southeast Asia', label: 'Southeast Asia', description: 'Migration and trade-linked audiences across Southeast Asia.' },
  { value: 'Australia/NZ', label: 'Australia/NZ', description: 'Diaspora publics in Australia and New Zealand.' },
  { value: 'Global', label: 'Global', description: 'Distributed international communities across multiple destination regions.' },
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
