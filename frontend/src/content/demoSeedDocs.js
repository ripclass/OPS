import { DEMO_DEFAULT_PACK_KEY } from './demoFlowPacks'

// Reality seeds are the artefacts a client or a programme office would actually
// hand over with a brief: a deck, a scanned circular, a chat export, a stock
// sheet, a photograph nobody can date. They exist so a demo run visibly
// consumes something before it advances. Every brand, programme, employer and
// facility named here is fictional and matches the pack it belongs to.
//
// Shape: { name, kind, note }
//   kind - short type token shown in a badge
//   note - very short provenance line, six words at most

export const DEMO_SEED_DOCS = {
  bangladesh: [
    { name: 'Commerce Ministry price notice.pdf', kind: 'PDF', note: 'circulated 09:40, copy unverified' },
    { name: 'Karwan Bazar price board.jpg', kind: 'IMG', note: 'shot 07:12, wholesaler lane' },
    { name: 'Retail rate tracker, six wards.xlsx', kind: 'XLSX', note: 'client sheet, updated weekly' },
  ],

  bdbrand: [
    { name: 'Rongdhonu Eid campaign deck.pdf', kind: 'PDF', note: 'client deck, version four' },
    { name: 'Mother group screenshots.png', kind: 'IMG', note: 'forwarded 22:14, unverified' },
    { name: 'Distributor pullback log.xlsx', kind: 'XLSX', note: 'eleven retailers, three days' },
  ],

  bdngo: [
    { name: 'Upazila circular scan.pdf', kind: 'PDF', note: 'photographed at union office' },
    { name: 'Field officer WhatsApp log.txt', kind: 'TXT', note: 'exported 21:05, four unions' },
    { name: 'Mayer Hashi collection dropoff.xlsx', kind: 'XLSX', note: 'Alor Shetu monitoring, month seven' },
  ],

  bdtelco: [
    { name: 'Akashlink tariff sheet, new packs.pdf', kind: 'PDF', note: 'client issued, not yet public' },
    { name: 'Care line complaint export.csv', kind: 'CSV', note: '48 hours, top ten reasons' },
    { name: 'Rider group chat export.txt', kind: 'TXT', note: 'night shift riders, unverified' },
  ],

  bdwallet: [
    { name: 'Shonchoy Pay fee change memo.pdf', kind: 'PDF', note: 'internal, marked draft' },
    { name: 'Agent point float report.xlsx', kind: 'XLSX', note: 'Sylhet zone, nine days' },
    { name: 'Para committee forward.txt', kind: 'TXT', note: 'screenshot text, sender unknown' },
  ],

  bdwage: [
    { name: 'Wage board gazette extract.pdf', kind: 'PDF', note: 'eight pages, section three only' },
    { name: 'Shubarna Apparels gate notice.jpg', kind: 'IMG', note: 'pinned at shift change' },
    { name: 'Poshak Sromik Oikko statement.doc', kind: 'DOC', note: 'emailed 18:40, embargo unclear' },
  ],

  bdhealth: [
    { name: 'Shapla General ward occupancy.xlsx', kind: 'XLSX', note: 'night count, three wards' },
    { name: 'Beds full voice note transcript.txt', kind: 'TXT', note: 'forwarded 23:50, source unknown' },
    { name: 'Corridor photo from family group.jpg', kind: 'IMG', note: 'undated, location unclear' },
  ],

  india: [
    { name: 'District food office circular.pdf', kind: 'PDF', note: 'scanned at block office' },
    { name: 'Fair price shop stock register.xlsx', kind: 'XLSX', note: 'twelve shops, week three' },
    { name: 'Family WhatsApp forward log.txt', kind: 'TXT', note: 'exported 20:30, unverified' },
  ],

  pakistan: [
    { name: 'Utility store supply note.pdf', kind: 'PDF', note: 'district copy, unsigned' },
    { name: 'Flour rate board photo.jpg', kind: 'IMG', note: 'shot at Ghanta Ghar lane' },
    { name: 'Masjid group forward export.txt', kind: 'TXT', note: 'exported 21:15, two groups' },
  ],

  srilanka: [
    { name: 'Divisional secretariat cost notice.pdf', kind: 'PDF', note: 'posted at estate office' },
    { name: 'Estate grocer price ledger.xlsx', kind: 'XLSX', note: 'line rooms, four weeks' },
    { name: 'Union meeting minutes.doc', kind: 'DOC', note: 'typed later from memory' },
  ],

  nepal: [
    { name: 'Municipal price notice.pdf', kind: 'PDF', note: 'pasted at ward office' },
    { name: 'Village shop rate sheet.xlsx', kind: 'XLSX', note: 'seven shops, hand entered' },
    { name: 'FCHV visit notes.txt', kind: 'TXT', note: 'typed from field diary' },
  ],
}

