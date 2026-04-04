const COUNTRY_CODE_TO_PACK = {
  BD: 'bangladesh',
  IN: 'india',
  PK: 'pakistan',
  LK: 'srilanka',
  NP: 'nepal',
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

function createGraphData(key, labels = {}) {
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
  graphLogs,
  populationNotes,
  personas,
  simulationLogs,
  simulationActions,
  reportTitle,
  reportSummary,
  reportSections,
  reportWorkbench,
  interactionLogs,
  reportAgentMessages,
  interviewAgents,
}) {
  const graphData = createGraphData(key, {
    commodity: `${countryLabel} staple price shock`,
    dhaka: city,
    ...graphLabels,
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
      personas,
      logs: [
        `Load country priors for ${countryLabel}.`,
        `Assemble audience clusters for ${city}.`,
        `Generate persona seeds for ${personas.length} anchor agents.`,
        `Lock environment configuration for static demo playback.`,
      ],
    },
    simulation: {
      communityA: { name: 'Info Plaza', rounds: 40, acts: 276 },
      communityB: { name: 'Topic Community', rounds: 40, acts: 456 },
      actions: simulationActions,
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
    reportSections: [
      {
        title: 'Household stress surfaces before visible protest',
        paragraphs: [
          'In the first phase of the simulation, low-income households respond by shrinking food portions and delaying purchases before producing a loud public complaint.',
          'The emotional center of the response is not ideological anger at first. It is domestic arithmetic, especially among remittance-linked households and women managing food for the family.',
        ],
      },
      {
        title: 'Student pages convert private strain into public narrative',
        paragraphs: [
          'Once campus Facebook pages frame the issue as institutional neglect, the conversation shifts from household coping to legitimacy and accountability.',
          'That framing creates a bridge between price anxiety and a broader story of exclusion, letting the issue travel faster than official clarification.',
        ],
      },
      {
        title: 'Late relief messaging deepens distrust',
        paragraphs: [
          'When relief signals arrive late, they do not reset the conversation. They arrive into an already skeptical information environment shaped by rumor, screenshots, and queue imagery.',
          'The result is not only frustration but a durable drop in trust toward the institutions expected to respond first.',
        ],
      },
    ],
    reportWorkbench: [
      { label: 'Planning', title: 'Outline', detail: 'Three sections focused on household coping, public amplification, and trust decay.' },
      { label: 'Quick Search', title: 'Active memories', detail: 'Price board photos, queue language, remittance household stress, Eid timing.' },
      { label: 'Agent Interview', title: 'Population check', detail: 'Silent coping among women managing food persists longer than visible complaint.' },
      { label: 'Complete', title: 'Report ready', detail: 'Static demo report assembled for Bangladesh pack.' },
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
    interviewAgents: [
      { name: 'Halima', role: 'Fish drying worker', response: 'She does not post. She reduces meals first and only speaks when the shortage becomes impossible to hide.' },
      { name: 'Rafi', role: 'Student page admin', response: 'He turns price anxiety into a sharable story about institutions not listening.' },
      { name: 'Shila', role: 'Garment worker', response: 'She measures the shock through dormitory budgeting and delayed remittances home.' },
    ],
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
      'Women who manage both care labor and ration queues.',
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
      { label: 'Complete', title: 'Report ready', detail: 'Static Bihar demo package complete.' },
    ],
    interactionLogs: ['Load Bihar report thread.', 'Load interviewable district personas.', 'Survey prompt bank ready.'],
    reportAgentMessages: [
      { role: 'assistant', text: 'In this scenario, the line outside the ration shop matters more than the text of the notice.' },
      { role: 'user', text: 'Who stabilizes the response?' },
      { role: 'assistant', text: 'Volunteer women and known local workers act as informal trust infrastructure.' },
    ],
    interviewAgents: [
      { name: 'Phulwanti', role: 'ASHA volunteer', response: 'She continues her rounds while answering food questions she was never formally assigned to handle.' },
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
      'Women who manage household food without public political speech.',
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
      { label: 'Complete', title: 'Report ready', detail: 'Static Faisalabad demo package complete.' },
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
      { label: 'Complete', title: 'Report ready', detail: 'Static Sri Lanka demo package complete.' },
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
      'Women running the farm, school payments, medicine, and debt servicing.',
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
      { label: 'Complete', title: 'Report ready', detail: 'Static Nepal demo package complete.' },
    ],
    interactionLogs: ['Load Nepal report thread.', 'Load interviewable remittance-household personas.', 'Survey prompt bank ready.'],
    reportAgentMessages: [
      { role: 'assistant', text: 'The earliest reaction is household management through silence, not visible protest.' },
      { role: 'user', text: 'What makes the issue public?' },
      { role: 'assistant', text: 'Shared price evidence at the village shop and trusted interpretation by local volunteers.' },
    ],
    interviewAgents: [
      { name: 'Kalpana', role: 'Farmer and volunteer', response: 'She hides the first consequences from her husband because her job is to keep the household functioning.' },
      { name: 'Milan', role: 'Shopkeeper', response: 'He is where private struggle becomes a visible public fact.' },
      { name: 'Anju', role: 'Health volunteer', response: 'She explains risk in language that people trust more than official copy.' },
    ],
  }),
}

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
