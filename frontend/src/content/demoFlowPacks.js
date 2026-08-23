// The report is the artefact the agency puts in front of a client, so it is
// long. Each Bangladesh pack keeps its report sections, its report-agent
// answers and its interview material in its own module under reportPacks/,
// which is also where the answers get deep enough to survive a real Q and A.
import { BANGLADESH_REPORT } from './reportPacks/bangladesh.js'
import { BDBRAND_REPORT } from './reportPacks/bdbrand.js'
import { BDNGO_REPORT } from './reportPacks/bdngo.js'
import { BDTELCO_REPORT } from './reportPacks/bdtelco.js'
import { BDWALLET_REPORT } from './reportPacks/bdwallet.js'
import { BDWAGE_REPORT } from './reportPacks/bdwage.js'
import { BDHEALTH_REPORT } from './reportPacks/bdhealth.js'

const COUNTRY_CODE_TO_PACK = {
  BD: 'bangladesh',
  IN: 'india',
  PK: 'pakistan',
  LK: 'srilanka',
  NP: 'nepal',
  // A second Bangladesh pack, selected with ?country=BD-BRAND. Plain BD keeps
  // the default price-shock flow untouched.
  'BD-BRAND': 'bdbrand',
  // Five further Bangladesh scenarios. Each one is built around a different
  // silence lane, which is the reading the product exists to sell.
  'BD-NGO': 'bdngo',
  'BD-TELCO': 'bdtelco',
  'BD-WALLET': 'bdwallet',
  'BD-WAGE': 'bdwage',
  'BD-HEALTH': 'bdhealth',
}

const GRAPH_COLORS = {
  GovernmentAgency: '#ff6b35',
  MediaOutlet: '#004e89',
  Person: '#7b2d8e',
  Organization: '#1a936f',
  OpinionLeader: '#c5283d',
  Location: '#f39c12',
  Entity: '#3498db',
}

const GRAPH_TEMPLATE = [
  ['gov_notice', 'Government Notice', ['GovernmentAgency']],
  ['commodity', 'Rice Price Shock', ['Entity']],
  ['bazaar', 'Bazaar Rumor Chain', ['Organization']],
  ['students', 'Student Facebook Pages', ['MediaOutlet']],
  ['remittance', 'Remittance Households', ['Person']],
  ['workers', 'Garment Workers', ['Person']],
  ['mosque', 'Mosque Network', ['Organization']],
  ['relief', 'Relief Office', ['GovernmentAgency']],
  ['media', 'Local Media', ['MediaOutlet']],
  ['grocers', 'Neighborhood Grocers', ['Organization']],
  ['mothers', 'Mothers in Queue', ['Person']],
  ['dhaka', 'Dhaka', ['Location']],
]

const GRAPH_EDGES = [
  ['gov_notice', 'commodity', 'ANNOUNCES'],
  ['commodity', 'bazaar', 'TRIGGERS'],
  ['commodity', 'students', 'SPARKS'],
  ['commodity', 'remittance', 'PRESSURES'],
  ['commodity', 'workers', 'STRAINS'],
  ['bazaar', 'mothers', 'REACHES'],
  ['students', 'media', 'AMPLIFIES'],
  ['media', 'relief', 'PRESSURES'],
  ['mosque', 'mothers', 'INFLUENCES'],
  ['grocers', 'bazaar', 'ECHOES'],
  ['dhaka', 'bazaar', 'HOSTS'],
  ['dhaka', 'students', 'HOSTS'],
  ['dhaka', 'workers', 'HOSTS'],
]

const GRAPH_CLUSTER_SPECS = [
  {
    anchor: 'students',
    label: 'MediaOutlet',
    count: 18,
    secondary: ['media', 'bazaar', 'dhaka'],
    cross: ['workers', 'mothers'],
    relations: ['AMPLIFIES', 'ECHOES', 'THREADS_WITH'],
    nameFactory: ({ city }, index) => `${city} student page ${String(index + 1).padStart(2, '0')}`,
  },
  {
    anchor: 'media',
    label: 'MediaOutlet',
    count: 16,
    secondary: ['students', 'gov_notice', 'relief'],
    cross: ['bazaar', 'grocers'],
    relations: ['FRAMES', 'REPOSTS', 'REFERENCES'],
    nameFactory: ({ countryLabel }, index) => `${countryLabel} bulletin ${String(index + 1).padStart(2, '0')}`,
  },
  {
    anchor: 'remittance',
    label: 'Person',
    count: 22,
    secondary: ['commodity', 'grocers', 'mothers'],
    cross: ['workers', 'dhaka'],
    relations: ['ABSORBS', 'SHARES_WITH', 'DEPENDS_ON'],
    nameFactory: ({ city }, index) => `${city} household ${String(index + 1).padStart(2, '0')}`,
  },
  {
    anchor: 'workers',
    label: 'Person',
    count: 20,
    secondary: ['commodity', 'dhaka', 'students'],
    cross: ['media', 'grocers'],
    relations: ['STRAINS', 'HOSTS', 'COMMENTS_ON'],
    nameFactory: ({ city }, index) => `${city} worker ${String(index + 1).padStart(2, '0')}`,
  },
  {
    anchor: 'mothers',
    label: 'Person',
    count: 18,
    secondary: ['bazaar', 'grocers', 'relief'],
    cross: ['remittance', 'mosque'],
    relations: ['QUEUES_AT', 'HEARS', 'ASKS'],
    nameFactory: ({ city }, index) => `${city} queue mother ${String(index + 1).padStart(2, '0')}`,
  },
  {
    anchor: 'bazaar',
    label: 'Organization',
    count: 16,
    secondary: ['grocers', 'media', 'mothers'],
    cross: ['students', 'relief'],
    relations: ['ECHOES', 'CONNECTS', 'REACHES'],
    nameFactory: ({ city }, index) => `${city} bazaar thread ${String(index + 1).padStart(2, '0')}`,
  },
  {
    anchor: 'grocers',
    label: 'Organization',
    count: 12,
    secondary: ['bazaar', 'commodity', 'dhaka'],
    cross: ['remittance', 'workers'],
    relations: ['UPDATES', 'HOSTS', 'WARNS'],
    nameFactory: ({ city }, index) => `${city} grocer lane ${String(index + 1).padStart(2, '0')}`,
  },
  {
    anchor: 'gov_notice',
    label: 'GovernmentAgency',
    count: 10,
    secondary: ['relief', 'media', 'students'],
    cross: ['commodity', 'dhaka'],
    relations: ['ANNOUNCES', 'CLARIFIES', 'DELAYS'],
    nameFactory: ({ countryLabel }, index) => `${countryLabel} notice relay ${String(index + 1).padStart(2, '0')}`,
  },
  {
    anchor: 'relief',
    label: 'GovernmentAgency',
    count: 10,
    secondary: ['gov_notice', 'mothers', 'grocers'],
    cross: ['bazaar', 'media'],
    relations: ['RESPONDS_TO', 'SERVES', 'MISSES'],
    nameFactory: ({ city }, index) => `${city} relief desk ${String(index + 1).padStart(2, '0')}`,
  },
  {
    anchor: 'dhaka',
    label: 'Location',
    count: 14,
    secondary: ['workers', 'students', 'bazaar'],
    cross: ['relief', 'media'],
    relations: ['HOSTS', 'CONTAINS', 'LINKS'],
    nameFactory: ({ city }, index) => `${city} ward ${String(index + 1).padStart(2, '0')}`,
  },
]

function createGraphData(key, context = {}) {
  // clusterNouns lets a pack rename the generated cluster nodes. Without it the
  // shared nameFactory wording applies, which is right for a price shock but
  // reads oddly elsewhere ("Dhaka queue mother 01" in a brand crisis).
  const { labels = {}, countryLabel = 'Country', city = 'City', clusterNouns = {} } = context
  const nodes = GRAPH_TEMPLATE.map(([id, name, nodeLabels]) => ({
    uuid: `${key}_${id}`,
    name: labels[id] || name,
    labels: ['Entity', ...nodeLabels],
    attributes: {
      region: key,
      color: GRAPH_COLORS[nodeLabels[0]] || GRAPH_COLORS.Entity,
    },
  }))

  const edges = GRAPH_EDGES.map(([source, target, name], index) => ({
    uuid: `${key}_edge_${index + 1}`,
    source_node_uuid: `${key}_${source}`,
    target_node_uuid: `${key}_${target}`,
    name,
    fact_type: name,
  }))

  const addEdge = (source, target, name) => {
    edges.push({
      uuid: `${key}_edge_${edges.length + 1}`,
      source_node_uuid: source,
      target_node_uuid: target,
      name,
      fact_type: name,
    })
  }

  GRAPH_CLUSTER_SPECS.forEach((spec) => {
    for (let index = 0; index < spec.count; index += 1) {
      const nodeUuid = `${key}_${spec.anchor}_cluster_${String(index + 1).padStart(2, '0')}`
      const previousUuid = index > 0
        ? `${key}_${spec.anchor}_cluster_${String(index).padStart(2, '0')}`
        : null

      nodes.push({
        uuid: nodeUuid,
        name: clusterNouns[spec.anchor]
          ? `${clusterNouns[spec.anchor]} ${String(index + 1).padStart(2, '0')}`
          : spec.nameFactory({ countryLabel, city, labels }, index),
        labels: ['Entity', spec.label],
        attributes: {
          region: key,
          color: GRAPH_COLORS[spec.label] || GRAPH_COLORS.Entity,
        },
      })

      addEdge(nodeUuid, `${key}_${spec.anchor}`, spec.relations[0])
      addEdge(nodeUuid, `${key}_${spec.secondary[index % spec.secondary.length]}`, spec.relations[1])

      if (previousUuid) {
        addEdge(previousUuid, nodeUuid, spec.relations[2])
      }

      if (index % 4 === 0) {
        addEdge(nodeUuid, `${key}_${spec.cross[Math.floor(index / 4) % spec.cross.length]}`, spec.relations[0])
      }
    }
  })

  return {
    nodes,
    edges,
    node_count: nodes.length,
    edge_count: edges.length,
  }
}

function createPack({
  key,
  countryCode,
  countryLabel,
  city,
  seedLabel,
  defaultScenario,
  graphLabels,
  graphClusterNouns,
  graphLogs,
  populationNotes,
  topicSeeds,
  personas,
  simulationLogs,
  simulationActions,
  cascadeTails,
  reportTitle,
  reportSummary,
  reportSections,
  reportWorkbench,
  interactionLogs,
  reportAgentMessages,
  reportAgentAnswers,
  interviewAgents,
}) {
  const graphData = createGraphData(key, {
    countryLabel,
    city,
    clusterNouns: graphClusterNouns || {},
    labels: {
      commodity: `${countryLabel} staple price shock`,
      dhaka: city,
      ...graphLabels,
    },
  })

  return {
    key,
    countryCode,
    countryLabel,
    intake: {
      seedLabel,
      defaultScenario,
      readinessLine: `System is ready to stage a ${countryLabel}-grounded public response simulation.`,
    },
    graph: {
      graphData,
      entityTypes: ['GovernmentAgency', 'MediaOutlet', 'Person', 'Organization', 'Location'],
      relationTypes: ['ANNOUNCES', 'TRIGGERS', 'PRESSURES', 'AMPLIFIES', 'ECHOES', 'HOSTS'],
      stats: {
        nodes: graphData.node_count,
        edges: graphData.edge_count,
        types: 5,
      },
      logs: graphLogs,
    },
    population: {
      runId: `demo_${key}_run`,
      graphId: `demo_${key}_graph`,
      simulationId: `demo_${key}_sim`,
      notes: populationNotes,
      // Optional per-pack interest topics for generated personas. Without them
      // the shared price-shock topic list applies, which reads oddly on a pack
      // about data packs or hospital beds.
      topicSeeds: topicSeeds || null,
      personas,
      logs: [
        `Load country priors for ${countryLabel}.`,
        `Assemble audience clusters for ${city}.`,
        'Generate persona seeds for the full demo population.',
        `Lock environment configuration before launch.`,
      ],
    },
    simulation: {
      communityA: { name: 'Info Plaza', rounds: 40, acts: 276 },
      communityB: { name: 'Topic Community', rounds: 40, acts: 456 },
      actions: simulationActions,
      // Optional per-pack filler lines for generated cascade actions.
      cascadeTails: cascadeTails || null,
      logs: simulationLogs,
    },
    report: {
      title: reportTitle,
      summary: reportSummary,
      sections: reportSections,
      workbench: reportWorkbench,
      logs: [
        'Planning outline...',
        'Running quick search against active memory...',
        'Compiling section draft...',
        'Report package ready.',
      ],
    },
    interaction: {
      logs: interactionLogs,
      reportAgentMessages,
      // Keyword-hooked answers for the report agent. Packs that omit these fall
      // back to the shared price-shock wording in demoRuntime.
      reportAgentAnswers: reportAgentAnswers || null,
      interviewAgents,
    },
  }
}