// The scripted brief behind "Draft the brief for me". Written the way an
// account exec writes one: the trigger, the segments worth watching, and the
// decision the client is actually stuck on. Deliberately richer than the pack's
// own one-line defaultScenario.
export const DEMO_DRAFTED_BRIEFS = {
  bangladesh:
    'Rice has risen about 40 percent in the Dhaka wholesale lanes in the ten days before Eid, and the Commerce Ministry notice has not landed as reassurance. We need the response traced across low-income households already cutting portions, campus grievance pages turning it into a legitimacy story, and the bazaar rumour chains that move a price board photo faster than a circular. The client has to decide whether to announce a relief measure this week or wait for the market to settle, and needs to know which of those two costs more trust.',

  bdbrand:
    'A contamination rumour about Rongdhonu Noodles started in school mother groups on the second day of the Eid campaign flight, and by day three the meme pages were carrying it. We need to see who stops buying quietly, which mudi dokan retailers pull stock before anyone asks them to, and whether a clean BSTI test result will still be believed by the time it arrives. The client has to decide today whether to pause the Eid creative or keep spending through the rumour, and we want the cost of both options on the table.',

  bdngo:
    'A rumour is moving through Kurigram that the Mayer Hashi maternal allowance is being cut and that every mother must re-register with her NID at the union office. Alor Shetu Foundation needs to know which beneficiary mothers stop collecting rather than risk a wasted day of travel, how field officers are answering when they do not have the circular in hand, and where union gatekeepers are charging for help that is meant to be free. The decision is whether to run the correction through the unions that are part of the problem or go direct to mothers through a slower, more trusted channel.',

  bdtelco:
    'Akashlink raised data pack prices this week and a rumour spread alongside it that speeds are throttled after midnight. We want the response separated across students living on the cheapest packs, delivery riders who work the night hours, and small traders running a business off a single SIM, plus the group that switches SIM without ever calling the care line. The client has to decide whether to publish a speed commitment it will then be measured against, or stay quiet and absorb the churn.',

  bdwallet:
    'A rumour says Shonchoy Pay is raising cashout fees and freezing balances above a limit, and the Sylhet agent points saw a visible run on Thursday afternoon. We need to know which remittance households emptied the wallet without telling anyone, how agent points are explaining a fee change that has not actually happened, and what the para committees are repeating to each other. The client has to decide whether a public denial calms the run or confirms to people that something is wrong.',

  bdwage:
    'The wage board announcement landed at Shubarna Apparels in Gazipur in the middle of Eid bonus season, and the floor read it as the bonus being replaced rather than added on top. We want the response split across sewing line workers, line supervisors caught between both sides, Poshak Sromik Oikko organisers, and the Poshak Malik Forum, and we want to know where the sentence that actually moves the floor gets said. The client has to decide whether management speaks at the gate before the morning shift or lets the union carry the explanation.',

  bdhealth:
    'A rumour that every hospital bed in the city is full is spreading in the middle of dengue season, and Shapla General had four empty beds on the night the claim peaked. We need to see which households with a fever stop presenting at hospital altogether, what the para pharmacies are now being asked to answer, and how an undated corridor photograph became the proof everyone cites. The decision is whether the hospital publishes a nightly bed count or whether that reads as advertising during an outbreak.',

  india:
    'Wheat prices jumped across Gaya district in the week before the festival, and the fair price shops opened with visibly short stock. We want the response mapped across ration queue regulars, the ASHA volunteers who get asked first because they are known personally, and the family WhatsApp groups that move a shelf photo faster than any circular. The decision on the table is whether the district announces a stock guarantee now or holds the statement until supply is confirmed.',

  pakistan:
    'Flour rates moved sharply in Faisalabad with no relief plan announced, and the utility store queues formed before any official word. Watch the home-based embroidery workers, the power loom households cutting the evening roti count, and the masjid WhatsApp admins who decide which rumour is safe to forward. The client needs to know whether a relief announcement without a delivery date buys calm or makes the distrust worse.',

  srilanka:
    'Rice prices rose sharply in the hill country and estate households had already dropped a meal before anyone complained in public. We need the response traced across the estate line rooms, the daughters sending small transfers back from factory towns, and the union voices that only arrive after the shock has been absorbed privately. The question for the client is whether the relief notice will land as help or as proof that nobody was watching.',

  nepal:
    'Food prices have risen across remittance-dependent households in Sindhupalchok and the village shop counter is the only place the change is visible to everyone at once. Watch the women running the household budget in silence, the FCHV volunteers people actually stop and ask, and the migrant husbands still assuming the next transfer settles it. The client has to decide whether to communicate through the municipal relief desk or through the volunteers who are already trusted inside the ward.',
}

export function getSeedDocsForPack(packKey) {
  return DEMO_SEED_DOCS[packKey] || DEMO_SEED_DOCS[DEMO_DEFAULT_PACK_KEY]
}

export function getDraftedBrief(packKey) {
  return DEMO_DRAFTED_BRIEFS[packKey] || DEMO_DRAFTED_BRIEFS[DEMO_DEFAULT_PACK_KEY]
}
