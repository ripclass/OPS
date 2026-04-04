import { DEMO_DEFAULT_PACK_KEY, DEMO_PACKS, getDemoPack, resolveDemoPackKey } from '../content/demoFlowPacks'
import { demoState } from '../store/demoFlow'
import { getPendingUpload } from '../store/pendingUpload'

const RUNTIME_STORAGE_KEY = 'murmur_demo_runtime_v2'
const REPORT_TIMELINE_DURATION_MS = 9000
const SIMULATION_DURATION_MS = 12000
const PREPARE_DURATION_MS = 7000
const GRAPH_BUILD_DURATION_MS = 9000
const DEMO_MIN_AGENT_COUNT = 100

const SEGMENT_KEY_ALIASES = {
  rural: 'rural',
  'urban working class': 'urban_working',
  urban_working: 'urban_working',
  'middle class': 'middle_class',
  middle_class: 'middle_class',
  corporate: 'corporate',
  'migration workers': 'migration_workers',
  migration_workers: 'migration_workers',
  students: 'students',
  women: 'women',
  elderly: 'elderly',
}

const COUNTRY_AGENT_POOLS = {
  bangladesh: {
    defaultSegments: ['urban_working', 'students', 'women', 'migration_workers'],
    segmentWeights: {
      rural: 0.35,
      urban_working: 0.24,
      middle_class: 0.15,
      corporate: 0.05,
      migration_workers: 0.09,
      students: 0.07,
      women: 0.03,
      elderly: 0.02,
    },
    femaleFirst: ['Halima', 'Shila', 'Rokeya', 'Munni', 'Nasima', 'Jannat', 'Rashida', 'Farzana', 'Sufia', 'Aklima', 'Momena', 'Shahnaz', 'Dilruba', 'Parvin'],
    maleFirst: ['Rafi', 'Harun', 'Sohel', 'Imran', 'Masud', 'Jahid', 'Rasel', 'Shakib', 'Monir', 'Babul', 'Kamal', 'Anis', 'Selim', 'Naeem'],
    surnames: ['Begum', 'Akhter', 'Khatun', 'Sultana', 'Miah', 'Hossain', 'Islam', 'Molla', 'Sheikh', 'Mondal', 'Sarker', 'Ahmed'],
    locations: ['Noakhali', 'Gazipur', 'Mirpur, Dhaka', 'Keraniganj', 'Savar', 'Narayanganj', 'Mohammadpur', 'Jatrabari', 'Mugda', 'Demra'],
    occupations: {
      rural: ['Fish drying worker', 'Shrimp peeling worker', 'Agricultural day laborer', 'Homestead poultry farmer', 'Vegetable seller'],
      urban_working: ['Garment worker', 'Market porter', 'Neighbourhood grocer helper', 'Food delivery rider', 'Construction helper'],
      middle_class: ['Government school teacher', 'Nurse', 'NGO program officer', 'Bank clerk', 'Journalist'],
      corporate: ['Software associate', 'Corporate communications officer', 'Private bank officer', 'Policy researcher', 'University lecturer'],
      migration_workers: ['Remittance household manager', 'Gulf returnee driver', 'Migrant wife running the household', 'Recruiting-agency caller', 'Overseas worker family bookkeeper'],
      students: ['Campus page admin', 'Private university student', 'Public university student', 'Coaching student', 'Freelance student organizer'],
      women: ['Queue manager for the household', 'Domestic worker', 'Beauty parlor worker', 'Microcredit field collector', 'Clinic support worker'],
      elderly: ['Retired madrasa teacher', 'Retired school clerk', 'Elderly shopkeeper', 'Village elder', 'Household pensioner'],
    },
  },
  india: {
    defaultSegments: ['urban_working', 'students', 'women', 'middle_class'],
    segmentWeights: {
      rural: 0.32,
      urban_working: 0.24,
      middle_class: 0.17,
      corporate: 0.08,
      migration_workers: 0.07,
      students: 0.07,
      women: 0.03,
      elderly: 0.02,
    },
    femaleFirst: ['Phulwanti', 'Sunita', 'Asha', 'Meena', 'Kavita', 'Pooja', 'Ruksana', 'Shabnam'],
    maleFirst: ['Rahul', 'Vikas', 'Imran', 'Arjun', 'Suresh', 'Rohit', 'Prakash', 'Amit'],
    surnames: ['Yadav', 'Kumar', 'Ansari', 'Sharma', 'Singh', 'Devi', 'Khan', 'Paswan'],
    locations: ['Delhi', 'Gaya', 'Noida', 'Surat', 'Lucknow', 'Patna', 'Mumbai', 'Kanpur'],
    occupations: {
      rural: ['NREGA worker', 'Bidi roller', 'ASHA volunteer', 'Agricultural laborer', 'Dairy farmer'],
      urban_working: ['Delivery rider', 'Construction worker', 'Domestic worker', 'Garment worker', 'Security guard'],
      middle_class: ['Government teacher', 'Clinic receptionist', 'Bank assistant', 'Journalist', 'Tutor'],
      corporate: ['Software engineer', 'Operations analyst', 'Law associate', 'Consultant', 'HR manager'],
      migration_workers: ['Surat construction migrant', 'Gulf returnee', 'Interstate factory worker', 'Driver', 'Warehouse loader'],
      students: ['Campus organizer', 'Civil service aspirant', 'Engineering student', 'Student page editor', 'Law student'],
      women: ['ASHA worker', 'Anganwadi worker', 'Tailor', 'Beauty worker', 'Nurse trainee'],
      elderly: ['Retired clerk', 'Retired teacher', 'Small shopkeeper', 'Temple committee elder', 'Pensioner'],
    },
  },
  pakistan: {
    defaultSegments: ['urban_working', 'women', 'migration_workers', 'students'],
    segmentWeights: {
      rural: 0.33,
      urban_working: 0.23,
      middle_class: 0.16,
      corporate: 0.06,
      migration_workers: 0.09,
      students: 0.07,
      women: 0.04,
      elderly: 0.02,
    },
    femaleFirst: ['Nasreen', 'Rabia', 'Farzana', 'Shazia', 'Nida', 'Rukhsar', 'Amina', 'Hina'],
    maleFirst: ['Bilal', 'Imran', 'Usman', 'Adnan', 'Salman', 'Hamza', 'Faisal', 'Adeel'],
    surnames: ['Khan', 'Butt', 'Ahmed', 'Siddiqui', 'Ansari', 'Malik', 'Chaudhry', 'Sheikh'],
    locations: ['Faisalabad', 'Lahore', 'Karachi', 'Rawalpindi', 'Multan', 'Sialkot', 'Peshawar', 'Hyderabad'],
    occupations: {
      rural: ['Cotton picker', 'Brick kiln worker', 'Agricultural laborer', 'Canal-irrigation farmer', 'Livestock caretaker'],
      urban_working: ['Power loom worker', 'Delivery rider', 'Factory loader', 'Workshop mechanic', 'Security guard'],
      middle_class: ['School teacher', 'Bank assistant', 'Clinic admin', 'Reporter', 'Pharmacist'],
      corporate: ['Software developer', 'Compliance officer', 'Media producer', 'Corporate lawyer', 'NGO coordinator'],
      migration_workers: ['Gulf household manager', 'Saudi construction worker family contact', 'Remittance-dependent spouse', 'Visa processing helper', 'Return migrant driver'],
      students: ['Student union poster', 'Campus debater', 'Exam prep student', 'WhatsApp admin', 'Law student'],
      women: ['Home-based embroidery worker', 'Tailor', 'LHW volunteer', 'Quran tutor', 'Beauty worker'],
      elderly: ['Retired trader', 'Mohalla elder', 'Retired government clerk', 'Mosque committee elder', 'Pensioner'],
    },
  },
  srilanka: {
    defaultSegments: ['urban_working', 'women', 'middle_class', 'students'],
    segmentWeights: {
      rural: 0.28,
      urban_working: 0.25,
      middle_class: 0.18,
      corporate: 0.08,
      migration_workers: 0.09,
      students: 0.06,
      women: 0.04,
      elderly: 0.02,
    },
    femaleFirst: ['Selvamani', 'Tharshi', 'Nadeesha', 'Shanika', 'Fathima', 'Kumari', 'Ruwani', 'Dilani'],
    maleFirst: ['Suren', 'Kasun', 'Nimal', 'Arun', 'Rizwan', 'Pradeep', 'Thilak', 'Sajith'],
    surnames: ['Perera', 'Fernando', 'Silva', 'Rajapaksa', 'Nadarajah', 'Subramaniam', 'Mendis', 'Ismail'],
    locations: ['Nuwara Eliya', 'Colombo', 'Kandy', 'Jaffna', 'Batticaloa', 'Galle', 'Negombo', 'Ratnapura'],
    occupations: {
      rural: ['Tea plucker', 'Smallholder farmer', 'Fishing worker', 'Gem pit laborer', 'Rubber tapper'],
      urban_working: ['FTZ garment worker', 'Bus conductor', 'Shop cashier', 'Delivery rider', 'Port helper'],
      middle_class: ['School teacher', 'Nurse', 'Bank officer', 'Local journalist', 'Account assistant'],
      corporate: ['IT analyst', 'Tourism manager', 'Law associate', 'Corporate planner', 'Private hospital executive'],
      migration_workers: ['Gulf remittance wife', 'Abroad domestic worker family contact', 'Return migrant technician', 'Transfer-dependent parent', 'Recruitment desk caller'],
      students: ['Campus activist', 'Tuition student', 'University society editor', 'Student page moderator', 'A-level candidate'],
      women: ['Tea estate household manager', 'Clinic attendant', 'Garment dormitory worker', 'School canteen worker', 'Union volunteer'],
      elderly: ['Retired public servant', 'Temple elder', 'Estate elder', 'Small trader', 'Pensioner'],
    },
  },
  nepal: {
    defaultSegments: ['migration_workers', 'women', 'rural', 'students'],
    segmentWeights: {
      rural: 0.35,
      urban_working: 0.2,
      middle_class: 0.15,
      corporate: 0.05,
      migration_workers: 0.13,
      students: 0.06,
      women: 0.04,
      elderly: 0.02,
    },
    femaleFirst: ['Kalpana', 'Sita', 'Asha', 'Mina', 'Laxmi', 'Pabitra', 'Sunita', 'Gita'],
    maleFirst: ['Milan', 'Suresh', 'Dinesh', 'Bikash', 'Rajesh', 'Kiran', 'Ram', 'Arjun'],
    surnames: ['Tamang', 'Sharma', 'Thapa', 'Magar', 'Yadav', 'Rai', 'Sherpa', 'Chaudhary'],
    locations: ['Sindhupalchok', 'Kathmandu', 'Pokhara', 'Biratnagar', 'Janakpur', 'Dang', 'Butwal', 'Dhading'],
    occupations: {
      rural: ['Farmer', 'Goat keeper', 'Village shopkeeper', 'Terrace cultivator', 'Vegetable seller'],
      urban_working: ['Delivery rider', 'Construction worker', 'Market helper', 'Bus helper', 'Factory hand'],
      middle_class: ['Teacher', 'Bank assistant', 'NGO officer', 'Clinic worker', 'Journalist'],
      corporate: ['IT associate', 'Project officer', 'Travel company analyst', 'Policy assistant', 'Private bank officer'],
      migration_workers: ['Remittance household manager', 'Qatar worker family contact', 'Malaysia returnee', 'Visa processing clerk', 'Transfer-dependent spouse'],
      students: ['Campus organizer', 'Exam student', 'Messenger group admin', 'Nursing student', 'Law student'],
      women: ['FCHV volunteer', 'Household manager', 'Tailor', 'School meal worker', 'Clinic attendant'],
      elderly: ['Retired teacher', 'Ward elder', 'Small landowner', 'Temple helper', 'Pensioner'],
    },
  },
}

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
    graphBuildTaskId: null,
    buildStartedAt: null,
    graphCompletedAt: null,
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
  const match = String(value || '').match(/^demo_([^_]+)_(project|graph|sim|report|prepare|graphbuild)$/)
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
    graphBuildTaskId: `demo_${pack.key}_graphbuild`,
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

