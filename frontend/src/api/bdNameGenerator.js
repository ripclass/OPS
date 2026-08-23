// Bangladeshi persona name generator.
//
// Replaces the old first-name x surname grid, which produced things a
// Bangladeshi reader catches instantly: "Naeem Begum", "Mizanur" with nothing
// after it, a twenty-year-old student called Jobeda, and Begum on a third of
// the women. Every rule here comes from the compiled research dataset in
// ../content/bdNames.js; the short version of each rule is at the top of that
// file.
//
// Three properties this module must keep:
//
//   1. DETERMINISM. createProfiles() in demoRuntime.js is called on every poll
//      of the population, config and interview endpoints. The same agent index
//      must produce the same person every time, so every draw comes from a
//      PRNG seeded on (pack, index, segment, gender) and nothing else.
//   2. COHORT AGREEMENT. The name has to match the age. An elderly agent gets
//      Jobeda Khatun or Abdul Quddus; a student gets Tahmid Rayan or Mim.
//      Cohort is drawn from the segment, and the given-name pool is filtered
//      by it.
//   3. CROWD REALISM, not just per-name realism. A crowd is checked as a crowd:
//      no full name repeats, no single given name takes more than about two
//      percent, and the second element is not the same three words all the way
//      down.

import {
  ABDUL_CARRIERS,
  BARUA,
  CHRISTIAN,
  CHT,
  ENGLISH_WORD_NICKNAMES,
  FEMALE_DAAKNAM,
  FEMALE_GIVEN,
  FEMALE_SECOND,
  FEMALE_SECOND_BY_COHORT,
  FEMALE_SECOND_PRESENT,
  HINDU,
  MALE_DAAKNAM,
  MALE_GIVEN,
  MALE_SECOND,
  MD_FORMS,
  MST_FORMS,
  POETIC_DAAKNAM_ONLY,
  REGIONAL,
} from '../content/bdNames.js'

// ---------------------------------------------------------------------------
// Deterministic randomness
// ---------------------------------------------------------------------------

function hashSeed(text) {
  let hash = 2166136261
  const value = String(text)
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index)
    hash = Math.imul(hash, 16777619)
  }
  return hash >>> 0
}