export const DEMO_PACKS = {
  bangladesh: createPack({
    key: 'bangladesh',
    countryCode: 'BD',
    countryLabel: 'Bangladesh',
    city: 'Dhaka',
    seedLabel: 'Bangladesh Rice Price Shock Brief.pdf',
    defaultScenario:
      'Rice rises 40% before Eid in Dhaka. How do low-income households, student pages, and bazaar rumor chains respond?',
    graphLabels: {
      gov_notice: 'Commerce Ministry Notice',
      bazaar: 'Dhaka Bazaar Rumor Chain',
      students: 'Campus Facebook Pages',
      remittance: 'Remittance Households',
      workers: 'Gazipur Garment Workers',
      mosque: 'Neighbourhood Mosque Network',
      relief: 'Relief Office',
      media: 'Bangla News Pages',
      grocers: 'Neighbourhood Grocers',
      mothers: 'Women in Queue',
    },
    graphLogs: [
      'Scenario brief ingested from Bangladesh demo pack.',
      'Commerce Ministry notice extracted as institutional seed.',
      'Rumor chain, student pages, and remittance households linked into the graph.',
      'Scenario graph ready for population setup.',
    ],
    populationNotes: [
      'Low-income households that absorb first and complain last.',
      'Student pages that convert grievance into sharable narrative.',
      'Neighbourhood rumor relays that move faster than official clarification.',
    ],
    personas: [
      { name: 'Halima', role: 'Fish drying worker', detail: 'Noakhali -> Dhaka remittance household', trait: 'Absorbs shock silently' },
      { name: 'Rafi', role: 'Student admin', detail: 'Runs a campus grievance page', trait: 'Amplifies procedural anger' },
      { name: 'Shila', role: 'Garment worker', detail: 'Tracks prices through market calls home', trait: 'Cuts food before posting' },
      { name: 'Imam Harun', role: 'Local imam', detail: 'Filters official language into community speech', trait: 'Legitimizes or cools rumor' },
    ],
    simulationLogs: [
      'Stage 1: Household rationing begins.',
      'Stage 2: Student pages frame the issue as institutional neglect.',
      'Stage 3: Bazaar rumor chains outrun the first official clarification.',
      'Stage 4: Relief delay hardens distrust.',
    ],
    simulationActions: [
      { id: 'bd1', platform: 'plaza', actor: 'Halima', role: 'Fish drying worker', kind: 'Silent adjustment', text: 'Cuts household rice portions before telling her husband anything.', round: 'R04', time: '01:20' },
      { id: 'bd2', platform: 'community', actor: 'Rafi', role: 'Student admin', kind: 'Post', text: 'Campus page frames the shock as another decision made without listening to ordinary people.', round: 'R09', time: '02:10' },
      { id: 'bd3', platform: 'plaza', actor: 'Grocer', role: 'Neighbourhood grocer', kind: 'Price board update', text: 'The new market board photo gets forwarded before the official notice is understood.', round: 'R15', time: '03:05' },
      { id: 'bd4', platform: 'community', actor: 'Imam Harun', role: 'Local imam', kind: 'Voice message', text: 'Calls for calm but acknowledges that people are already skipping meals.', round: 'R22', time: '04:40' },
      { id: 'bd5', platform: 'plaza', actor: 'Shila', role: 'Garment worker', kind: 'Dorm chat', text: 'Dormitory groups discuss delaying remittances home because food costs spiked first.', round: 'R31', time: '05:30' },
      { id: 'bd6', platform: 'community', actor: 'News page', role: 'Bangla media page', kind: 'Repost', text: 'Media pages amplify queue photos and relief rumours at the same time.', round: 'R40', time: '06:45' },
    ],
    reportTitle: 'Pre-Eid Rice Price Shock in Dhaka: Forecast Report on Household Strain, Rumor Spread, and Institutional Trust',
    reportSummary:
      'The simulated response does not begin with outrage. It begins with rationing, silence, and improvised household math, then spreads outward through student pages and bazaar rumor chains before official reassurance catches up.',
    reportSections: BANGLADESH_REPORT.reportSections,
    reportAgentAnswers: BANGLADESH_REPORT.reportAgentAnswers,
    reportWorkbench: [
      { label: 'Planning', title: 'Outline', detail: 'Cascade phases, segment breakdown, the silence lane, amplifier profiles, trust map, dashboard warning, recommendations.' },
      { label: 'Quick Search', title: 'Active memories', detail: 'Price board photos, queue language, remittance household stress, Eid timing.' },
      { label: 'Agent Interview', title: 'Population check', detail: 'Silent coping among women managing food persists longer than visible complaint.' },
      { label: 'Complete', title: 'Report ready', detail: 'Bangladesh report assembled and ready for review.' },
    ],
    interactionLogs: [
      'Open report-agent conversation.',
      'Load four interviewable public personas.',
      'Survey prompt bank ready.',
    ],
    reportAgentMessages: [
      { role: 'assistant', text: 'The earliest signal is not public anger. It is rationing inside the household.' },
      { role: 'user', text: 'What makes the issue spread publicly?' },
      { role: 'assistant', text: 'Student Facebook pages and bazaar rumor chains translate private strain into a legitimacy narrative.' },
    ],
    interviewAgents: BANGLADESH_REPORT.interviewAgents,
  }),
  india: createPack({
    key: 'india',
    countryCode: 'IN',
    countryLabel: 'India',
    city: 'Gaya',
    seedLabel: 'Bihar Wheat Price Brief.pdf',
    defaultScenario:
      'Wheat prices jump before a festival week in Bihar. How do ration lines, women health volunteers, and family WhatsApp groups respond?',
    graphLabels: {
      gov_notice: 'State Food Notice',
      commodity: 'Wheat Price Shock',
      bazaar: 'Ration Queue Gossip',
      students: 'District WhatsApp Pages',
      remittance: 'Migrant Worker Households',
      workers: 'ASHA Volunteers',
      mosque: 'Ward Elders Network',
      relief: 'Fair Price Shop Office',
      media: 'Hindi Local Media',
      grocers: 'Village Grocers',
      mothers: 'Women at the Ration Shop',
    },
    graphLogs: [
      'Bihar price-shock scenario loaded.',
      'Ration queue signals extracted as local amplification path.',
      'Volunteer health workers added as high-trust connectors.',
      'District graph ready for demo population setup.',
    ],
    populationNotes: [
      'Households where women manage both care labour and ration queues.',
      'Migratory households dependent on irregular transfers.',
      'District message relays that travel through WhatsApp before formal clarification.',
    ],
    personas: [
      { name: 'Phulwanti', role: 'ASHA volunteer', detail: 'Gaya district care worker', trait: 'Keeps serving while food cost rises' },
      { name: 'Sanjay', role: 'Migrant son', detail: 'Sends money home from Surat', trait: 'Hides instability from family' },
      { name: 'Rekha', role: 'Queue organizer', detail: 'Tracks ration stock rumours', trait: 'Translates scarcity into urgency' },
      { name: 'Ward teacher', role: 'Schoolteacher', detail: 'Local signal spreader', trait: 'Legitimizes information' },
    ],
    simulationLogs: [
      'Ration line anxiety forms before public accusation.',
      'WhatsApp screenshots accelerate queue panic.',
      'Volunteer networks become trusted explanation nodes.',
      'Delayed stock clarity becomes institutional blame.',
    ],
    simulationActions: [
      { id: 'in1', platform: 'plaza', actor: 'Phulwanti', role: 'ASHA volunteer', kind: 'Field note', text: 'She starts visiting homes and hears the same question at every stop: will the ration shop open full stock tomorrow?', round: 'R05', time: '01:10' },
      { id: 'in2', platform: 'community', actor: 'Rekha', role: 'Queue organizer', kind: 'Forward', text: 'A photo of a half-empty ration shelf is forwarded through local groups before anyone verifies it.', round: 'R11', time: '02:00' },
      { id: 'in3', platform: 'plaza', actor: 'Sanjay', role: 'Migrant son', kind: 'Private call', text: 'He promises to send extra money but does not admit his own wages were cut.', round: 'R20', time: '03:25' },
      { id: 'in4', platform: 'community', actor: 'Ward teacher', role: 'Schoolteacher', kind: 'Clarification post', text: 'Posts the official explanation, but the line outside the shop is already too long to calm.', round: 'R33', time: '05:12' },
    ],
    reportTitle: 'Festival-Week Wheat Shock in Bihar: Forecast Report on Ration Anxiety, Volunteer Mediation, and Queue Panic',
    reportSummary:
      'The simulated response shows that ration anxiety spreads through local queue evidence and family groups before formal reassurance. Health volunteers become critical trust translators, but not fast enough to prevent panic.',
    reportSections: [
      { title: 'Scarcity becomes visible through the queue', paragraphs: ['The first public signal is not the government notice itself. It is the sight of people arriving early and seeing stock uncertainty with their own eyes.', 'That visual uncertainty is then recoded as certainty through screenshots and retellings.'] },
      { title: 'Volunteer women become trust infrastructure', paragraphs: ['ASHA-style local workers absorb questions that formal channels cannot answer quickly.', 'Because they are known personally, they carry more persuasive weight than distant administrative language.'] },
      { title: 'Relief clarity loses ground to rumor speed', paragraphs: ['By the time the official explanation arrives, the social fact of scarcity has already been constructed.', 'Institutional blame grows not only from shortage but from timing.'] },
    ],
    reportWorkbench: [
      { label: 'Planning', title: 'Outline', detail: 'Ration queue, trust relay, delayed reassurance.' },
      { label: 'Quick Search', title: 'Household memories', detail: 'Festival week, wage irregularity, volunteer care labor.' },
      { label: 'Agent Interview', title: 'Volunteer check', detail: 'Care workers absorb questions that policy copy cannot answer.' },
      { label: 'Complete', title: 'Report ready', detail: 'India report assembled and ready for review.' },
    ],
    interactionLogs: ['Load Bihar report thread.', 'Load interviewable district personas.', 'Survey prompt bank ready.'],
    reportAgentMessages: [
      { role: 'assistant', text: 'In this scenario, the line outside the ration shop matters more than the text of the notice.' },
      { role: 'user', text: 'Who stabilizes the response?' },
      { role: 'assistant', text: 'Volunteer women and known local workers act as informal trust infrastructure.' },
    ],
    interviewAgents: [
      // Possessive "her" cannot survive retargetPronouns, so this reads "the
      // rounds" rather than "her rounds". Same reason as the note in bdbrand.
      { name: 'Phulwanti', role: 'ASHA volunteer', response: 'She continues the daily rounds while answering food questions she was never formally assigned to handle.' },
      { name: 'Rekha', role: 'Queue organizer', response: 'She is one of the first people to convert uncertainty into urgency for everyone else.' },
      { name: 'Sanjay', role: 'Migrant son', response: 'He protects family morale with half-truths about money and availability.' },
    ],
  }),
  pakistan: createPack({
    key: 'pakistan',
    countryCode: 'PK',
    countryLabel: 'Pakistan',
    city: 'Faisalabad',
    seedLabel: 'Atta Shock Brief - Faisalabad.pdf',
    defaultScenario:
      'Flour prices jump in Faisalabad with no immediate relief plan. How do home-based women workers, factory households, and mosque WhatsApp groups respond?',
    graphLabels: {
      gov_notice: 'Punjab Relief Notice',
      commodity: 'Atta Price Shock',
      bazaar: 'Neighborhood WhatsApp Rumor',
      students: 'Political Meme Pages',
      remittance: 'Factory Wage Households',
      workers: 'Home-based Embroidery Workers',
      mosque: 'Masjid WhatsApp Admins',
      relief: 'Utility Store Desk',
      media: 'Urdu Local Media',
      grocers: 'Flour Sellers',
      mothers: 'Women Running the Kitchen',
    },
    graphLogs: [
      'Punjab atta shock scenario loaded.',
      'Home-based women workers added as silent pressure points.',
      'WhatsApp mosque admins added as local legitimacy relays.',
      'Faisalabad demo graph ready.',
    ],
    populationNotes: [
      'Households where women manage food without public political speech.',
      'Factory households living under visible price pressure and hidden partisan anxiety.',
      'WhatsApp groups that route rumor through piety and practical information together.',
    ],
    personas: [
      { name: 'Nasreen', role: 'Embroidery worker', detail: 'Home-based income manager', trait: 'Signals distress through implication, not declaration' },
      { name: 'Bilal', role: 'Power loom worker', detail: 'Factory wage earner', trait: 'Measures shock through evening food cuts' },
      { name: 'Imran', role: 'WhatsApp admin', detail: 'Masjid information relay', trait: 'Packages rumor as caution' },
      { name: 'Rabia', role: 'Neighbor organizer', detail: 'Kitchen supply tracker', trait: 'Translates stress into household gossip' },
    ],
    simulationLogs: [
      'Household food math tightens before overt complaint.',
      'Relief rumours spread through mosque-linked groups.',
      'Practical questions outrun political speech.',
      'Kitchen strain becomes distrust of promised support.',
    ],
    simulationActions: [
      { id: 'pk1', platform: 'plaza', actor: 'Nasreen', role: 'Embroidery worker', kind: 'Private message', text: 'She asks three women quietly whether anyone has heard about relief before she says anything political.', round: 'R06', time: '01:12' },
      { id: 'pk2', platform: 'community', actor: 'Imran', role: 'WhatsApp admin', kind: 'Forwarded note', text: 'A mosque group circulates caution about prices and possible utility-store distribution.', round: 'R12', time: '02:35' },
      { id: 'pk3', platform: 'plaza', actor: 'Bilal', role: 'Power loom worker', kind: 'Household adjustment', text: 'The evening roti count drops before the household speaks publicly about inflation.', round: 'R21', time: '03:55' },
      { id: 'pk4', platform: 'community', actor: 'Rabia', role: 'Neighbor organizer', kind: 'Voice note', text: 'Kitchen gossip turns into a neighborhood warning faster than official clarification arrives.', round: 'R34', time: '05:48' },
    ],
    reportTitle: 'Faisalabad Atta Shock: Forecast Report on Kitchen Strain, WhatsApp Rumor, and Relief Distrust',
    reportSummary:
      'The simulation shows that practical household strain precedes explicit political complaint. Relief rumors move through trusted religious and neighborhood channels, shaping response before official messaging catches up.',
    reportSections: [
      { title: 'Kitchen stress precedes visible speech', paragraphs: ['Food reduction begins at home, especially among women managing both earnings and meal planning.', 'The emotional signature is contained strain rather than open declaration.'] },
      { title: 'WhatsApp and mosque relays set the tempo', paragraphs: ['Rumor travels through trusted social administrators who package it as caution and mutual help.', 'That makes the message harder to dislodge once it has spread.'] },
      { title: 'Relief trust erodes through delay', paragraphs: ['The issue becomes not only price itself but whether support promises were ever real.', 'Delay transforms uncertainty into a judgment about institutional reliability.'] },
    ],
    reportWorkbench: [
      { label: 'Planning', title: 'Outline', detail: 'Kitchen strain, relay networks, relief trust.' },
      { label: 'Quick Search', title: 'Household fragments', detail: 'Roti count, piety language, relief rumor, utility store.' },
      { label: 'Agent Interview', title: 'Household check', detail: 'Women ask practical questions before they speak politically.' },
      { label: 'Complete', title: 'Report ready', detail: 'Pakistan report assembled and ready for review.' },
    ],
    interactionLogs: ['Load Faisalabad report thread.', 'Load interviewable household personas.', 'Survey prompt bank ready.'],
    reportAgentMessages: [
      { role: 'assistant', text: 'The response begins in the kitchen, not on the timeline.' },
      { role: 'user', text: 'Why does rumor outrun official messaging?' },
      { role: 'assistant', text: 'Because the trusted relay is the person already inside the household network, not the institution outside it.' },
    ],
    interviewAgents: [
      { name: 'Nasreen', role: 'Embroidery worker', response: 'She asks about relief quietly, then reduces food before naming the scale of the problem aloud.' },
      { name: 'Imran', role: 'WhatsApp admin', response: 'He packages rumor as caution and therefore makes it socially acceptable to circulate.' },
      { name: 'Rabia', role: 'Neighbor organizer', response: 'She turns kitchen concern into neighborhood certainty.' },
    ],
  }),
  srilanka: createPack({
    key: 'srilanka',
    countryCode: 'LK',
    countryLabel: 'Sri Lanka',
    city: 'Nuwara Eliya',
    seedLabel: 'Estate Rice Shock Brief.pdf',
    defaultScenario:
      'Rice prices rise sharply in the hill country. How do estate households, migrant daughters, and local union talk respond before formal relief appears?',
    graphLabels: {
      gov_notice: 'Cabinet Cost Notice',
      bazaar: 'Estate Line-Room Talk',
      students: 'Youth Facebook Pages',
      remittance: 'Garment-Factory Transfers',
      workers: 'Tea Estate Workers',
      mosque: 'Temple and church relays',
      relief: 'Divisional Secretariat',
      media: 'Tamil and Sinhala local media',
      grocers: 'Estate Grocers',
      mothers: 'Estate Mothers',
    },
    graphLogs: [
      'Hill-country rice shock scenario loaded.',
      'Estate household pressure mapped into the graph.',
      'Migrant transfer nodes linked to household coping.',
      'Nuwara Eliya demo graph ready.',
    ],
    populationNotes: [
      'Estate households with little slack and inherited powerlessness.',
      'Families dependent on small transfers from daughters in factories.',
      'Local conversations that name despair long before anger.',
    ],
    personas: [
      { name: 'Selvamani', role: 'Tea plucker', detail: 'Estate household manager', trait: 'Responds with despair before protest' },
      { name: 'Tharshi', role: 'Factory daughter', detail: 'Sends small transfers home', trait: 'Extends household endurance remotely' },
      { name: 'Union rep', role: 'Estate organizer', detail: 'Translates despair into demands', trait: 'Slowly collectivizes grievance' },
      { name: 'Grocer', role: 'Estate grocer', detail: 'Daily price witness', trait: 'Makes shortage visible' },
    ],
    simulationLogs: [
      'Household despair appears before organized complaint.',
      'Transfer-dependent families attempt to stretch remittance first.',
      'Estate talk spreads through repeated arithmetic of food costs.',
      'Late relief notice deepens inherited distrust.',
    ],
    simulationActions: [
      { id: 'lk1', platform: 'plaza', actor: 'Selvamani', role: 'Tea plucker', kind: 'Household math', text: 'She recalculates rice against wages and realizes the numbers do not resolve.', round: 'R05', time: '01:18' },
      { id: 'lk2', platform: 'community', actor: 'Grocer', role: 'Estate grocer', kind: 'Counter talk', text: 'Every purchase becomes a public measure of what a day of labor can no longer buy.', round: 'R13', time: '02:44' },
      { id: 'lk3', platform: 'plaza', actor: 'Tharshi', role: 'Factory daughter', kind: 'Transfer promise', text: 'She promises another small transfer but knows the amount will not close the gap.', round: 'R24', time: '04:05' },
      { id: 'lk4', platform: 'community', actor: 'Union rep', role: 'Estate organizer', kind: 'Meeting note', text: 'Despair becomes organized language only after households have already absorbed the first shock.', round: 'R36', time: '06:00' },
    ],
    reportTitle: 'Hill-Country Rice Shock: Forecast Report on Estate Despair, Transfer Dependence, and Delayed Relief',
    reportSummary:
      'The simulated response centers on despair and arithmetic rather than fast outrage. Estate households absorb the shock first, then slowly translate it into organized demand through local trust networks.',
    reportSections: [
      { title: 'The first reaction is arithmetic, not speech', paragraphs: ['Estate households respond first by checking what a day of work still buys.', 'That arithmetic produces despair before it produces a public argument.'] },
      { title: 'Transfer dependence buys time, not safety', paragraphs: ['Small remittances from migrant daughters extend endurance but do not resolve the shortage.', 'They delay open crisis while deepening household strain.'] },
      { title: 'Organization arrives after absorption', paragraphs: ['By the time relief or union language appears, the first shock has already been privately borne.', 'The delay shapes response as distrust rather than gratitude.'] },
    ],
    reportWorkbench: [
      { label: 'Planning', title: 'Outline', detail: 'Arithmetic, remittance stretch, slow organization.' },
      { label: 'Quick Search', title: 'Active memories', detail: 'Rice math, line-room talk, transfer dependence, relief delay.' },
      { label: 'Agent Interview', title: 'Household check', detail: 'Despair is the correct first emotion in this pack.' },
      { label: 'Complete', title: 'Report ready', detail: 'Sri Lanka report assembled and ready for review.' },
    ],
    interactionLogs: ['Load Sri Lanka report thread.', 'Load estate household interview set.', 'Survey prompt bank ready.'],
    reportAgentMessages: [
      { role: 'assistant', text: 'In this scenario, despair arrives before anger because arithmetic arrives before rhetoric.' },
      { role: 'user', text: 'What changes the issue from private to public?' },
      { role: 'assistant', text: 'Repeated visible proof at the grocer and later translation by organized intermediaries.' },
    ],
    interviewAgents: [
      { name: 'Selvamani', role: 'Tea plucker', response: 'She experiences the shock first as impossible arithmetic inside the household.' },
      { name: 'Tharshi', role: 'Factory daughter', response: 'She can delay crisis but cannot solve it from afar.' },
      { name: 'Union rep', role: 'Estate organizer', response: 'He turns quiet despair into collective language only after absorption has already happened.' },
    ],
  }),
  nepal: createPack({
    key: 'nepal',
    countryCode: 'NP',
    countryLabel: 'Nepal',
    city: 'Sindhupalchok',
    seedLabel: 'Remittance Household Food Shock Brief.pdf',
    defaultScenario:
      'Food prices rise across remittance-dependent households in Sindhupalchok. How do wives managing the household, local volunteers, and village rumor paths respond?',
    graphLabels: {
      gov_notice: 'District Price Notice',
      bazaar: 'Village Rumor Path',
      students: 'Youth Messenger Groups',
      remittance: 'Qatar-linked Households',
      workers: 'FCHV Volunteers',
      mosque: 'Ward elder network',
      relief: 'Municipal Relief Desk',
      media: 'Nepali Local Media',
      grocers: 'Village Shopkeepers',
      mothers: 'Women Managing the Household',
    },
    graphLogs: [
      'Sindhupalchok remittance household scenario loaded.',
      'Village shop and volunteer networks added as signal relays.',
      'Qatar-linked households mapped as fragile stabilizers.',
      'Nepal demo graph ready.',
    ],
    populationNotes: [
      'Households where women run the farm, school payments, medicine, and debt servicing.',
      'Remittance households whose transfers buy time but not certainty.',
      'Local volunteers who become trusted interpreters of risk.',
    ],
    personas: [
      { name: 'Kalpana', role: 'Farmer and volunteer', detail: 'Sindhupalchok household manager', trait: 'Absorbs instability before reporting it' },
      { name: 'Milan', role: 'Village shopkeeper', detail: 'Local price signal source', trait: 'Makes inflation visible every day' },
      { name: 'Anju', role: 'Health volunteer', detail: 'Known community messenger', trait: 'Carries difficult news softly' },
      { name: 'Suresh', role: 'Migrant husband', detail: 'Qatar wage worker', trait: 'Believes transfer solves more than it does' },
    ],
    simulationLogs: [
      'Household managers absorb shock before they disclose it.',
      'Village shop prices create the first shared public evidence.',
      'Volunteer trust networks carry explanation faster than policy copy.',
      'Remittance confidence weakens as transfers stop covering the gap.',
    ],
    simulationActions: [
      { id: 'np1', platform: 'plaza', actor: 'Kalpana', role: 'Farmer and volunteer', kind: 'Household delay', text: 'She postpones a school purchase and says nothing to her husband on the evening call.', round: 'R07', time: '01:25' },
      { id: 'np2', platform: 'community', actor: 'Milan', role: 'Shopkeeper', kind: 'Counter conversation', text: 'The shop becomes the first place where the shock is made public through everyday pricing.', round: 'R14', time: '02:42' },
      { id: 'np3', platform: 'plaza', actor: 'Anju', role: 'Health volunteer', kind: 'Quiet explanation', text: 'She explains the price change gently, but hears fear about debt in every conversation.', round: 'R23', time: '03:58' },
      { id: 'np4', platform: 'community', actor: 'Suresh', role: 'Migrant husband', kind: 'Voice message', text: 'He promises the next transfer will settle things, not realizing the household has already started cutting essentials.', round: 'R35', time: '05:51' },
    ],
    reportTitle: 'Sindhupalchok Food Shock: Forecast Report on Remittance Strain, Household Silence, and Village Trust Relays',
    reportSummary:
      'The response is driven by women who absorb instability before naming it, village shop prices that make the issue public, and trusted volunteers who explain a crisis that remittance money can no longer fully contain.',
    reportSections: [
      { title: 'Silence is the first coping mechanism', paragraphs: ['Household managers absorb the first wave of the shock privately through delay, substitution, and omission.', 'This silence is practical, not passive. It is an active management strategy.'] },
      { title: 'Village shops make the shock visible', paragraphs: ['The shock becomes socially real at the counter, where everyone sees the same change but interprets it through different burdens.', 'That shared visual evidence matters more than official language in the first phase.'] },
      { title: 'Remittance confidence weakens', paragraphs: ['Transfers still matter, but the belief that they can solve the problem erodes quickly.', 'That gap between expectation and household reality becomes a trust problem as well as an economic one.'] },
    ],
    reportWorkbench: [
      { label: 'Planning', title: 'Outline', detail: 'Household silence, public pricing, remittance strain.' },
      { label: 'Quick Search', title: 'Active memories', detail: 'Debt, school delay, medicine, village shop evidence.' },
      { label: 'Agent Interview', title: 'Household check', detail: 'Silence here is workload, not disengagement.' },
      { label: 'Complete', title: 'Report ready', detail: 'Nepal report assembled and ready for review.' },
    ],
    interactionLogs: ['Load Nepal report thread.', 'Load interviewable remittance-household personas.', 'Survey prompt bank ready.'],
    reportAgentMessages: [
      { role: 'assistant', text: 'The earliest reaction is household management through silence, not visible protest.' },
      { role: 'user', text: 'What makes the issue public?' },
      { role: 'assistant', text: 'Shared price evidence at the village shop and trusted interpretation by local volunteers.' },
    ],
    interviewAgents: [
      { name: 'Kalpana', role: 'Farmer and volunteer', response: 'She hides the first consequences from the spouse abroad, because keeping the household functioning is the job.' },
      { name: 'Milan', role: 'Shopkeeper', response: 'He is where private struggle becomes a visible public fact.' },
      { name: 'Anju', role: 'Health volunteer', response: 'She explains risk in language that people trust more than official copy.' },
    ],
  }),

  // Brand-crisis pack for agency audiences. Rongdhonu Noodles is invented for
  // this demo; the scenario shape echoes the 2015 regional instant-noodle
  // safety scare, but no real brand is named anywhere in it.
  bdbrand: createPack({
    key: 'bdbrand',
    countryCode: 'BD-BRAND',
    countryLabel: 'Bangladesh',
    city: 'Dhaka',
    seedLabel: 'Rongdhonu Noodles - Eid Campaign Crisis Brief (fictional brand).pdf',
    defaultScenario:
      'A contamination rumour hits Rongdhonu Noodles during Eid campaign week. How do mothers groups, retailers, and meme pages respond, and who quietly stops buying?',
    graphLabels: {
      gov_notice: 'BSTI Test Notice',
      commodity: 'Rongdhonu Contamination Rumour',
      bazaar: 'Bazaar and Teashop Talk',
      students: 'Campus and Meme Pages',
      remittance: 'Young Family Households',
      workers: 'Office Tiffin Groups',
      mosque: 'Community Group Admins',
      relief: 'Rongdhonu Response Desk',
      media: 'Bangla Health and News Pages',
      grocers: 'Mudi Dokan Retailers',
      mothers: 'School Mother Groups',
    },
    graphClusterNouns: {
      students: 'Dhaka meme page',
      media: 'Bangla health page',
      remittance: 'Dhaka young family',
      workers: 'Dhaka tiffin group',
      mothers: 'Dhaka school-mother group',
      bazaar: 'Dhaka teashop thread',
      grocers: 'Dhaka mudi dokan',
      gov_notice: 'BSTI circular',
      relief: 'Rongdhonu response desk',
      dhaka: 'Dhaka ward',
    },
    graphLogs: [
      'Campaign brief and rumour screenshots ingested from the brand crisis pack.',
      'Rongdhonu Noodles registered as the campaign entity under scrutiny.',
      'Mother groups, mudi dokan retailers, and meme pages linked as distinct lanes.',
      'Scenario graph ready for population setup.',
    ],
    populationNotes: [
      'Households that stop buying quietly and never post a complaint.',
      'Mudi dokan retailers who see demand fall before any statement is issued.',
      'Group admins and meme pages that decide how fast a screenshot travels.',
    ],
    personas: [
      { name: 'Sharmin', role: 'School-group mother', detail: 'Packs a tiffin box every morning', trait: 'Removes the product before saying anything' },
      { name: 'Kamrul', role: 'Mudi dokan owner', detail: 'Runs a para grocery in Mirpur', trait: 'Reads demand off the shelf, not the news' },
      { name: 'Tanvir', role: 'Meme page admin', detail: 'Runs a campus humour page', trait: 'Turns a batch number into a joke that travels' },
      { name: 'Nasrin', role: 'Garment floor supervisor', detail: 'Buys in bulk for a shared kitchen', trait: 'Switches brand without announcing it' },
    ],
    simulationLogs: [
      'Seeding Eid campaign posts and the first rumour screenshot.',
      'Running mother groups, retail lane, and meme pages in parallel.',
      'Tracking silent substitution against visible complaint.',
      'Cascade complete across both communities.',
    ],
    simulationActions: [
      { id: 'bb1', platform: 'community', actor: 'Sharmin', role: 'School-group mother', kind: 'Group message', text: 'Apuu, ei noodles ta ki bacchader tiffin e deya thik hobe? Ekta screenshot dekhlam, batch number soho. Bhoy lagche.', round: 'R02', time: '00:40' },
      { id: 'bb2', platform: 'plaza', actor: 'Rongdhonu', role: 'Brand campaign page', kind: 'Campaign post', text: 'Eid er khushi, ek plate e. Rongdhonu Noodles er notun Eid campaign live. (Scheduled post, published forty minutes after the first screenshot.)', round: 'R04', time: '01:05' },
      { id: 'bb3', platform: 'community', actor: 'Group admin', role: 'Community group admin', kind: 'Forward', text: 'ভাই, ব্যাচ নম্বরটা দেখেন। কেউ কনফার্ম করতে পারলে জানান। আপাতত বাচ্চাদের না দেওয়াই ভালো।', round: 'R07', time: '01:50' },
      { id: 'bb4', platform: 'plaza', actor: 'Tanvir', role: 'Meme page admin', kind: 'Meme post', text: 'Eid er khushi ek plate e, lead o ek plate e. Batch number ta comment e dilam. (The joke reaches more people in two hours than the campaign did in two days.)', round: 'R11', time: '02:35' },
      { id: 'bb5', platform: 'community', actor: 'Kamrul', role: 'Mudi dokan owner', kind: 'Retailer signal', text: 'Ei week e tin carton porei ache. Keu chaitese na, kintu keu jigges o kortese na. Customer chupchap onno brand nite jaitese.', round: 'R15', time: '03:20' },
      { id: 'bb6', platform: 'plaza', actor: 'Nasrin', role: 'Garment floor supervisor', kind: 'Silent adjustment', text: 'Buys a different brand at the bazaar on the way home and says nothing to anyone. No post, no comment, no complaint. The switch is invisible to every dashboard.', round: 'R19', time: '04:10' },
      { id: 'bb7', platform: 'community', actor: 'Teashop table', role: 'Bazaar and teashop talk', kind: 'Offline relay', text: 'Cha er dokane ekjon bollo tar bhaginar school e naki notice diyeche. Keu link dekhe nai, kintu shobai bishwas kore fellcho.', round: 'R24', time: '05:05' },
      { id: 'bb8', platform: 'plaza', actor: 'BSTI notice', role: 'Regulator', kind: 'Test notice', text: 'A sample-testing notice is issued. The wording is procedural and gives no verdict, so both sides read it as proof of their own position.', round: 'R28', time: '06:00' },
      { id: 'bb9', platform: 'plaza', actor: 'Rongdhonu', role: 'Brand response desk', kind: 'Clarification', text: 'Brand issues an English-language statement citing compliance certificates. It circulates among middle-class pages and does not enter the mother groups at all.', round: 'R33', time: '06:50' },
      { id: 'bb10', platform: 'community', actor: 'Kamrul', role: 'Mudi dokan owner', kind: 'Trade outcome', text: 'Statement er por o order kori nai. Ami wait kortesi. Customer fire ashle tokhon anbo, ager moto na.', round: 'R38', time: '07:40' },
    ],
    cascadeTails: [
      'The screenshot arrives before anyone has checked whether it is real.',
      'Nobody asks the shopkeeper why, they simply reach for the other packet.',
      'The joke travels further than the correction ever will.',
      'A group admin decides in one second how far this goes.',
      'The tiffin box changes before the opinion does.',
      'The campaign schedule keeps posting into a room that has already turned.',
    ],
    reportTitle: 'Contamination Rumour in Eid Campaign Week: Forecast Report on Silent Substitution, Retail Drag, and Split Trust Recovery',
    reportSummary:
      'The damage does not arrive as outrage. It arrives as a tiffin box packed with something else, a shelf that stops moving, and a clarification that reaches the segment that had already forgiven you.',
    reportSections: BDBRAND_REPORT.reportSections,
    reportWorkbench: [
      { label: 'Planning', title: 'Outline', detail: 'Cascade phases, segment breakdown, the silent substitution lane, amplifier profiles, trust map, dashboard warning, recommendations.' },
      { label: 'Quick Search', title: 'Active memories', detail: 'Tiffin box, batch number screenshot, mudi dokan reorder, Eid campaign calendar.' },
      { label: 'Agent Interview', title: 'Retail check', detail: 'Shopkeepers see the switch before the brand sees the sentiment.' },
      { label: 'Complete', title: 'Report ready', detail: 'Brand crisis report assembled and ready for review.' },
    ],
    interactionLogs: [
      'Load brand crisis report thread.',
      'Load interviewable mother, retailer, and page-admin personas.',
      'Survey prompt bank ready.',
    ],
    reportAgentMessages: [
      { role: 'assistant', text: 'The first loss is not reputation. It is a tiffin box quietly packed with another brand.' },
      { role: 'user', text: 'Where does the brand find out?' },
      { role: 'assistant', text: 'At the shelf. Retailers stop reordering before public sentiment moves enough to register.' },
    ],
    reportAgentAnswers: BDBRAND_REPORT.reportAgentAnswers,
    interviewAgents: BDBRAND_REPORT.interviewAgents,
  }),

  // Social-programme pack. Alor Shetu Foundation and the Mayer Hashi allowance
  // are invented for this demo. The silence lane is non-collection: mothers who
  // stop turning up rather than risk being told at the counter that they are off
  // the list.
  bdngo: createPack({
    key: 'bdngo',
    countryCode: 'BD-NGO',
    countryLabel: 'Bangladesh',
    city: 'Kurigram',
    seedLabel: 'Mayer Hashi Allowance - Re-registration Rumour Brief (fictional programme).pdf',
    defaultScenario:
      'A rumour says the Mayer Hashi maternal allowance is being cut and every mother must re-register with her NID. How do rural beneficiary mothers, field officers, and union gatekeepers respond, and who quietly stops collecting?',
    graphLabels: {
      gov_notice: 'Upazila Office Circular',
      commodity: 'Mayer Hashi Re-registration Rumour',
      bazaar: 'Ghat and Bazaar Talk',
      students: 'Dhaka Commentary Pages',
      remittance: 'Beneficiary Households',
      workers: 'Alor Shetu Field Officers',
      mosque: 'Union Gatekeepers',
      relief: 'Alor Shetu Help Desk',
      media: 'Bangla News and Fact Pages',
      grocers: 'Photocopy and NID Shops',
      mothers: 'Mothers Who Collect the Allowance',
    },
    graphClusterNouns: {
      students: 'Dhaka commentary page',
      media: 'Bangla news page',
      remittance: 'Kurigram beneficiary household',
      workers: 'Alor Shetu field officer',
      mothers: 'Kurigram collecting mother',
      bazaar: 'Kurigram ghat thread',
      grocers: 'Kurigram photocopy shop',
      gov_notice: 'Upazila circular',
      relief: 'Alor Shetu help desk',
      dhaka: 'Kurigram union',
    },
    graphLogs: [
      'Programme brief and forwarded voice notes ingested from the maternal allowance pack.',
      'Mayer Hashi allowance registered as the programme entity under rumour.',
      'Beneficiary mothers, field officers, and union gatekeepers linked as separate lanes.',
      'Scenario graph ready for population setup.',
    ],
    populationNotes: [
      'Mothers who stop collecting rather than ask a question they may be punished for.',
      'Field officers who learn about the drop from a register, never from a beneficiary.',
      'Union gatekeepers who can settle or spread a rumour in a single afternoon.',
    ],
    topicSeeds: [
      'maternal allowance',
      'NID re-registration',
      'disbursement day',
      'union parishad queue',
      'shomiti group talk',
      'field officer visits',
      'forwarded voice notes',
      'household cash flow',
      'programme trust',
      'photocopy shop queues',
      'ward gatekeepers',
      'names missing from the register',
    ],
    personas: [
      { name: 'Morjina', role: 'Beneficiary mother', detail: 'Collects the allowance at the union parishad', trait: 'Stops going before asking anyone' },
      { name: 'Sirajul', role: 'Field officer', detail: 'Covers nine villages for Alor Shetu', trait: 'Hears about the panic a month late' },
      { name: 'Anowara', role: 'Shomiti group leader', detail: 'Holds the group book for twenty mothers', trait: 'Decides what the group believes' },
      { name: 'Rafiqul', role: 'Union parishad member', detail: 'Signs the NID verification slips', trait: 'Turns a rumour into a queue' },
    ],
    simulationLogs: [
      'Seeding the forwarded voice note and the first re-registration claim.',
      'Running beneficiary households, field officers, and gatekeeper lanes in parallel.',
      'Tracking silent non-collection against visible protest at the union office.',
      'Cascade complete across both communities.',
    ],
    simulationActions: [
      { id: 'bn1', platform: 'community', actor: 'Anowara', role: 'Shomiti group leader', kind: 'Voice note', text: 'আপা, শুনলাম ভাতা নাকি বন্ধ হইয়া যাইতেছে। নতুন কইরা এনআইডি দিয়া নাম তুলতে হইব। যার নাম উঠব না, তার টাকা আর আইব না।', round: 'R02', time: '00:35' },
      { id: 'bn2', platform: 'plaza', actor: 'Union office', role: 'Union parishad desk', kind: 'Counter reply', text: 'Office theke bollo kono notice ashe nai. Kintu keu likhito kichu dilo na, tai keu bishwas korlo na.', round: 'R05', time: '01:10' },
      { id: 'bn3', platform: 'community', actor: 'Morjina', role: 'Beneficiary mother', kind: 'Silent adjustment', text: 'Ei mash e ar gelam na. Giya jodi shuni nam kata, tar cheye na jaowai bhalo. Karo ke bolio nai.', round: 'R08', time: '01:55' },
      { id: 'bn4', platform: 'plaza', actor: 'Dhaka page', role: 'Commentary page admin', kind: 'Post', text: 'A Dhaka page posts that the allowance is being cut, attaches a stock photo of a queue, and gets more reach in one evening than the programme has had all year.', round: 'R12', time: '02:40' },
      { id: 'bn5', platform: 'community', actor: 'Photocopy shop', role: 'NID photocopy shop owner', kind: 'Counter signal', text: 'Ek shoptahe eto NID photocopy age kono din kori nai. Shobai bolteche re-registration lagbe. Ami jani na lagbe kina, ami shudhu copy kore ditesi.', round: 'R16', time: '03:25' },
      { id: 'bn6', platform: 'plaza', actor: 'Rafiqul', role: 'Union parishad member', kind: 'Verification queue', text: 'He begins signing verification slips nobody asked him for, and the queue outside his room becomes the strongest proof available that the rumour is true.', round: 'R20', time: '04:15' },
      { id: 'bn7', platform: 'community', actor: 'Union office crowd', role: 'Protest group', kind: 'Group protest', text: 'Thirty mothers gather at the union office and demand a written notice. They are loud, they are counted, and they are the ones who never stopped collecting.', round: 'R25', time: '05:00' },
      { id: 'bn8', platform: 'plaza', actor: 'Sirajul', role: 'Field officer', kind: 'Field note', text: 'Ei mash er register e chollish jon kom. Keu phone kore nai, keu obhijog kore nai. Ami nijeo jani na keno.', round: 'R29', time: '05:45' },
      { id: 'bn9', platform: 'community', actor: 'Fact page', role: 'Bangla fact page', kind: 'Correction', text: 'A correction post explains that no circular exists. It is shared by people who were never worried, and it does not reach a single phone that has no data on it.', round: 'R34', time: '06:35' },
      { id: 'bn10', platform: 'plaza', actor: 'Alor Shetu', role: 'Programme help desk', kind: 'Clarification', text: 'The help desk issues a Bangla notice and a hotline number. The mothers who left have no number saved, no reason to call, and no way to learn that they were never removed.', round: 'R39', time: '07:30' },
    ],
    cascadeTails: [
      'The voice note is forwarded before anyone checks whether a circular exists.',
      'Nobody asks the officer, they simply are not in the queue next month.',
      'A signed slip nobody requested becomes the proof the rumour needed.',
      'The correction reaches the phones that were never frightened.',
      'A name missing from the register looks the same as a name that was never there.',
      'The loudest thirty are counted and the quiet four hundred are not.',
    ],
    reportTitle: 'Re-registration Rumour in a Maternal Allowance Programme: Forecast Report on Silent Non-Collection, Gatekeeper Amplification, and a Correction That Misses',
    reportSummary:
      'The programme does not lose the mothers who protest at the union office. It loses the ones who decide that the safest response to an unclear rule is to stop turning up, and the register writes that down as attendance rather than as alarm.',
    reportSections: BDNGO_REPORT.reportSections,
    reportWorkbench: [
      { label: 'Planning', title: 'Outline', detail: 'Cascade phases, segment breakdown, the non-collection lane, amplifier profiles, trust map, dashboard warning, recommendations.' },
      { label: 'Quick Search', title: 'Active memories', detail: 'Forwarded voice note, NID photocopy queue, verification slip, disbursement register.' },
      { label: 'Agent Interview', title: 'Field check', detail: 'Field officers learn about the drop from a register, never from a mother.' },
      { label: 'Complete', title: 'Report ready', detail: 'Maternal allowance report assembled and ready for review.' },
    ],
    interactionLogs: [
      'Load maternal allowance report thread.',
      'Load interviewable mother, field officer, and gatekeeper personas.',
      'Survey prompt bank ready.',
    ],
    reportAgentMessages: [
      { role: 'assistant', text: 'The first loss is not a protest at the union office. It is a mother deciding not to walk there.' },
      { role: 'user', text: 'Where does the programme find out?' },
      { role: 'assistant', text: 'In the disbursement register, a month late, as an attendance number with no reason attached to it.' },
    ],
    reportAgentAnswers: BDNGO_REPORT.reportAgentAnswers,
    interviewAgents: BDNGO_REPORT.interviewAgents,
  }),

  // Telecom pack. Akashlink is an invented operator. The silence lane is dual
  // SIM churn: the complaint volume and the churn are two different
  // populations, and only one of them files a ticket.
  bdtelco: createPack({
    key: 'bdtelco',
    countryCode: 'BD-TELCO',
    countryLabel: 'Bangladesh',
    city: 'Dhaka',
    seedLabel: 'Akashlink Data Pack Repricing - Night Throttling Rumour Brief (fictional operator).pdf',
    defaultScenario:
      'Akashlink raises data pack prices and a rumour spreads that speeds are throttled after midnight. How do students, delivery riders, and small traders respond, and who quietly switches SIM without ever calling the care line?',
    graphLabels: {
      gov_notice: 'Regulator Tariff Notice',
      commodity: 'Akashlink Data Pack Price Rise',
      bazaar: 'Rider Group and Teashop Talk',
      students: 'Campus and Gaming Pages',
      remittance: 'Dual SIM Households',
      workers: 'Delivery Riders',
      mosque: 'Building and Para Groups',
      relief: 'Akashlink Care Line',
      media: 'Bangla Tech and News Pages',
      grocers: 'Flexiload and Recharge Points',
      mothers: 'Household Bill Managers',
    },
    graphClusterNouns: {
      students: 'Dhaka campus page',
      media: 'Bangla tech page',
      remittance: 'Dhaka dual SIM household',
      workers: 'Dhaka rider group',
      mothers: 'Dhaka bill manager',
      bazaar: 'Dhaka teashop thread',
      grocers: 'Dhaka flexiload point',
      gov_notice: 'Regulator notice relay',
      relief: 'Akashlink care queue',
      dhaka: 'Dhaka ward',
    },
    graphLogs: [
      'Tariff sheet and speed test screenshots ingested from the operator pack.',
      'Akashlink registered as the operator entity under complaint.',
      'Campus pages, rider groups, and flexiload points linked as distinct lanes.',
      'Scenario graph ready for population setup.',
    ],
    populationNotes: [
      'Users who post nothing and simply move the second SIM into the primary slot.',
      'Flexiload points that watch recharge value fall before a single complaint is filed.',
      'Rider groups where one speed test screenshot outweighs an official statement.',
    ],
    topicSeeds: [
      'data pack pricing',
      'night speed tests',
      'dual SIM habits',
      'flexiload recharge',
      'rider group chatter',
      'campus page complaints',
      'care line queues',
      'OTP only numbers',
      'operator switching',
      'tariff notices',
      'ping and latency',
      'household bill planning',
    ],
    personas: [
      { name: 'Shakil', role: 'Delivery rider', detail: 'Runs on data all day across Badda and Rampura', trait: 'Switches SIM at the recharge counter, not on a call' },
      { name: 'Mim', role: 'University student', detail: 'Buys the monthly pack out of tuition money', trait: 'Posts the anger and keeps the number' },
      { name: 'Tanjim', role: 'Gaming page admin', detail: 'Runs a ping and speed test group', trait: 'Turns a latency graph into a movement' },
      { name: 'Nazma', role: 'Flexiload counter operator', detail: 'Sells recharge in a Mirpur lane', trait: 'Reads churn off the till, not the news' },
    ],
    simulationLogs: [
      'Seeding the tariff post and the first midnight speed test screenshot.',
      'Running campus pages, rider groups, and recharge counters in parallel.',
      'Tracking silent dual SIM switching against visible complaint volume.',
      'Cascade complete across both communities.',
    ],
    simulationActions: [
      { id: 'bt1', platform: 'plaza', actor: 'Akashlink', role: 'Operator page', kind: 'Tariff post', text: 'Notun data pack, notun daam. Akashlink er shathe thakun. (The post is scheduled. The comment section is not.)', round: 'R02', time: '00:35' },
      { id: 'bt2', platform: 'community', actor: 'Tanjim', role: 'Gaming page admin', kind: 'Speed test', text: 'Rat 12 tar por speed test korlam, 0.6 mbps. Ager rate chilo 18. Eta throttling na hoile ki?', round: 'R05', time: '01:15' },
      { id: 'bt3', platform: 'plaza', actor: 'Mim', role: 'University student', kind: 'Comment storm', text: 'Proti mash e daam baray, service ek i. Ei pack ta ekhon tuition er ordhek. Boycott Akashlink.', round: 'R09', time: '02:05' },
      { id: 'bt4', platform: 'community', actor: 'Rider group', role: 'Delivery rider group', kind: 'Group message', text: 'Bhai, ami dui SIM e chalai. Ekhon Akashlink ta shudhu call er jonno rakhsi, data onno ta te. Keu jigges kore nai, ami kau ke bolio nai.', round: 'R13', time: '02:50' },
      { id: 'bt5', platform: 'plaza', actor: 'Bangla tech page', role: 'Tech page', kind: 'Explainer', text: 'A tech page explains that a throttle cannot be proved from one speed test. The post does well and changes nobody who has already run the test on their own phone.', round: 'R17', time: '03:40' },
      { id: 'bt6', platform: 'community', actor: 'Nazma', role: 'Flexiload counter operator', kind: 'Counter signal', text: 'Ei shoptahe Akashlink er recharge onek kome geche. Manush ekhon onno operator er load nite ashe. Keu karon bole na, shudhu number ta bodle jay.', round: 'R21', time: '04:25' },
      { id: 'bt7', platform: 'plaza', actor: 'Care line', role: 'Akashlink care line', kind: 'Queue statistic', text: 'Call volume rises by a fifth and the operator reads that as the size of the problem. Every complaint in that queue belongs to a customer who has not left.', round: 'R26', time: '05:15' },
      { id: 'bt8', platform: 'community', actor: 'Household bill manager', role: 'Household bill manager', kind: 'Family decision', text: 'Barir shobar pack ek shathe kena hoy. Ei mash e cheler jonno onno operator er pack nilam. Purano SIM ta phone e ache, kintu ekhon shudhu OTP er jonno.', round: 'R30', time: '06:05' },
      { id: 'bt9', platform: 'plaza', actor: 'Regulator notice', role: 'Regulator', kind: 'Tariff notice', text: 'A tariff filing is published. It is procedural, says nothing about speed, and both the operator and the campaign pages quote it as support for their own position.', round: 'R34', time: '06:50' },
      { id: 'bt10', platform: 'community', actor: 'Shakil', role: 'Delivery rider', kind: 'Trade outcome', text: 'Ami complain kori nai. Complain korle time jay, order miss hoy. Ami shudhu tray ta khule SIM ta ulta kore dilam.', round: 'R39', time: '07:40' },
    ],
    cascadeTails: [
      'One speed test becomes the whole network in a single screenshot.',
      'The tray opens, the SIM turns over, and no ticket is ever raised.',
      'The care line counts the people who stayed, not the ones who left.',
      'The explainer convinces the ones who never ran the test.',
      'The number stays alive for OTP and dies for everything else.',
      'Reach arrives in the comments and revenue leaves at the recharge counter.',
    ],
    reportTitle: 'Data Pack Repricing and a Throttling Rumour: Forecast Report on Loud Complaint, Silent Dual SIM Churn, and a Care Line Counting the Wrong People',
    reportSummary:
      'Complaint volume and churn are two different populations here. The people filling the comment section still hold the number, and the people who quietly move data onto the second SIM never file anything, so the operator measures its loudest loyal users and calls that the size of the damage.',
    reportSections: BDTELCO_REPORT.reportSections,
    reportWorkbench: [
      { label: 'Planning', title: 'Outline', detail: 'Cascade phases, segment breakdown, the silent churn lane, amplifier profiles, trust map, dashboard warning, recommendations.' },
      { label: 'Quick Search', title: 'Active memories', detail: 'Midnight speed test, tray swap, flexiload till, OTP only number.' },
      { label: 'Agent Interview', title: 'Recharge check', detail: 'Counter operators see the switch weeks before the retention team does.' },
      { label: 'Complete', title: 'Report ready', detail: 'Operator report assembled and ready for review.' },
    ],
    interactionLogs: [
      'Load operator churn report thread.',
      'Load interviewable rider, student, and recharge counter personas.',
      'Survey prompt bank ready.',
    ],
    reportAgentMessages: [
      { role: 'assistant', text: 'The loudest customers here are the ones who stayed. The churn is happening in silence, one SIM tray at a time.' },
      { role: 'user', text: 'Where does the operator find out?' },
      { role: 'assistant', text: 'At the flexiload counter, as falling recharge value on a connection that still looks perfectly active.' },
    ],
    reportAgentAnswers: BDTELCO_REPORT.reportAgentAnswers,
    interviewAgents: BDTELCO_REPORT.interviewAgents,
  }),

  // Mobile financial services pack. Shonchoy Pay is an invented wallet. The
  // silence lane is a run: nobody complains about taking out their own money,
  // so the only witness is an agent point with no cash left by noon.
  bdwallet: createPack({
    key: 'bdwallet',
    countryCode: 'BD-WALLET',
    countryLabel: 'Bangladesh',
    city: 'Sylhet',
    seedLabel: 'Shonchoy Pay - Cashout Fee Rumour and Agent Float Brief (fictional wallet).pdf',
    defaultScenario:
      'A rumour says Shonchoy Pay cashout fees are rising and balances above a limit will be frozen. How do remittance households, agent points, and para committees respond, and who empties the wallet without telling anyone?',
    graphLabels: {
      gov_notice: 'Central Bank Circular Rumour',
      commodity: 'Shonchoy Pay Cashout Fee Rumour',
      bazaar: 'Bazaar and Agent Point Talk',
      students: 'Meme and Campus Pages',
      remittance: 'Remittance Households',
      workers: 'Agent Point Operators',
      mosque: 'Para Committee Groups',
      relief: 'Shonchoy Pay Helpline',
      media: 'Bangla Business Pages',
      grocers: 'Mudi Dokan Agent Points',
      mothers: 'Women Receiving Transfers',
    },
    graphClusterNouns: {
      students: 'Sylhet campus page',
      media: 'Bangla business page',
      remittance: 'Sylhet remittance household',
      workers: 'Sylhet agent point',
      mothers: 'Sylhet transfer receiver',
      bazaar: 'Sylhet bazaar thread',
      grocers: 'Sylhet mudi dokan agent',
      gov_notice: 'Circular screenshot',
      relief: 'Shonchoy Pay helpline',
      dhaka: 'Sylhet upazila',
    },
    graphLogs: [
      'Forwarded circular screenshot and agent float reports ingested from the wallet pack.',
      'Shonchoy Pay registered as the wallet entity under rumour.',
      'Remittance households, agent points, and para committees linked as distinct lanes.',
      'Scenario graph ready for population setup.',
    ],
    populationNotes: [
      'Households that empty the wallet quietly rather than argue about a fee.',
      'Agent points that run out of cash by noon and cannot say why.',
      'Para committees that can turn one screenshot into a whole upazila cashing out.',
    ],
    topicSeeds: [
      'cashout fees',
      'agent point float',
      'remittance timing',
      'balance limits',
      'forwarded circulars',
      'shomiti savings',
      'bazaar credit',
      'helpline queues',
      'cash kept at home',
      'distributor supply',
      'para committee talk',
      'wallet trust',
    ],
    personas: [
      { name: 'Rahela', role: 'Transfer receiving household head', detail: 'Receives from a son in Muscat', trait: 'Withdraws everything and posts nothing' },
      { name: 'Suhel', role: 'Agent point operator', detail: 'Runs a cash point beside the Beanibazar bus stand', trait: 'Runs dry before understanding why' },
      { name: 'Jesmin', role: 'Shomiti group leader', detail: 'Holds the savings book for a group of twenty', trait: 'Moves twenty households with one decision' },
      { name: 'Belal', role: 'Para committee secretary', detail: 'Forwards what the committee should know', trait: 'Packages rumour as prudence' },
    ],
    simulationLogs: [
      'Seeding the forwarded circular screenshot and the first fee claim.',
      'Running household, agent point, and committee lanes in parallel.',
      'Tracking silent cashout against visible complaint volume.',
      'Cascade complete across both communities.',
    ],
    simulationActions: [
      { id: 'bw1', platform: 'community', actor: 'Belal', role: 'Para committee secretary', kind: 'Forward', text: 'ভাইসব, একটা সার্কুলার ঘুরতেছে। ক্যাশআউট চার্জ নাকি বাড়তেছে, আর একটা লিমিটের উপরে টাকা রাখলে নাকি আটকায়া যাইব। যাচাই করতে পারলাম না, তবু জানায়া রাখলাম।', round: 'R02', time: '00:40' },
      { id: 'bw2', platform: 'plaza', actor: 'Shonchoy Pay', role: 'Wallet brand page', kind: 'Campaign post', text: 'Shonchoy Pay diye Eid er kenakata, ekhon aro shohoj. (Scheduled post, published while the screenshot is still moving.)', round: 'R04', time: '01:05' },
      { id: 'bw3', platform: 'community', actor: 'Rahela', role: 'Transfer receiving household head', kind: 'Silent cashout', text: 'Chele je taka pathaise, puro ta tuila anlam. Rekhe labh ki, jodi atkaya jay. Karo ke kichu bolar dorkar nai.', round: 'R07', time: '01:50' },
      { id: 'bw4', platform: 'plaza', actor: 'Meme page', role: 'Campus meme page', kind: 'Meme post', text: 'Balance 12 taka, tao chinta hoy limit cross korlam kina. (The joke gets more reach in one evening than the helpline gets calls in a week.)', round: 'R11', time: '02:35' },
      { id: 'bw5', platform: 'community', actor: 'Suhel', role: 'Agent point operator', kind: 'Liquidity signal', text: 'Shokal egaro tar moddhe cash shesh. Ekjon o taka rakhte ashe nai, shobai shudhu tulte ashtese. Distributor ke phone dilam, tini o cash pacchen na.', round: 'R15', time: '03:20' },
      { id: 'bw6', platform: 'plaza', actor: 'Bangla business page', role: 'Business page', kind: 'Explainer', text: 'A business page reports that no circular exists and the fee schedule is unchanged. It circulates among people who read business pages and does not reach a single agent point.', round: 'R19', time: '04:10' },
      { id: 'bw7', platform: 'community', actor: 'Jesmin', role: 'Shomiti group leader', kind: 'Group decision', text: 'Group er shob apa ke bollam, ei mash er taka cash e rakhen. Bhul hole pore abar dhukaya diben. Bish jon apa ek din e tuila felsen.', round: 'R24', time: '05:00' },
      { id: 'bw8', platform: 'plaza', actor: 'Helpline', role: 'Shonchoy Pay helpline', kind: 'Queue statistic', text: 'Complaint calls barely move all week. The people cashing out do not have a complaint, they have a plan, and a plan does not generate a ticket.', round: 'R28', time: '05:50' },
      { id: 'bw9', platform: 'community', actor: 'Bazaar trader', role: 'Bazaar wholesale trader', kind: 'Trade outcome', text: 'Ei shoptahe bazar e cash er obostha kharap. Agent point e taka nai, tai shobai bakite mal ditese. Eta wallet er khobor na, eta bazar er khobor.', round: 'R33', time: '06:40' },
      { id: 'bw10', platform: 'plaza', actor: 'Shonchoy Pay', role: 'Wallet response desk', kind: 'Clarification', text: 'The brand posts a fee table in Bangla and English. It reassures the app users who never emptied anything, and the households already holding the money in cash have no reason to open it.', round: 'R38', time: '07:35' },
    ],
    cascadeTails: [
      'The screenshot is forwarded before anyone checks whether a circular exists.',
      'Nobody announces a run, they arrive one at a time and take everything.',
      'The agent point is dry by noon while the dashboard still looks healthy.',
      'A plan does not generate a complaint, so the helpline stays quiet.',
      'The correction reaches the people who never moved the money.',
      'Cash in a tin at home is invisible to every metric the brand owns.',
    ],
    reportTitle: 'Cashout Fee Rumour and a Quiet Run on Agent Points: Forecast Report on Silent Withdrawal, Float Collapse, and a Helpline That Stays Quiet',
    reportSummary:
      'This crisis produces almost no complaints, because withdrawing your own money is not a grievance. The first and only visible symptom is an agent point running dry by noon, and by then the balances have already left the system.',
    reportSections: BDWALLET_REPORT.reportSections,
    reportWorkbench: [
      { label: 'Planning', title: 'Outline', detail: 'Cascade phases, segment breakdown, the silent run lane, amplifier profiles, trust map, dashboard warning, recommendations.' },
      { label: 'Quick Search', title: 'Active memories', detail: 'Forwarded circular image, agent float, shomiti group decision, cash kept at home.' },
      { label: 'Agent Interview', title: 'Agent point check', detail: 'Operators run dry before anyone in the company sees a number move.' },
      { label: 'Complete', title: 'Report ready', detail: 'Wallet report assembled and ready for review.' },
    ],
    interactionLogs: [
      'Load wallet run report thread.',
      'Load interviewable household, agent point, and committee personas.',
      'Survey prompt bank ready.',
    ],
    reportAgentMessages: [
      { role: 'assistant', text: 'There is almost no complaint in this scenario. Taking out your own money is not something anyone files a ticket about.' },
      { role: 'user', text: 'Where does the company find out?' },
      { role: 'assistant', text: 'At the agent point, when the float is gone by noon and the distributor has nothing left to send.' },
    ],
    reportAgentAnswers: BDWALLET_REPORT.reportAgentAnswers,
    interviewAgents: BDWALLET_REPORT.interviewAgents,
  }),

  // Industrial relations pack. Shubarna Apparels, Poshak Sromik Oikko and the
  // Poshak Malik Forum are invented. The silence lane is the factory floor: the
  // sentence that matters is never said where a supervisor can hear it.
  bdwage: createPack({
    key: 'bdwage',
    countryCode: 'BD-WAGE',
    countryLabel: 'Bangladesh',
    city: 'Gazipur',
    seedLabel: 'Wage Board Announcement in Bonus Season - Floor Response Brief (fictional employer and union bodies).pdf',
    defaultScenario:
      'A wage board announcement lands in the middle of Eid bonus season at Shubarna Apparels in Gazipur. How do floor workers, supervisors, union voices, and the owners forum respond, and where does the sentence that matters actually get said?',
    graphLabels: {
      gov_notice: 'Wage Board Announcement',
      commodity: 'Wage Board and Eid Bonus Gap',
      bazaar: 'Teashop and Mess Talk',
      students: 'Labour Rights Pages',
      remittance: 'Village Households Waiting for the Bonus',
      workers: 'Garment Floor Workers',
      mosque: 'Mess and Building Networks',
      relief: 'Shubarna HR and Compliance Desk',
      media: 'Bangla Labour News Pages',
      grocers: 'Mess Canteens and Grocers',
      mothers: 'Women on the Sewing Floor',
    },
    graphClusterNouns: {
      students: 'Labour rights page',
      media: 'Bangla labour page',
      remittance: 'Village household waiting',
      workers: 'Gazipur floor worker',
      mothers: 'Gazipur sewing line',
      bazaar: 'Gazipur teashop thread',
      grocers: 'Gazipur mess canteen',
      gov_notice: 'Wage board relay',
      relief: 'Shubarna HR desk',
      dhaka: 'Gazipur ward',
    },
    graphLogs: [
      'Wage board summary and bonus circular ingested from the factory pack.',
      'Shubarna Apparels registered as the employer entity under pressure.',
      'Floor workers, supervisors, union voices, and the owners forum linked as separate lanes.',
      'Scenario graph ready for population setup.',
    ],
    populationNotes: [
      'Floor workers who cannot say on the line what they will say at the teashop.',
      'Supervisors held responsible for a number they did not set.',
      'Village households budgeting Eid around a figure nobody has confirmed.',
    ],
    topicSeeds: [
      'wage board figures',
      'Eid bonus timing',
      'overtime lists',
      'floor silence',
      'teashop talk',
      'union statements',
      'owners forum messaging',
      'supervisor pressure',
      'village remittance plans',
      'gate notices',
      'mess room decisions',
      'attendance records',
    ],
    personas: [
      { name: 'Rina', role: 'Sewing machine operator', detail: 'Eleven years on the same floor', trait: 'Silent at the machine, precise at the teashop' },
      { name: 'Shafiq', role: 'Line supervisor', detail: 'Answers to production and to sixty operators', trait: 'Carries a number set in another room' },
      { name: 'Monowara', role: 'Helper section worker', detail: 'Sends the bonus home to Kurigram', trait: 'Plans Eid around a figure nobody has confirmed' },
      { name: 'Jahangir', role: 'Owners forum representative', detail: 'Speaks for a group of factories', trait: 'Answers the buyers, not the floor' },
    ],
    simulationLogs: [
      'Seeding the wage board announcement into bonus season.',
      'Running the floor, the teashop, the union lane, and the owners forum in parallel.',
      'Tracking floor silence against teashop volume.',
      'Cascade complete across both communities.',
    ],
    simulationActions: [
      { id: 'bg1', platform: 'plaza', actor: 'Wage board', role: 'Wage board announcement', kind: 'Announcement', text: 'The new minimum is announced as a monthly figure. The floor immediately reads it as a question about the Eid bonus, which is calculated on the old one.', round: 'R02', time: '00:35' },
      { id: 'bg2', platform: 'community', actor: 'Rina', role: 'Sewing machine operator', kind: 'Floor silence', text: 'Line e keu kichu bole nai. Supervisor pashei daraya chilo. Shobai jane, keu mukh khole na.', round: 'R05', time: '01:15' },
      { id: 'bg3', platform: 'plaza', actor: 'Poshak Sromik Oikko', role: 'Union voice', kind: 'Statement', text: 'Notun wage board er ghoshona kono bhabei Eid bonus e kaat dhorate parbe na. Amra proti factory te likhito nishchoyota chai.', round: 'R09', time: '02:05' },
      { id: 'bg4', platform: 'community', actor: 'Teashop table', role: 'Teashop and mess talk', kind: 'Night talk', text: 'Rat dosh tay cha er dokane shob kotha ber hoy. Ke koto pabe, ke pabe na, kar barite ki bolche. Ekhane keu supervisor na.', round: 'R12', time: '02:45' },
      { id: 'bg5', platform: 'plaza', actor: 'Poshak Malik Forum', role: 'Owners forum representative', kind: 'Press line', text: 'The owners forum tells a business page that the new structure will be implemented in full and on time. The sentence is about compliance and answers nothing the floor asked.', round: 'R16', time: '03:35' },
      { id: 'bg6', platform: 'community', actor: 'Shafiq', role: 'Line supervisor', kind: 'Between two rooms', text: 'Upor theke bole target thik rakhte. Nich theke jigges kore bonus koto. Ami duitar kono uttor jani na, kintu duitar jonnoi amake dhorbe.', round: 'R20', time: '04:20' },
      { id: 'bg7', platform: 'plaza', actor: 'Labour rights page', role: 'Labour rights page', kind: 'Post', text: 'A rights page posts a worked example showing the bonus falling short. The arithmetic is shared thousands of times, mostly by people who have never worked a line.', round: 'R24', time: '05:05' },
      { id: 'bg8', platform: 'community', actor: 'Monowara', role: 'Helper section worker', kind: 'Village call', text: 'Barite bolechi Eid e taka pathabo. Ekhon jani na koto ashbe. Ma ke ekhono kichu boli nai, mash sesh na howa porjonto bolbo o na.', round: 'R29', time: '05:55' },
      { id: 'bg9', platform: 'plaza', actor: 'HR desk', role: 'Factory HR and compliance desk', kind: 'Gate notice', text: 'HR posts a Bangla notice on the board beside the gate. It is read by the workers leaving the shift and rewritten five times before it reaches the mess.', round: 'R34', time: '06:45' },
      { id: 'bg10', platform: 'community', actor: 'Mess room', role: 'Mess and building network', kind: 'Quiet withdrawal', text: 'Kaj bondho korar kotha keu bolche na. Kintu ei mash e overtime e keu thakte chaitese na. Eta kono notice na, eta shudhu bari chole jawa.', round: 'R39', time: '07:35' },
    ],
    cascadeTails: [
      'The sentence that matters is not said where a supervisor can hear it.',
      'A number set in one room is enforced in another by someone who did not set it.',
      'The notice on the gate is rewritten five times before it reaches the mess.',
      'Nobody calls it a protest, they simply stop staying for overtime.',
      'The village is told nothing until the figure is certain.',
      'The press answer is about compliance and the floor asked about Eid.',
    ],
    reportTitle: 'A Wage Board Announcement in Bonus Season: Forecast Report on Floor Silence, Teashop Truth, and Supervisors Caught in Between',
    reportSummary:
      'On the floor the response is silence, because speaking in front of the person who writes the overtime list is a risk. The sentence that matters is said at the teashop at ten at night, and the factory receives a fifth hand version of it a week later, if at all.',
    reportSections: BDWAGE_REPORT.reportSections,
    reportWorkbench: [
      { label: 'Planning', title: 'Outline', detail: 'Cascade phases, segment breakdown, the floor silence lane, amplifier profiles, trust map, dashboard warning, recommendations.' },
      { label: 'Quick Search', title: 'Active memories', detail: 'Attendance and overtime list, teashop at ten, gate notice, village phone call.' },
      { label: 'Agent Interview', title: 'Floor check', detail: 'Workers give management the silence and the teashop the sentence.' },
      { label: 'Complete', title: 'Report ready', detail: 'Wage board report assembled and ready for review.' },
    ],
    interactionLogs: [
      'Load wage board report thread.',
      'Load interviewable floor, supervisor, and owners forum personas.',
      'Survey prompt bank ready.',
    ],
    reportAgentMessages: [
      { role: 'assistant', text: 'The floor is quiet and that is not agreement. It is what happens when the person who writes the overtime list is standing right there.' },
      { role: 'user', text: 'Where does the sentence that matters get said?' },
      { role: 'assistant', text: 'At the teashop at ten at night, with no supervisor in the room and no route back into the factory.' },
    ],
    reportAgentAnswers: BDWAGE_REPORT.reportAgentAnswers,
    interviewAgents: BDWAGE_REPORT.interviewAgents,
  }),

  // Public health pack. Shapla General is an invented hospital. The silence
  // lane is care seeking itself: the sick stop presenting, and the surge shows
  // up only as paracetamol volume at a counter that keeps no register.
  bdhealth: createPack({
    key: 'bdhealth',
    countryCode: 'BD-HEALTH',
    countryLabel: 'Bangladesh',
    city: 'Dhaka',
    seedLabel: 'Dengue Season - Beds Full Rumour and Care Seeking Brief (fictional hospital).pdf',
    defaultScenario:
      'A rumour says every hospital bed in the city is full during dengue season. How do households with a fever, para pharmacies, and ward staff respond, and who stops presenting at hospital altogether?',
    graphLabels: {
      gov_notice: 'District Health Office Notice',
      commodity: 'Beds Full Rumour in Dengue Season',
      bazaar: 'Para and Rickshaw Stand Talk',
      students: 'Campus and Health Meme Pages',
      remittance: 'Households With a Fever at Home',
      workers: 'Hospital Ward Staff',
      mosque: 'Building and Para Committees',
      relief: 'Shapla General Front Desk',
      media: 'Bangla Health Pages',
      grocers: 'Para Pharmacy Counters',
      mothers: 'Mothers Watching a Fever Chart',
    },
    graphClusterNouns: {
      students: 'Dhaka health meme page',
      media: 'Bangla health page',
      remittance: 'Dhaka fever household',
      workers: 'Shapla ward staff',
      mothers: 'Dhaka fever chart mother',
      bazaar: 'Dhaka rickshaw stand thread',
      grocers: 'Dhaka para pharmacy',
      gov_notice: 'Health office notice',
      relief: 'Shapla front desk',
      dhaka: 'Dhaka ward',
    },
    graphLogs: [
      'Corridor photographs and forwarded voice notes ingested from the dengue season pack.',
      'Shapla General registered as the facility entity under rumour.',
      'Fever households, para pharmacies, and ward staff linked as distinct lanes.',
      'Scenario graph ready for population setup.',
    ],
    populationNotes: [
      'Households that treat a fever at home rather than risk a night on a corridor floor.',
      'Para pharmacy counters that see the cases no hospital register ever records.',
      'Ward staff with empty beds on a night the city is certain there are none.',
    ],
    topicSeeds: [
      'dengue season',
      'bed availability',
      'pharmacy counter advice',
      'platelet counts',
      'fever charts',
      'corridor photographs',
      'late presentation',
      'rickshaw stand talk',
      'building group forwards',
      'health office notices',
      'ward occupancy',
      'treating a fever at home',
    ],
    personas: [
      { name: 'Shefa', role: 'Mother watching a fever chart', detail: 'Two children, day five of a fever', trait: 'Buys the saline instead of the taxi fare' },
      { name: 'Masum', role: 'Para pharmacy counter', detail: 'Sells more paracetamol than in any week this year', trait: 'Counts the cases nobody else counts' },
      { name: 'Tania', role: 'Ward nurse', detail: 'Night shift at Shapla General', trait: 'Sees the beds the city says are gone' },
      { name: 'Arafat', role: 'Rickshaw stand organiser', detail: 'Carries the sick to hospital, or does not', trait: 'Repeats whatever the last passenger said' },
    ],
    simulationLogs: [
      'Seeding the corridor photograph and the first beds full claim.',
      'Running fever households, pharmacy counters, and ward staff in parallel.',
      'Tracking the collapse in presentation against visible complaint volume.',
      'Cascade complete across both communities.',
    ],
    simulationActions: [
      { id: 'bh1', platform: 'community', actor: 'Building group', role: 'Building committee group', kind: 'Forward', text: 'ভাই, ওইদিকে নাকি একটাও সিট খালি নাই। ফ্লোরে রাখতেছে। একটা ছবি পাঠাইলাম, কে তুলছে জানি না।', round: 'R02', time: '00:35' },
      { id: 'bh2', platform: 'plaza', actor: 'Health meme page', role: 'Health meme page', kind: 'Meme post', text: 'Dengue season e hospital er bed khoja ar Dhaka te parking khoja, ekoi jinish. (The joke carries the claim further than the photograph did.)', round: 'R05', time: '01:10' },
      { id: 'bh3', platform: 'community', actor: 'Shefa', role: 'Mother watching a fever chart', kind: 'Home treatment', text: 'Panch din hoise jor. Hospital e giya floor e thakte hobe shune ar gelam na. Pharmacy theke saline ar napa nilam, ar khatay temperature likhe rakhtesi.', round: 'R09', time: '02:00' },
      { id: 'bh4', platform: 'plaza', actor: 'Masum', role: 'Para pharmacy counter', kind: 'Counter signal', text: 'Ei shoptahe napa ar saline er bikri tin gun. Manush ekhon amar kache eshe platelet er kotha jigges kore. Ami doctor na, kintu amar shathei kotha bole.', round: 'R13', time: '02:50' },
      { id: 'bh5', platform: 'community', actor: 'Arafat', role: 'Rickshaw stand organiser', kind: 'Stand talk', text: 'Rat e ekjon ke niya gesilam, firaya dise bole shunsi. Tar por theke keu hospital er kotha bolle ami oi kotha tai boli.', round: 'R17', time: '03:40' },
      { id: 'bh6', platform: 'plaza', actor: 'Tania', role: 'Ward nurse', kind: 'Ward observation', text: 'Kal rat e amader ward e char ta bed khali chilo. Shohor bolche ekta o nai. Amra kake bolbo shetai jani na.', round: 'R21', time: '04:25' },
      { id: 'bh7', platform: 'community', actor: 'Para pharmacy', role: 'Para pharmacy counter', kind: 'Counter triage', text: 'A counter sells a fourth day of paracetamol to the same household and advises a platelet test. That advice is the only clinical triage this patient will receive.', round: 'R26', time: '05:15' },
      { id: 'bh8', platform: 'plaza', actor: 'District health office', role: 'District health office', kind: 'Occupancy notice', text: 'The health office publishes bed availability by facility. It is a document, it is accurate, and it is opened by journalists and by nobody with a fever at home.', round: 'R30', time: '06:05' },
      { id: 'bh9', platform: 'community', actor: 'Fever household', role: 'Household with a fever at home', kind: 'Late presentation', text: 'Ath din er din obostha kharap hoise, tokhon hospital e newa hoise. Deri ta rumour er jonno, kintu file e likha thakbe late presentation.', round: 'R35', time: '06:55' },
      { id: 'bh10', platform: 'plaza', actor: 'Shapla General', role: 'Hospital front desk', kind: 'Clarification', text: 'The hospital posts that beds are available. It reaches the people who were always going to come, and the households that already decided see no reason to check again.', round: 'R39', time: '07:40' },
    ],
    cascadeTails: [
      'A corridor photograph nobody can date becomes the state of every hospital.',
      'The fever is treated at a counter that keeps no register.',
      'The ward has empty beds on the night the city is certain there are none.',
      'The accurate notice is opened by journalists and by nobody with a fever.',
      'Delay caused by a rumour is written into the file as late presentation.',
      'The correction reaches the households that were always going to come.',
    ],
    reportTitle: 'A Beds Full Rumour in Dengue Season: Forecast Report on Care Seeking Collapse, Pharmacy Counter Triage, and a Correction Nobody Opens',
    reportSummary:
      'The hospital does not lose the patients who argue at the front desk. It loses the ones who never arrive, whose fever is managed at a pharmacy counter for four extra days, and who are written up on admission as late presentation rather than as a rumour.',
    reportSections: BDHEALTH_REPORT.reportSections,
    reportWorkbench: [
      { label: 'Planning', title: 'Outline', detail: 'Cascade phases, segment breakdown, the care seeking lane, amplifier profiles, trust map, dashboard warning, recommendations.' },
      { label: 'Quick Search', title: 'Active memories', detail: 'Corridor photograph, fourth day of paracetamol, platelet question, occupancy notice.' },
      { label: 'Agent Interview', title: 'Counter check', detail: 'Pharmacies see the surge that never reaches an admission register.' },
      { label: 'Complete', title: 'Report ready', detail: 'Dengue season report assembled and ready for review.' },
    ],
    interactionLogs: [
      'Load dengue season report thread.',
      'Load interviewable household, pharmacy counter, and ward staff personas.',
      'Survey prompt bank ready.',
    ],
    reportAgentMessages: [
      { role: 'assistant', text: 'The first loss is not an argument at the front desk. It is a household deciding at eleven at night not to come at all.' },
      { role: 'user', text: 'Where does the system find out?' },
      { role: 'assistant', text: 'At a para pharmacy counter, as paracetamol volume, days before any admission number moves.' },
    ],
    reportAgentAnswers: BDHEALTH_REPORT.reportAgentAnswers,
    interviewAgents: BDHEALTH_REPORT.interviewAgents,
  }),
}