function normalizeDemoAgentCount(value) {
  const parsed = Number.parseInt(String(value || '').replace(/,/g, '').trim(), 10)
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return DEMO_MIN_AGENT_COUNT
  }
  return parsed
}

function normalizeSegmentKey(value) {
  const normalized = String(value || '').trim().toLowerCase()
  return SEGMENT_KEY_ALIASES[normalized] || null
}

function resolveDemoRuntimeConfig(pack) {
  const runtime = getRuntimeState(pack)
  const pending = getPendingUpload()
  const selectedSegments = Array.isArray(runtime.selectedSegments) && runtime.selectedSegments.length
    ? runtime.selectedSegments.map(normalizeSegmentKey).filter(Boolean)
    : Array.isArray(pending.opsConfig?.segments)
      ? pending.opsConfig.segments.map(normalizeSegmentKey).filter(Boolean)
      : []

  return {
    selectedAgentCount: normalizeDemoAgentCount(runtime.selectedAgentCount || pending.opsConfig?.targetAgents),
    selectedSegments,
  }
}

function resolveDemoAgentCount(pack) {
  return resolveDemoRuntimeConfig(pack).selectedAgentCount
}

function resolveDemoSegments(pack) {
  const config = resolveDemoRuntimeConfig(pack)
  const pools = COUNTRY_AGENT_POOLS[pack.key] || COUNTRY_AGENT_POOLS.bangladesh
  return config.selectedSegments.length ? config.selectedSegments : pools.defaultSegments
}

