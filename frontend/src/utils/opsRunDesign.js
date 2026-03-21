const DEFAULT_OPS_CONFIG = Object.freeze({
  runType: 'Domestic',
  originCountry: 'Bangladesh',
  originCountries: [],
  audienceRegion: '',
  corridor: '',
  segments: [],
  targetAgents: '100',
  requestedOutputs: ['PDF report'],
  demoModeBypass: true,
})

export function createDefaultOpsConfig(overrides = {}) {
  return {
    ...DEFAULT_OPS_CONFIG,
    ...overrides,
    originCountries: Array.isArray(overrides.originCountries) ? [...overrides.originCountries] : [...DEFAULT_OPS_CONFIG.originCountries],
    segments: Array.isArray(overrides.segments) ? [...overrides.segments] : [...DEFAULT_OPS_CONFIG.segments],
    requestedOutputs: Array.isArray(overrides.requestedOutputs) ? [...overrides.requestedOutputs] : [...DEFAULT_OPS_CONFIG.requestedOutputs],
  }
}

export function normalizeOpsConfig(config = {}) {
  const normalized = createDefaultOpsConfig(config)
  normalized.runType = String(normalized.runType || DEFAULT_OPS_CONFIG.runType).trim() || DEFAULT_OPS_CONFIG.runType
  normalized.originCountry = String(normalized.originCountry || DEFAULT_OPS_CONFIG.originCountry).trim() || DEFAULT_OPS_CONFIG.originCountry
  normalized.originCountries = Array.from(new Set((normalized.originCountries || []).map((value) => String(value).trim()).filter(Boolean)))
  normalized.audienceRegion = String(normalized.audienceRegion || '').trim()
  normalized.corridor = String(normalized.corridor || '').trim()
  normalized.segments = Array.from(new Set((normalized.segments || []).map((value) => String(value).trim()).filter(Boolean)))
  normalized.targetAgents = String(normalized.targetAgents || DEFAULT_OPS_CONFIG.targetAgents).trim() || DEFAULT_OPS_CONFIG.targetAgents
  normalized.requestedOutputs = Array.from(new Set((normalized.requestedOutputs || []).map((value) => String(value).trim()).filter(Boolean)))
  if (normalized.requestedOutputs.length === 0) {
    normalized.requestedOutputs = [...DEFAULT_OPS_CONFIG.requestedOutputs]
  }
  normalized.demoModeBypass = normalized.demoModeBypass !== false
  return normalized
}

function parseMetadataLines(blockText = '') {
  const metadata = {}
  blockText
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .forEach((line) => {
      const separator = line.indexOf(':')
      if (separator === -1) return
      const key = line.slice(0, separator).trim()
      const value = line.slice(separator + 1).trim()
      metadata[key] = value
    })
  return metadata
}

export function parseOpsSimulationRequirement(requirement = '') {
  const rawRequirement = String(requirement || '')
  const match = rawRequirement.match(/\[OPS Wizard Metadata\]([\s\S]*?)\[\/OPS Wizard Metadata\]/)

  if (!match) {
    return {
      hasMetadata: false,
      baseRequirement: rawRequirement.trim(),
      opsConfig: createDefaultOpsConfig(),
    }
  }

  const metadata = parseMetadataLines(match[1])
  const scenarioMatch = rawRequirement.match(/Scenario:\s*([\s\S]*)$/)
  const baseRequirement = scenarioMatch ? scenarioMatch[1].trim() : rawRequirement.replace(match[0], '').trim()

  const opsConfig = normalizeOpsConfig({
    runType: metadata['Run type'],
    originCountry: metadata['Origin country'],
    originCountries: metadata['Origin countries'] ? metadata['Origin countries'].split(',').map((item) => item.trim()) : [],
    audienceRegion: metadata['Audience region'],
    corridor: metadata.Corridor,
    segments: metadata.Segments ? metadata.Segments.split(',').map((item) => item.trim()) : [],
    targetAgents: metadata['Target agents'],
    requestedOutputs: metadata['Requested outputs'] ? metadata['Requested outputs'].split(',').map((item) => item.trim()) : [],
  })

  return {
    hasMetadata: true,
    baseRequirement,
    opsConfig,
  }
}

export function buildOpsSimulationRequirement(baseRequirement = '', config = {}) {
  const normalized = normalizeOpsConfig(config)
  const scenarioText = String(baseRequirement || '').trim()
  const lines = [
    '[OPS Wizard Metadata]',
    `Run type: ${normalized.runType}`,
  ]

  if (normalized.runType === 'Regional multi-country') {
    lines.push(`Origin countries: ${normalized.originCountries.join(', ')}`)
  } else {
    lines.push(`Origin country: ${normalized.originCountry}`)
  }

  if (normalized.audienceRegion) {
    lines.push(`Audience region: ${normalized.audienceRegion}`)
  }
  if (normalized.corridor) {
    lines.push(`Corridor: ${normalized.corridor}`)
  }

  lines.push(`Segments: ${normalized.segments.join(', ') || 'None selected'}`)
  lines.push(`Target agents: ${normalized.targetAgents}`)
  lines.push(`Requested outputs: ${normalized.requestedOutputs.join(', ') || 'None selected'}`)
  lines.push('[/OPS Wizard Metadata]', '', 'Scenario:', scenarioText)

  return lines.join('\n').trim()
}

export function getOpsGeographySummary(config = {}) {
  const normalized = normalizeOpsConfig(config)

  if (normalized.runType === 'Regional multi-country') {
    return normalized.originCountries.join(', ') || 'South Asia'
  }

  if (normalized.runType === 'Diaspora') {
    return normalized.audienceRegion ? `${normalized.originCountry} diaspora in ${normalized.audienceRegion}` : `${normalized.originCountry} diaspora`
  }

  if (normalized.runType === 'Corridor-based') {
    return normalized.corridor || `${normalized.originCountry} corridor`
  }

  return normalized.originCountry
}

export function validateOpsConfig(config = {}) {
  const normalized = normalizeOpsConfig(config)
  const errors = []

  if (normalized.runType === 'Regional multi-country' && normalized.originCountries.length < 2) {
    errors.push('Regional multi-country runs need at least two origin countries.')
  }

  if (normalized.runType !== 'Regional multi-country' && !normalized.originCountry) {
    errors.push('Choose an origin country.')
  }

  if (normalized.runType === 'Diaspora' && !normalized.audienceRegion) {
    errors.push('Choose an audience region for diaspora runs.')
  }

  if (normalized.runType === 'Corridor-based' && !normalized.corridor) {
    errors.push('Describe the corridor for corridor-based runs.')
  }

  if (normalized.segments.length === 0) {
    errors.push('Select at least one demographic segment.')
  }

  return {
    valid: errors.length === 0,
    errors,
    normalized,
  }
}