// Scenario picker source for the demo intake. Country codes here are the same
// ones ?country= accepts, so a pick is only ever a query change.
export const DEMO_SCENARIO_PICKS = [
  { countryCode: 'BD', label: 'Rice price shock', detail: 'Dhaka, staple price rise before Eid' },
  { countryCode: 'BD-BRAND', label: 'Contamination rumour', detail: 'Fictional noodle brand, Eid campaign week' },
  { countryCode: 'BD-NGO', label: 'Re-registration rumour', detail: 'Maternal cash transfer, Kurigram' },
  { countryCode: 'BD-TELCO', label: 'Price rise and throttling', detail: 'Fictional operator, Dhaka' },
  { countryCode: 'BD-WALLET', label: 'Cashout fee run', detail: 'Fictional wallet, Sylhet agent points' },
  { countryCode: 'BD-WAGE', label: 'Wage board in bonus season', detail: 'Garment floor, Gazipur' },
  { countryCode: 'BD-HEALTH', label: 'Beds full rumour', detail: 'Dengue season, Dhaka' },
]

export const DEMO_DEFAULT_PACK_KEY = 'bangladesh'

export function resolveDemoPackKey(countryCode) {
  const normalized = String(countryCode || '').trim().toUpperCase()
  return COUNTRY_CODE_TO_PACK[normalized] || DEMO_DEFAULT_PACK_KEY
}

export function getDemoPackByCountryCode(countryCode) {
  return DEMO_PACKS[resolveDemoPackKey(countryCode)]
}

export function getDemoPack(packKey) {
  return DEMO_PACKS[packKey] || DEMO_PACKS[DEMO_DEFAULT_PACK_KEY]
}

export const DEMO_WORKFLOW_STEPS = [
  {
    number: '01',
    title: 'Graph Build',
    description: 'Reality seed extraction, relationship mapping, and GraphRAG construction.',
  },
  {
    number: '02',
    title: 'Population Setup',
    description: 'Country priors, persona generation, and environment scaffolding.',
  },
  {
    number: '03',
    title: 'Start Simulation',
    description: 'Multi-agent rounds, platform actions, and cascade progression.',
  },
  {
    number: '04',
    title: 'Report Generation',
    description: 'Structured synthesis grounded in the simulated public sphere.',
  },
  {
    number: '05',
    title: 'Deep Interaction',
    description: 'Question the report agent and interview simulated people.',
  },
]