function normalizeWeightSubset(weights) {
  const total = Object.values(weights).reduce((sum, weight) => sum + Math.max(weight || 0, 0), 0)
  if (total <= 0) {
    const keys = Object.keys(weights)
    const even = keys.length ? 1 / keys.length : 1
    return Object.fromEntries(keys.map(key => [key, even]))
  }
  return Object.fromEntries(
    Object.entries(weights).map(([key, weight]) => [key, Math.max(weight || 0, 0) / total])
  )
}

function allocateWeightedCounts(totalCount, weights) {
  const allocations = {}
  const remainders = []
  let assigned = 0

  Object.entries(weights).forEach(([key, weight]) => {
    const raw = totalCount * weight
    const count = Math.floor(raw)
    allocations[key] = count
    assigned += count
    remainders.push({ key, remainder: raw - count })
  })

  let remaining = totalCount - assigned
  remainders
    .sort((left, right) => right.remainder - left.remainder)
    .forEach(({ key }) => {
      if (remaining <= 0) {
        return
      }
      allocations[key] += 1
      remaining -= 1
    })

  return allocations
}

function buildSegmentAssignments(pack, totalAgents) {
  const pools = COUNTRY_AGENT_POOLS[pack.key] || COUNTRY_AGENT_POOLS.bangladesh
  const selectedSegments = resolveDemoSegments(pack)
  const availableWeights = pools.segmentWeights || {}
  const selectedWeights = normalizeWeightSubset(
    Object.fromEntries(selectedSegments.map(segment => [segment, availableWeights[segment] ?? 1]))
  )
  const allocations = allocateWeightedCounts(totalAgents, selectedWeights)
  const assignments = []

  Object.entries(allocations).forEach(([segment, count]) => {
    for (let index = 0; index < count; index += 1) {
      assignments.push(segment)
    }
  })

  assignments.sort((left, right) => selectedSegments.indexOf(left) - selectedSegments.indexOf(right))
  return assignments
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

function buildUniqueAgentName(pools, gender, index) {
  const firstNames = gender === 'female' ? pools.femaleFirst : pools.maleFirst
  const first = firstNames[index % firstNames.length]
  const surname = pools.surnames[Math.floor(index / firstNames.length) % pools.surnames.length]
  const cycle = Math.floor(index / (firstNames.length * pools.surnames.length))
  return cycle > 0 ? `${first} ${surname} ${cycle + 1}` : `${first} ${surname}`
}

function buildAgentProfession(pack, pools, segmentKey, index) {
  const pool = pools.occupations[segmentKey] || [pack.population.personas[index % pack.population.personas.length]?.role || 'Community member']
  return pool[index % pool.length]
}

function buildAgentLocation(pools, index) {
  return pools.locations[index % pools.locations.length]
}

function createDemoBio(pack, anchor, profession, location, segmentKey, detailNote) {
  const segmentNotes = {
    rural: 'Feels the shock first through food, transport, and local market exposure.',
    urban_working: 'Reads the crisis through wages, rent, and the next market visit.',
    middle_class: 'Balances household dignity with growing institutional distrust.',
    corporate: 'Interprets the issue through reputational risk and formal messaging gaps.',
    migration_workers: 'Measures every change against remittance timing and household duty.',
    students: 'Moves quickly between grievance, screenshots, and peer amplification.',
    women: 'Carries the household burden before the complaint becomes public.',
    elderly: 'Responds slowly, but remembers previous shocks and shortages clearly.',
  }

  return `${location}. ${profession}. ${detailNote} ${anchor.trait}. ${segmentNotes[segmentKey] || 'Tracks public change through local networks.'}`
}

function resolveAgentGender(segmentKey, index) {
  if (segmentKey === 'women') {
    return 'female'
  }
  if (segmentKey === 'elderly') {
    return index % 3 === 0 ? 'female' : 'male'
  }
  return index % 2 === 0 ? 'female' : 'male'
}

function createHandle(name, index) {
  const slug = String(name || 'murmur_agent')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
  return `${slug}_${String(index + 1).padStart(3, '0')}`
}

function createProfiles(pack) {
  const topicPool = buildTopicPool(pack)
  const anchors = pack.population.personas
  const pools = COUNTRY_AGENT_POOLS[pack.key] || COUNTRY_AGENT_POOLS.bangladesh
  const totalAgents = resolveDemoAgentCount(pack)
  const segmentAssignments = buildSegmentAssignments(pack, totalAgents)

  return Array.from({ length: totalAgents }, (_, index) => {
    const anchor = anchors[index % anchors.length]
    const segmentKey = segmentAssignments[index] || pools.defaultSegments[index % pools.defaultSegments.length]
    const gender = resolveAgentGender(segmentKey, index)
    const username = buildUniqueAgentName(pools, gender, index)
    const profession = buildAgentProfession(pack, pools, segmentKey, index)
    const location = buildAgentLocation(pools, index)
    const detailNote = pack.population.notes[index % pack.population.notes.length]
    const interested_topics = Array.from({ length: 4 }, (_unused, topicIndex) => {
      return topicPool[(index + topicIndex * 5) % topicPool.length]
    })

    return {
      id: index,
      agent_id: index,
      username,
      name: createHandle(username, index),
      profession,
      bio: createDemoBio(pack, anchor, profession, location, segmentKey, detailNote),
      interested_topics,
      entity_type: 'Person',
    }
  })
}

function createSimulationConfig(pack) {
  const profiles = createProfiles(pack)
  const previewProfiles = profiles.slice(0, Math.min(profiles.length, 24))

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
    agent_configs: previewProfiles.map((profile, index) => ({
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

function getGraphBuildElapsed(pack) {
  const runtime = getRuntimeState(pack)
  if (!runtime.buildStartedAt) {
    return 0
  }
  return Date.now() - runtime.buildStartedAt
}

function getGraphBuildProgress(pack) {
  const runtime = getRuntimeState(pack)
  if (runtime.graphCompletedAt) {
    return 1
  }
  if (!runtime.buildStartedAt) {
    return 0
  }
  return Math.max(0, Math.min(1, getGraphBuildElapsed(pack) / GRAPH_BUILD_DURATION_MS))
}

function createVisibleGraphData(pack) {
  const fullGraph = pack.graph.graphData
  const progress = getGraphBuildProgress(pack)

  if (progress >= 1) {
    return fullGraph
  }

  const visibleNodeCount = progress <= 0 ? 0 : Math.max(1, Math.floor(fullGraph.nodes.length * progress))
  const visibleNodes = fullGraph.nodes.slice(0, visibleNodeCount)
  const visibleNodeIds = new Set(visibleNodes.map(node => node.uuid))
  const edgeBudget = progress <= 0 ? 0 : Math.max(0, Math.floor(fullGraph.edges.length * progress))
  const visibleEdges = fullGraph.edges
    .filter(edge => visibleNodeIds.has(edge.source_node_uuid) && visibleNodeIds.has(edge.target_node_uuid))
    .slice(0, edgeBudget)

  return {
    nodes: visibleNodes,
    edges: visibleEdges,
    node_count: visibleNodes.length,
    edge_count: visibleEdges.length,
  }
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
  const ids = getIdsForPack(pack)
  const runtime = getRuntimeState(pack)
  const baseProject = createProjectData(pack)

  if (runtime.graphCompletedAt) {
    return {
      success: true,
      data: {
        ...baseProject,
        status: 'graph_completed',
        graph_id: ids.graphId,
      },
    }
  }

  if (runtime.buildStartedAt) {
    return {
      success: true,
      data: {
        ...baseProject,
        status: 'graph_building',
        graph_id: ids.graphId,
        graph_build_task_id: ids.graphBuildTaskId,
      },
    }
  }

  return {
    success: true,
    data: {
      ...baseProject,
      status: 'ontology_generated',
      graph_id: null,
      graph_build_task_id: null,
    },
  }
}

export function getDemoGraphData(graphId) {
  const pack = getPackForIdentifier(graphId)
  return {
    success: true,
    data: createVisibleGraphData(pack),
  }
}

export function buildDemoGraph({ project_id }) {
  const pack = getPackForIdentifier(project_id)
  const ids = getIdsForPack(pack)

  withRuntime(pack.key, current => ({
    ...current,
    graphBuildTaskId: ids.graphBuildTaskId,
    buildStartedAt: Date.now(),
    graphCompletedAt: null,
  }))

  return {
    success: true,
    data: {
      task_id: ids.graphBuildTaskId,
    },
  }
}

export function getDemoTaskStatus(taskId) {
  const pack = getPackForIdentifier(taskId)
  const progress = getGraphBuildProgress(pack)
  const completed = progress >= 1

  if (completed) {
    withRuntime(pack.key, current => ({
      ...current,
      graphCompletedAt: current.graphCompletedAt || Date.now(),
    }))

    return {
      success: true,
      data: {
        status: 'completed',
        progress: 100,
        message: 'GraphRAG build complete. Knowledge graph, memory traces, and community summaries are ready.',
      },
    }
  }

  let message = 'Initializing graph build...'
  if (progress >= 0.75) {
    message = 'Forming temporal memory and community summaries...'
  } else if (progress >= 0.5) {
    message = 'Extracting entities and relations from staged chunks...'
  } else if (progress >= 0.25) {
    message = 'Chunking source material and preparing GraphRAG build...'
  }

  return {
    success: true,
    data: {
      status: 'running',
      progress: Math.max(5, Math.round(progress * 100)),
      message,
    },
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

export function prepareDemoSimulation({ simulation_id, ops_population_params }) {
  const pack = getPackForIdentifier(simulation_id)
  const ids = getIdsForPack(pack)
  const normalizedAgentCount = normalizeDemoAgentCount(ops_population_params?.n_agents)
  const normalizedSegments = Array.isArray(ops_population_params?.segments)
    ? ops_population_params.segments.map(normalizeSegmentKey).filter(Boolean)
    : []

  withRuntime(pack.key, current => ({
    ...current,
    prepareTaskId: ids.prepareTaskId,
    prepareStartedAt: Date.now(),
    preparedAt: null,
    selectedAgentCount: normalizedAgentCount,
    selectedSegments: normalizedSegments,
  }))

  const profiles = createProfiles(pack)

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
  const profiles = createProfiles(pack)

  if (!runtime.prepareStartedAt || runtime.preparedAt) {
    return {
      success: true,
      data: {
        config_generated: true,
        config,
        summary: {
          total_agents: profiles.length,
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