function createRng(seedText) {
  let state = hashSeed(seedText) || 1
  return function next() {
    state += 0x6d2b79f5
    let t = state
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function pick(rng, list) {
  if (!list || !list.length) {
    return null
  }
  return list[Math.floor(rng() * list.length) % list.length]
}

function pickWeighted(rng, entries) {
  // entries: [[value, weight], ...]
  const total = entries.reduce((sum, entry) => sum + Math.max(entry[1] || 0, 0), 0)
  if (total <= 0) {
    return entries.length ? entries[0][0] : null
  }
  let roll = rng() * total
  for (const [value, weight] of entries) {
    roll -= Math.max(weight || 0, 0)
    if (roll <= 0) {
      return value
    }
  }
  return entries[entries.length - 1][0]
}

const TIER_WEIGHT = { very_common: 6, common: 3, occasional: 1 }

function pickByTier(rng, list) {
  return pickWeighted(rng, list.map(entry => [entry, TIER_WEIGHT[entry.t] || 1]))
}

// A crowd where every Hossain is spelled the same way is a tell, and treating
// Akter / Akhter / Aktar as three different names under-weights the name. So:
// sample the name first, then sample the romanization.
const ROMANIZATION_JITTER = 0.2

function romanize(rng, entry) {
  if (!entry) {
    return ''
  }
  if (entry.v && entry.v.length && rng() < ROMANIZATION_JITTER) {
    return pick(rng, entry.v)
  }
  return entry.n
}

// ---------------------------------------------------------------------------
// Cohort and register, derived from the segment the agent was allocated to
// ---------------------------------------------------------------------------

// older = born ~1955-1975, mid = ~1980-1995, young = ~2000-2008.
const COHORT_BY_SEGMENT = {
  rural: { older: 0.3, mid: 0.44, young: 0.26 },
  urban_working: { older: 0.12, mid: 0.45, young: 0.43 },
  middle_class: { older: 0.18, mid: 0.5, young: 0.32 },
  corporate: { older: 0.14, mid: 0.56, young: 0.3 },
  migration_workers: { older: 0.2, mid: 0.55, young: 0.25 },
  students: { older: 0, mid: 0.08, young: 0.92 },
  retailers: { older: 0.24, mid: 0.5, young: 0.26 },
  women: { older: 0.24, mid: 0.5, young: 0.26 },
  // No mid-cohort tail here: the elderly segment's occupations are retired
  // teacher and para committee elder, and a 33 year old retired teacher is a
  // worse artefact than a slightly narrow age band.
  elderly: { older: 1, mid: 0, young: 0 },
}

// Register decides the honorific rate, the -ul compound rate, whether Begum is
// on the table at all, and how much of the name survives into a display name.
const REGISTER_BY_SEGMENT = {
  rural: { rural_mass: 0.72, mofussil: 0.25, urban_educated: 0.03 },
  urban_working: { rural_mass: 0.48, mofussil: 0.44, urban_educated: 0.08 },
  middle_class: { rural_mass: 0.12, mofussil: 0.46, urban_educated: 0.42 },
  corporate: { rural_mass: 0.02, mofussil: 0.18, urban_educated: 0.8 },
  migration_workers: { rural_mass: 0.55, mofussil: 0.38, urban_educated: 0.07 },
  students: { rural_mass: 0.16, mofussil: 0.4, urban_educated: 0.44 },
  retailers: { rural_mass: 0.42, mofussil: 0.48, urban_educated: 0.1 },
  women: { rural_mass: 0.5, mofussil: 0.4, urban_educated: 0.1 },
  elderly: { rural_mass: 0.58, mofussil: 0.34, urban_educated: 0.08 },
}

const AGE_RANGE = { older: [52, 71], mid: [31, 47], young: [18, 29] }

// Share of display names that are a single word. Real, but rare.
const SINGLE_TOKEN_RATE = 0.06

function pickFromWeightMap(rng, weights, fallback) {
  const entries = Object.entries(weights || {})
  if (!entries.length) {
    return fallback
  }
  return pickWeighted(rng, entries)
}

// ---------------------------------------------------------------------------
// Per-pack naming profile
// ---------------------------------------------------------------------------

// region shifts the name-part pool, the Mst. rate and the Khatun weight.
// community is the religious mix. cht is deliberately zero for every shipped
// pack: none of them is set in Rangamati, Bandarban or Khagrachhari, and CHT
// names in a Gazipur factory crowd would be a fabrication. Give a hill-district
// pack cht: 0.2 and the Chakma, Marma and Tripura branches switch on.
export const DEFAULT_NAMING_PROFILE = {
  region: 'national',
  community: { muslim: 0.895, hindu: 0.085, barua: 0.012, christian: 0.005, cht: 0 },
}

function normalizeCommunityMix(mix) {
  const source = { ...DEFAULT_NAMING_PROFILE.community, ...(mix || {}) }
  const total = Object.values(source).reduce((sum, value) => sum + Math.max(value || 0, 0), 0)
  if (total <= 0) {
    return { ...DEFAULT_NAMING_PROFILE.community }
  }
  return Object.fromEntries(
    Object.entries(source).map(([key, value]) => [key, Math.max(value || 0, 0) / total])
  )
}

function resolveRegion(profile) {
  const region = profile?.region || 'national'
  if (region === 'sylhet') {
    return {
      key: region,
      nameParts: REGIONAL.sylhet.nameParts,
      hinduSurnames: REGIONAL.sylhet.hinduSurnames,
      mstRate: 0.02,
      begumFactor: 0.7,
      // Khatun is a west-and-north Bengal marker. In Sylhet it is close to
      // absent, and a Sylheti crowd full of Khatuns reads wrong.
      khatunFactor: 0.1,
      inheritedSurnameRate: 0.4,
    }
  }
  if (region === 'north_bengal') {
    return {
      key: region,
      nameParts: REGIONAL.northBengal.nameParts,
      hinduSurnames: REGIONAL.northBengal.hinduSurnames,
      mstRate: 0.12,
      begumFactor: 1,
      khatunFactor: 1.8,
      inheritedSurnameRate: 0.1,
    }
  }
  if (region === 'chattogram') {
    return {
      key: region,
      nameParts: REGIONAL.chattogram.nameParts,
      hinduSurnames: REGIONAL.chattogram.hinduSurnames,
      mstRate: 0.04,
      begumFactor: 1,
      khatunFactor: 0.7,
      inheritedSurnameRate: 0.3,
    }
  }
  return {
    key: 'national',
    nameParts: null,
    hinduSurnames: null,
    mstRate: 0.05,
    begumFactor: 1,
    khatunFactor: 1,
    inheritedSurnameRate: 0.22,
  }
}

// ---------------------------------------------------------------------------
// Pools, filtered once per module load
// ---------------------------------------------------------------------------

const byCohort = (list, cohort) => list.filter(entry => (entry.c || []).includes(cohort))

const POETIC_ONLY = new Set(POETIC_DAAKNAM_ONLY)

// Bristi, Srabon, Nodi, Prova, Antora. The community's own formulation is that
// the daak nam is Bengali while the name on paper is an Islamic one, so these
// are stripped out of the formal given slot for Muslim personas and reached
// only through the daak-nam pools. "Bristi Islam" on a document does not
// happen; "Nusrat Jahan Prova" does.
// Also strips poetic ROMANIZATIONS: Srabon is a spelling of Shaon, and letting
// the jitter reach for it would put a poetic name back in the formal slot
// through the back door.
const formalOnly = list => list
  .filter(entry => !POETIC_ONLY.has(entry.n))
  .map(entry => {
    if (!entry.v || !entry.v.some(variant => POETIC_ONLY.has(variant))) {
      return entry
    }
    return { ...entry, v: entry.v.filter(variant => !POETIC_ONLY.has(variant)) }
  })

const MALE_BY_COHORT = {
  older: formalOnly(byCohort(MALE_GIVEN, 'older')),
  mid: formalOnly(byCohort(MALE_GIVEN, 'mid')),
  young: formalOnly(byCohort(MALE_GIVEN, 'young')),
}
const FEMALE_BY_COHORT = {
  older: formalOnly(byCohort(FEMALE_GIVEN, 'older')),
  mid: formalOnly(byCohort(FEMALE_GIVEN, 'mid')),
  young: formalOnly(byCohort(FEMALE_GIVEN, 'young')),
}

const split = (list, predicate) => [list.filter(predicate), list.filter(entry => !predicate(entry))]

// Compound = the -ul / -ur family, which cannot stand without its completion.
// Carrier = the Abdul / Abdus / Abu / Golam family, which cannot stand without
// its prefix. Plain = everything that is a complete name on its own.
const MALE_POOLS = {}
for (const cohort of ['older', 'mid', 'young']) {
  const list = MALE_BY_COHORT[cohort]
  const [compound, rest] = split(list, entry => Boolean(entry.req))
  const [carrier, plain] = split(rest, entry => Boolean(entry.carrier))
  MALE_POOLS[cohort] = { compound, carrier, plain, all: list }
}

const FEMALE_DAAK_BY_COHORT = {
  older: byCohort(FEMALE_DAAKNAM, 'older'),
  mid: byCohort(FEMALE_DAAKNAM, 'mid'),
  young: byCohort(FEMALE_DAAKNAM, 'young'),
}
const MALE_DAAK_BY_COHORT = {
  older: byCohort(MALE_DAAKNAM, 'older'),
  mid: byCohort(MALE_DAAKNAM, 'mid'),
  young: byCohort(MALE_DAAKNAM, 'young'),
}

const FEMALE_SECOND_BY_NAME = Object.fromEntries(FEMALE_SECOND.map(entry => [entry.n, entry]))
const MALE_SECOND_BY_NAME = Object.fromEntries(MALE_SECOND.map(entry => [entry.n, entry]))

const HINDU_BY_COHORT = {
  male: {
    older: byCohort(HINDU.maleGiven, 'older'),
    mid: byCohort(HINDU.maleGiven, 'mid'),
    young: byCohort(HINDU.maleGiven, 'young'),
  },
  female: {
    older: byCohort(HINDU.femaleGiven, 'older'),
    mid: byCohort(HINDU.femaleGiven, 'mid'),
    young: byCohort(HINDU.femaleGiven, 'young'),
  },
}

// Honorifics are not names. Kept as a set so the crowd-level given-name cap
// counts the person, not the prefix in front of them.
const HONORIFIC_TOKENS = new Set([
  ...Object.keys(MD_FORMS),
  ...Object.keys(MST_FORMS),
  'Abdul', 'Abdus', 'Abdur', 'Abdun', 'Abu', 'Abul', 'Golam',
  'Sri', 'Sree', 'Srimoti', 'Srimati',
])

// Family-style elements a woman can carry in place of a gender marker
// (Sadia Islam, Farhana Chowdhury). Real, and the only route by which a Muslim
// woman in this generator gets something that looks like a surname.
const FEMALE_FAMILY_STYLE = ['Islam', 'Chowdhury', 'Ahmed', 'Rahman', 'Hossain', 'Haque', 'Khan']

// Rahman is reserved: it is the mandatory completion of an -ur given name and
// must never turn up as a free-floating name-part behind something else.
const MALE_SECOND_FREE = MALE_SECOND.filter(entry => !entry.reqPre)

// Miah encodes rural and older. It is not a Sylhet marker, and it does not
// belong on a twenty-two year old in Uttara.
const RURAL_OLDER_ONLY_PARTS = new Set(['Mia', 'Miah', 'Sardar', 'Fakir', 'Bepari', 'Matbar', 'Mridha'])

// The gendered tokens. Used by the sweep to prove no cross-gender pairs, and
// used here to stop a male given name ever reaching a female terminal.
// Bala is deliberately absent: it is a Hindu female medial AND a surname in its
// own right, so "Akash Bala" is a real man's name. Jahan is absent for the same
// kind of reason: "Shah Jahan" is a male given name that romanizes with a
// space in it.
export const FEMALE_ONLY_TOKENS = new Set([
  'Akter', 'Akhter', 'Aktar', 'Akther', 'Akhtar', 'Akthar', 'Khatun', 'Khaton', 'Khatoon',
  'Begum', 'Sultana', 'Khanam', 'Khanom', 'Banu', 'Nesa', 'Bibi', 'Bewa', 'Parvin',
  'Nahar', 'Yeasmin', 'Ara', 'Rani', 'Debi', 'Devi', 'Siddika',
  'Mst.', 'Mst', 'Most.', 'MST.', 'Mosammat', 'Musammat', 'Srimoti', 'Srimati',
])
export const MALE_ONLY_TOKENS = new Set([
  'Md.', 'Md', 'MD.', 'Mohammad', 'Mohammed', 'Muhammad', 'Mohd.', 'M.',
  'Abdul', 'Abdus', 'Abdur', 'Abdun', 'Abu', 'Abul', 'Golam',
  'Miah', 'Mia', 'Uddin', 'Ullah', 'Billah', 'Sheikh', 'Molla', 'Mollah', 'Sri', 'Sree',
])

// Only these six actually demand a following attribute. Syed, Sardar and Shah
// are listed with them in the research as carriers but are also ordinary
// terminal name-parts, so "Sohag Shah" is a complete name.
export const PREFIX_CARRIERS = new Set(['Abdul', 'Abdus', 'Abdur', 'Abdun', 'Abu', 'Abul', 'Golam'])

// ---------------------------------------------------------------------------
// Muslim names
// ---------------------------------------------------------------------------

function mdPrefixRate(cohort, register) {
  // Display-register rates, not document rates. A man whose NID says
  // "Md. Ariful Islam" posts as "Arif Khan".
  if (register === 'urban_educated') {
    return cohort === 'young' ? 0.04 : 0.1
  }
  if (register === 'mofussil') {
    return cohort === 'young' ? 0.14 : 0.26
  }
  return cohort === 'young' ? 0.2 : 0.34
}

function compoundRate(cohort, register) {
  // The -ul Islam compound is class and geography before it is age: strong for
  // rural and small-town men of any age under fifty, collapsed among elite
  // Dhaka under-thirties.
  if (register === 'urban_educated') {
    return cohort === 'young' ? 0.05 : 0.24
  }
  if (register === 'mofussil') {
    return cohort === 'young' ? 0.2 : 0.44
  }
  return cohort === 'young' ? 0.28 : 0.52
}

// The appended daak nam is what makes a name three tokens: Mehedi Hasan Sagor,
// Sharmin Akter Supta, Nusrat Jahan Riya. Old practice, newly visible in
// records: the 1999 cricket squad had 7 of 15 known by one and the press
// stripped them out; a 2024 youth squad prints them at 40 to 47 percent.
function daaknamAppendRate(cohort) {
  return cohort === 'young' ? 0.32 : cohort === 'mid' ? 0.22 : 0.08
}

function pickNamePart(rng, region, cohort, register) {
  const regional = region.nameParts || []
  const candidates = MALE_SECOND_FREE.filter(entry => {
    if (RURAL_OLDER_ONLY_PARTS.has(entry.n)) {
      return cohort !== 'young' && register !== 'urban_educated'
    }
    return true
  })
  const entries = candidates.map(entry => {
    let weight = TIER_WEIGHT[entry.t] || 1
    // A district-marked name-part is what makes a Sylhet crowd read as Sylhet.
    if (regional.includes(entry.n)) {
      weight *= 4
    }
    if (register === 'urban_educated' && ['Chowdhury', 'Khan', 'Rahman', 'Ahmed', 'Kabir', 'Karim'].includes(entry.n)) {
      weight *= 2
    }
    return [entry, weight]
  })
  return pickWeighted(rng, entries)
}

function buildMuslimMale(rng, ctx) {
  const { cohort, register, region } = ctx
  const pools = MALE_POOLS[cohort]
  const parts = []
  const marks = { md: false, namePart: false, uddinFamily: false, daak: false }

  const wantsMd = rng() < mdPrefixRate(cohort, register)
  if (wantsMd) {
    parts.push(pickFromWeightMap(rng, MD_FORMS, 'Md.'))
    marks.md = true
  }

  // Pure daak-nam display: no formal name at all, just the call name plus, most
  // of the time, a borrowed surname. "Sagor Khan", "Rana", "Shuvo Ahmed".
  const pureDaakRate = cohort === 'older' ? 0.03 : register === 'urban_educated' ? 0.16 : 0.13
  if (!wantsMd && rng() < pureDaakRate) {
    const daak = pick(rng, MALE_DAAK_BY_COHORT[cohort].length ? MALE_DAAK_BY_COHORT[cohort] : MALE_DAAKNAM)
    parts.push(daak.n)
    marks.daak = true
    if (rng() < 0.72) {
      const part = pickNamePart(rng, region, cohort, register)
      parts.push(romanize(rng, part))
      marks.namePart = true
    }
    return { parts, marks }
  }

  const carrierChance = cohort === 'older' && register !== 'urban_educated' ? 0.3 : cohort === 'older' ? 0.14 : 0.02
  const useCompound = rng() < compoundRate(cohort, register)

  if (pools.carrier.length && rng() < carrierChance) {
    // Abdul Quddus, Abdus Sattar, Abdur Rashid, Abul Kalam, Golam Rabbani.
    const attribute = pickByTier(rng, pools.carrier)
    const carrier = ABDUL_CARRIERS.includes(attribute.carrier) ? attribute.carrier : 'Abdul'
    parts.push(carrier)
    parts.push(romanize(rng, attribute))
  } else if (useCompound && pools.compound.length) {
    const given = pickByTier(rng, pools.compound)
    parts.push(romanize(rng, given))
    // Not optional. A bare "Mizanur", or a "Mizanur Islam", is the single
    // sharpest tell of a generated Bangladeshi name.
    const completion = pick(rng, given.req)
    const completionEntry = MALE_SECOND_BY_NAME[completion]
    parts.push(completionEntry ? romanize(rng, completionEntry) : completion)
    marks.namePart = true
  } else {
    const given = pickByTier(rng, pools.plain.length ? pools.plain : pools.all)
    parts.push(romanize(rng, given))
    if (given.solo) {
      marks.uddinFamily = true
      // -uzzaman, -uddin and -ullah are complete on their own. A second token
      // is allowed but never required.
      if (rng() < 0.22) {
        parts.push(romanize(rng, pickNamePart(rng, region, cohort, register)))
        marks.namePart = true
      }
    } else if (cohort === 'young' && register === 'urban_educated' && rng() < 0.42) {
      // Tahmid Rayan, Sadman Sami: two short modern given names and no
      // name-part at all. A real and rising Dhaka shape.
      const second = pickByTier(rng, MALE_POOLS.young.plain)
      parts.push(romanize(rng, second))
    } else if (rng() < 0.72) {
      parts.push(romanize(rng, pickNamePart(rng, region, cohort, register)))
      marks.namePart = true
    }
  }

  if (!marks.daak && rng() < daaknamAppendRate(cohort)) {
    const daak = pick(rng, MALE_DAAK_BY_COHORT[cohort].length ? MALE_DAAK_BY_COHORT[cohort] : MALE_DAAKNAM)
    parts.push(daak.n)
    marks.daak = true
  }

  // Two tokens is the mode for an ordinary crowd and one token is about two
  // percent of it. Without this the young pools, which drop the prefix and the
  // name-part together, leave far too many people on a single word.
  if (parts.length < 2 && rng() > SINGLE_TOKEN_RATE) {
    parts.push(romanize(rng, pickNamePart(rng, region, cohort, register)))
    marks.namePart = true
  }

  return { parts, marks }
}

function pickFemaleSecond(rng, cohort, register, region) {
  const table = FEMALE_SECOND_BY_COHORT[cohort] || FEMALE_SECOND_BY_COHORT.national
  const entries = Object.entries(table).map(([name, weight]) => {
    let value = weight
    if (name === 'Begum') {
      // Zero out of 138 urban Dhaka professionals carried Begum. It is a class
      // marker, and the reported bug was it landing on everybody. Damped hard
      // enough that it stays under five percent of women in every pack,
      // including Sylhet, where Khatun is suppressed and would otherwise push
      // its share of the remaining weight up.
      value = register === 'urban_educated' ? 0 : register === 'mofussil' ? value * 0.35 : value * 0.6
      value *= region.begumFactor
    }
    if (name === 'Khatun') {
      value *= region.khatunFactor
    }
    return [name, value]
  })
  const name = pickWeighted(rng, entries)
  const entry = FEMALE_SECOND_BY_NAME[name]
  return { name: entry ? romanize(rng, entry) : name, entry }
}

function buildMuslimFemale(rng, ctx) {
  const { cohort, register, region } = ctx
  const parts = []
  const marks = { md: false, namePart: false, uddinFamily: false, daak: false }

  const mstRate = register === 'urban_educated' ? region.mstRate * 0.2 : region.mstRate
  if (rng() < mstRate) {
    parts.push(pickFromWeightMap(rng, MST_FORMS, 'Mst.'))
    marks.md = true
  }

  const pool = FEMALE_BY_COHORT[cohort]
  const given = pickByTier(rng, pool.length ? pool : FEMALE_GIVEN)
  parts.push(romanize(rng, given))

  // A second given name, no gender marker at all. Umama Fatema, Tasnim
  // Tabassum. Common among young women and the main reason a modern crowd
  // should not be wall-to-wall Akter.
  const secondGivenRate = cohort === 'young' ? (register === 'urban_educated' ? 0.34 : 0.2) : 0.08
  let hasSecondGiven = false
  if (rng() < secondGivenRate) {
    // Same cohort pool as the first given name. Drawing the second from the
    // young pool regardless put "Ridita" and "Nawrin" on women in their forties.
    const second = pickByTier(rng, pool.length ? pool : FEMALE_GIVEN)
    if (second.n !== given.n) {
      parts.push(romanize(rng, second))
      hasSecondGiven = true
    }
  }

  let presentRate = FEMALE_SECOND_PRESENT[cohort] ?? 0.5
  if (register === 'urban_educated') {
    presentRate = Math.min(presentRate, FEMALE_SECOND_PRESENT.urban_professional ?? 0.32)
  }
  if (hasSecondGiven) {
    presentRate *= 0.5
  }

  let element = null
  if (rng() < presentRate) {
    const picked = pickFemaleSecond(rng, cohort, register, region)
    element = picked
    parts.push(picked.name)
    marks.namePart = true
  } else if (register !== 'rural_mass' && rng() < 0.22) {
    // The family-style element: Sadia Islam, Farhana Chowdhury.
    parts.push(pick(rng, FEMALE_FAMILY_STYLE))
    marks.namePart = true
  }

  // The appended daak nam is the distinctively Bangladeshi third token:
  // Sharmin Akter Supta, Nusrat Jahan Riya, Nishita Akter Nishi.
  let daakRate = daaknamAppendRate(cohort)
  if (!element) {
    daakRate *= 0.6
  }
  if (rng() < daakRate) {
    const englishRate = cohort === 'mid' ? 0.025 : cohort === 'young' ? 0.005 : 0
    if (rng() < englishRate) {
      parts.push(pick(rng, ENGLISH_WORD_NICKNAMES))
    } else {
      const daakPool = FEMALE_DAAK_BY_COHORT[cohort].length ? FEMALE_DAAK_BY_COHORT[cohort] : FEMALE_DAAKNAM
      parts.push(pick(rng, daakPool).n)
    }
    marks.daak = true
  }

  if (parts.length < 2 && rng() > SINGLE_TOKEN_RATE) {
    const roll = rng()
    if (roll < 0.62) {
      const picked = pickFemaleSecond(rng, cohort, register, region)
      parts.push(picked.name)
      marks.namePart = true
    } else if (roll < 0.85) {
      parts.push(pick(rng, FEMALE_FAMILY_STYLE))
      marks.namePart = true
    } else {
      const daakPool = FEMALE_DAAK_BY_COHORT[cohort].length ? FEMALE_DAAK_BY_COHORT[cohort] : FEMALE_DAAKNAM
      parts.push(pick(rng, daakPool).n)
      marks.daak = true
    }
  }

  return { parts, marks }
}

// ---------------------------------------------------------------------------
// Hindu names. The structure is not the Muslim one with different words.
// ---------------------------------------------------------------------------

// Banerjee, Mukherjee, Chatterjee, Ganguly, Bose, Basu and Guha are the West
// Bengal Kulin Brahmin and Kayastha signature. That stratum left at Partition,
// so these read Indian rather than Bangladeshi and are cut from the pool even
// though a couple of them survive in the source surname list.
const WEST_BENGAL_SIGNATURE = new Set(['Banerjee', 'Mukherjee', 'Chatterjee', 'Ganguly', 'Bose', 'Basu', 'Guha'])
const BD_HINDU_SURNAMES = HINDU.surnames.filter(entry => !WEST_BENGAL_SIGNATURE.has(entry.n))

const hinduSurnameCache = {}

function hinduSurnamePool(region) {
  if (hinduSurnameCache[region.key]) {
    return hinduSurnameCache[region.key]
  }
  const regional = new Set(region.hinduSurnames || [])
  const pool = BD_HINDU_SURNAMES.map(entry => [entry, (TIER_WEIGHT[entry.t] || 1) * (regional.has(entry.n) ? 5 : 1)])
  hinduSurnameCache[region.key] = pool
  return pool
}

function buildHindu(rng, ctx, gender) {
  const { cohort, register, region } = ctx
  const parts = []
  const pool = gender === 'female' ? HINDU.femaleGiven : HINDU.maleGiven
  const cohortPool = HINDU_BY_COHORT[gender === 'female' ? 'female' : 'male'][cohort]
  const given = pickByTier(rng, cohortPool.length ? cohortPool : pool)
  parts.push(given.n)

  if (gender === 'male') {
    // Chandra, Kumar, Lal. The highest-value realism lever for Hindu men:
    // nearly every man born pre-1960 carries one and essentially none of the
    // young ones do.
    const rate = cohort === 'older' ? 0.55 : cohort === 'mid' ? 0.22 : 0.05
    if (rng() < rate) {
      parts.push(pick(rng, HINDU.maleMiddle))
    }
  } else {
    // Rani sits MEDIAL, before the inherited surname. It is a class marker more
    // than a cohort one, so it survives in the youngest rural cohort.
    const base = register === 'urban_educated' ? 0.03 : 0.275
    const rate = cohort === 'older' ? base : cohort === 'mid' ? base * 0.7 : base * 0.35
    if (rng() < rate) {
      const middle = pickWeighted(
        rng,
        HINDU.femaleMiddle.map(entry => [entry, entry.n === 'Rani' ? 8 : cohort === 'older' ? 1 : 0])
      )
      parts.push(middle.n)
    }
  }

  parts.push(pickWeighted(rng, hinduSurnamePool(region)).n)
  return { parts, marks: { md: false, namePart: true, uddinFamily: false, daak: false } }
}

// ---------------------------------------------------------------------------
// Barua (Bengali Buddhist), Christian, and the hill-district branches
// ---------------------------------------------------------------------------

function buildBarua(rng, ctx, gender) {
  const { cohort } = ctx
  const parts = []
  parts.push(pick(rng, gender === 'female' ? BARUA.femaleGiven : BARUA.maleGiven))
  if (gender === 'male' && cohort !== 'young' && rng() < BARUA.kantiRate) {
    parts.push('Kanti')
  }
  parts.push(pickWeighted(rng, BARUA.surnames.map(entry => [entry.n, entry.t === 'very_common' ? 12 : 1])))
  return { parts, marks: { md: false, namePart: true, uddinFamily: false, daak: false } }
}

function buildChristian(rng, ctx, gender) {
  const parts = []
  parts.push(pick(rng, gender === 'female' ? CHRISTIAN.femaleGiven : CHRISTIAN.maleGiven))
  // Mixed English and Bengali given pairs are normal here, not exotic.
  if (rng() < 0.3) {
    const bengali = gender === 'female' ? ['Jharna', 'Shipra', 'Sathi', 'Bina', 'Dipali'] : ['Sanjib', 'Bimol', 'Nirmol', 'Sagar', 'Shuvo']
    parts.push(pick(rng, bengali))
  }
  const poolRoll = rng()
  const surnames = poolRoll < 0.45
    ? CHRISTIAN.surnamesPortuguese
    : poolRoll < 0.8
      ? CHRISTIAN.surnamesBengali
      : CHRISTIAN.surnamesClan
  parts.push(pick(rng, surnames))
  return { parts, marks: { md: false, namePart: true, uddinFamily: false, daak: false } }
}

// Raja, Rani and Dewan are administrative titles in the hill districts. Rani
// Kalindi was a ruling queen; Rani is not an ordinary Chakma given name.
const CHAKMA_FEMALE_GIVEN = CHT.chakma.femaleGiven.filter(name => name !== 'Rani' && name !== 'Raja')

function buildCht(rng, ctx, gender) {
  const roll = rng()
  if (roll < 0.5) {
    const pool = gender === 'female' ? CHAKMA_FEMALE_GIVEN : CHT.chakma.maleGiven
    const surname = pickWeighted(rng, CHT.chakma.surnames.map(entry => [entry.n, entry.t === 'very_common' ? 10 : entry.t === 'common' ? 3 : 1]))
    return { parts: [pick(rng, pool), surname], marks: { md: false, namePart: true, uddinFamily: false, daak: false } }
  }
  if (roll < 0.82) {
    // Marma names have no surname. The appended ethnonym on an NID is a state
    // ethnic classification, not a family name.
    const pool = gender === 'female' ? CHT.marma.femaleGiven : CHT.marma.maleGiven
    const parts = [pick(rng, pool)]
    if (rng() < CHT.marma.ethnonymRate) {
      parts.push('Marma')
    }
    return { parts, marks: { md: false, namePart: true, uddinFamily: false, daak: false } }
  }
  const pool = gender === 'female' ? CHT.tripura.femaleGiven : CHT.tripura.maleGiven
  const clan = rng() < 0.6 ? 'Tripura' : pick(rng, CHT.tripura.clans)
  return { parts: [pick(rng, pool), clan], marks: { md: false, namePart: true, uddinFamily: false, daak: false } }
}

// ---------------------------------------------------------------------------
// The exclusion filter
// ---------------------------------------------------------------------------

// A safety default recommended by the regional research: never emit a name
// shape that reads as Rohingya-coded, because a synthetic Bangladeshi crowd
// that produces one is producing a slur by accident. No Rohingya name pools
// exist in this generator; this catches the SHAPE, which is a Muslim name
// carrying no Bangladeshi structural marker at all: no Bengali name-part, no
// -uddin family token, no Akter family terminal, and no Md. prefix.
//
// The one Muslim shape that legitimately carries none of those is the young
// urban two-given-name pattern (Tahmid Rayan), so that is allowed explicitly
// and everything else regenerates.
function isUnmarkedMuslimShape(marks, ctx) {
  if (marks.md || marks.namePart || marks.uddinFamily || marks.daak) {
    return false
  }
  return ctx.cohort !== 'young'
}

function hasPoeticFormalMisuse(parts, marks) {
  // Bristi, Srabon and Nodi live in the daak-nam slot. "Bristi Islam" as a
  // formal name does not happen. Our pools keep them out of the given slot, so
  // this is a belt-and-braces check the sweep can assert on.
  if (!parts.length) {
    return false
  }
  return POETIC_ONLY.has(parts[0]) && marks.namePart
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

function pickCommunity(rng, mix) {
  const roll = rng()
  let cumulative = 0
  for (const key of ['muslim', 'hindu', 'barua', 'christian', 'cht']) {
    cumulative += mix[key] || 0
    if (roll < cumulative) {
      return key
    }
  }
  return 'muslim'
}

// Community is decided once, outside this function. Rebuilding a rejected name
// must not get another roll of the religion dice, or every rejected Muslim
// shape leaks a few percentage points into the Hindu share.
function buildForCommunity(rng, ctx, gender, community) {
  if (community === 'hindu') {
    return { community, ...buildHindu(rng, ctx, gender) }
  }
  if (community === 'barua') {
    return { community, ...buildBarua(rng, ctx, gender) }
  }
  if (community === 'christian') {
    return { community, ...buildChristian(rng, ctx, gender) }
  }
  if (community === 'cht') {
    return { community, ...buildCht(rng, ctx, gender) }
  }
  return {
    community,
    ...(gender === 'female' ? buildMuslimFemale(rng, ctx) : buildMuslimMale(rng, ctx)),
  }
}

/**
 * Builds one Bangladeshi identity. Deterministic in (packKey, index, segment,
 * gender): the same arguments always produce the same person.
 */
export function createBanglaIdentity({ packKey, index, gender, segmentKey, profile, salt = 0 }) {
  const naming = { ...DEFAULT_NAMING_PROFILE, ...(profile || {}) }
  const region = resolveRegion(naming)
  const communityMix = normalizeCommunityMix(naming.community)
  const rng = createRng(`${packKey}|${index}|${segmentKey}|${gender}|${salt}`)

  const cohort = pickFromWeightMap(rng, COHORT_BY_SEGMENT[segmentKey] || COHORT_BY_SEGMENT.middle_class, 'mid')
  const register = pickFromWeightMap(rng, REGISTER_BY_SEGMENT[segmentKey] || REGISTER_BY_SEGMENT.middle_class, 'mofussil')
  const ctx = { cohort, register, region, communityMix }
  // Community is drawn from its own stream, deliberately excluding the salt.
  // The crowd builder re-rolls a name when it collides or when a given name has
  // already taken its share of the crowd, and if those re-rolls could change
  // the religion, every rejected Muslim name would leak into the Hindu share.
  const community = pickCommunity(
    createRng(`${packKey}|${index}|${segmentKey}|${gender}|community`),
    communityMix
  )

  let built = buildForCommunity(rng, ctx, gender, community)
  let attempts = 0
  while (
    attempts < 6
    && community === 'muslim'
    && (isUnmarkedMuslimShape(built.marks, ctx) || hasPoeticFormalMisuse(built.parts, built.marks))
  ) {
    attempts += 1
    built = buildForCommunity(
      createRng(`${packKey}|${index}|${segmentKey}|${gender}|${salt}|retry${attempts}`),
      ctx,
      gender,
      community
    )
  }

  const [minAge, maxAge] = AGE_RANGE[cohort]
  const age = minAge + Math.floor(rng() * (maxAge - minAge))

  return {
    name: built.parts.filter(Boolean).join(' '),
    parts: built.parts.filter(Boolean),
    community: built.community,
    cohort,
    register,
    age,
  }
}

/**
 * Builds a whole crowd in one pass, so the crowd can be checked as a crowd.
 * Real crowds vary more than an unconstrained weighted draw does: no full name
 * repeats, and no single given name takes more than about two percent.
 */
export function createBanglaCrowd({ packKey, profile, members }) {
  const usedNames = new Set()
  const givenCounts = new Map()
  const total = members.length
  const givenCap = Math.max(3, Math.ceil(total * 0.02))

  return members.map(member => {
    let identity = null
    let fallback = null
    for (let salt = 0; salt < 14; salt += 1) {
      const candidate = createBanglaIdentity({ packKey, profile, salt, ...member })
      if (!fallback) {
        fallback = candidate
      }
      const key = candidate.name.toLowerCase()
      const givenKey = candidate.parts.find(part => !HONORIFIC_TOKENS.has(part)) || candidate.parts[0] || ''
      const count = givenCounts.get(givenKey) || 0
      if (!usedNames.has(key) && count < givenCap) {
        identity = candidate
        givenCounts.set(givenKey, count + 1)
        break
      }
    }
    const chosen = identity || fallback
    usedNames.add(chosen.name.toLowerCase())
    return chosen
  })
}
