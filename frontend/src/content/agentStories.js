export const COUNTRY_MAP = {
  BD: 'bangladesh',
  IN: 'india',
  PK: 'pakistan',
  LK: 'srilanka',
  NP: 'nepal',
}

export const GLOBAL_ROTATION_ORDER = [
  'bangladesh',
  'pakistan',
  'srilanka',
  'nepal',
  'india',
]

export const AGENT_STORIES = {
  bangladesh: {
    key: 'bangladesh',
    code: 'BD',
    name: 'Halima',
    imagePath: '/landing/halima-hero.webp',
    imageAlt: 'Halima portrait',
    eyeMarker: {
      top: '21%',
      left: '23%',
      width: '52%',
      height: '8%',
      rotate: '-1deg',
    },
    headlineName: 'Halima, 41.',
    headlineMeta: 'Noakhali. Fish drying worker.',
    scribbles: [
      {
        text: 'MURMUR KNOWS\nHALIMA',
        className: 'scribble--top-left scribble--xl',
        target: 'shell',
      },
      {
        text: 'NO POST /\nNO PROTEST',
        className: 'scribble--copy-shoulder scribble--md',
        target: 'copy',
      },
      {
        text: 'CASCADE\nNO ONE\nMEASURES',
        className: 'scribble--in-image scribble--lg scribble--accent',
        target: 'media',
      },
      {
        text: 'REMITTANCE /\nSKIPPED MEAL /\nSILENCE',
        className: 'scribble--under-image scribble--xs',
        target: 'belowMedia',
      },
    ],
    bodyParagraphs: [
      'Her husband went to Saudi Arabia three years ago. He sends 25,000 taka a month through bKash. She has two daughters in school and a mother-in-law with diabetes. She shares nothing on Facebook.',
      "When the rice price hits, she won't post. She won't protest. She'll cut her own meals to one a day and tell no one. She is the cascade no one measures. We built a system that knows Halima exists.",
    ],
    bodyLines: [
      'Her husband went to Saudi Arabia three years ago.',
      'He sends 25,000 taka a month through bKash.',
      'She has two daughters in school and a mother-in-law with diabetes.',
      'She shares nothing on Facebook.',
      "When the rice price hits, she won't post. She won't protest.",
      "She'll cut her own meals to one a day and tell no one.",
      'She is the cascade no one measures.',
      'We built a system that knows Halima exists.',
    ],
  },
  india: {
    key: 'india',
    code: 'IN',
    name: 'Phulwanti Devi',
    headlineName: 'Phulwanti Devi, 38.',
    headlineMeta: 'Gaya district, Bihar. NREGA worker and ASHA volunteer.',
    scribbles: [
      {
        text: 'INFRASTRUCTURE\nNO POLICY\nSEES',
        className: 'scribble--top-left scribble--xl',
      },
      {
        text: 'ration line 5am',
        className: 'scribble--top-right scribble--sm',
      },
      {
        text: 'volunteer /\nworker /\nlife',
        className: 'scribble--bottom-right scribble--lg',
      },
    ],
    bodyLines: [
      'Her husband does construction in Surat. He sends Rs 5,000 a month through PhonePe.',
      "She earns Rs 200 a day on NREGA when the work is available - it hasn't been for three months.",
      'She walks four kilometres every morning to check on pregnant women in six villages.',
      'The government calls her a volunteer. She calls it her life.',
      "When the wheat price hits, she won't post on social media. She's never posted.",
      "She'll walk to the ration shop at 5am to stand in line before the stock runs out.",
      "If there's no stock, she'll feed her children and skip her own meal.",
      "Then she'll go check on the pregnant women anyway.",
      'She is the infrastructure no policy paper sees.',
      'We built a system that knows Phulwanti exists.',
    ],
  },
  pakistan: {
    key: 'pakistan',
    code: 'PK',
    name: 'Nasreen',
    headlineName: 'Nasreen, 33.',
    headlineMeta: 'Faisalabad. Home-based phulkari embroidery worker.',
    scribbles: [
      {
        text: 'SILENCE HOLDS\nTHE HOUSE',
        className: 'scribble--top-left scribble--xl',
      },
      {
        text: 'Quran verse /\npatience /\nrelief rumor',
        className: 'scribble--bottom-right scribble--lg',
      },
    ],
    bodyLines: [
      "Her husband works the power loom twelve hours a day. She sells embroidery through a WhatsApp group her sister-in-law started. Together they earn Rs 40,000 a month. Rent is Rs 22,000. Her son goes to a government school. Her daughter goes to a madrasa because it's free.",
      "She voted PTI but will never say so at the factory where her husband's seth supports PML-N.",
      "When the flour price hits, she won't post about politics. She'll post a Quran verse about patience. Then she'll message three women in the WhatsApp group to ask if anyone has heard about a government relief scheme. No one will have heard. She'll reduce the evening roti from three per person to two and hope her husband doesn't notice.",
      'She is the silence that holds a household together.',
      'We built a system that knows Nasreen exists.',
    ],
  },
  srilanka: {
    key: 'srilanka',
    code: 'LK',
    name: 'Selvamani',
    headlineName: 'Selvamani, 42.',
    headlineMeta: 'Nuwara Eliya. Tea plucker.',
    scribbles: [
      {
        text: '200 YEARS\nUNANSWERED',
        className: 'scribble--top-left scribble--xl',
      },
      {
        text: 'Rs 1,350 / 250kg',
        className: 'scribble--top-right scribble--sm',
      },
      {
        text: 'despair\nnot anger',
        className: 'scribble--bottom-right scribble--lg',
      },
    ],
    bodyLines: [
      'She earns Rs 1,350 a day picking tea leaves on an estate her grandmother also picked.',
      'She lives in a line room built in 1920 - ten feet by twelve feet, five people, one shared latrine for the row.',
      'Her eldest daughter left for a garment factory in Katunayake. She sends Rs 5,000 a month.',
      "Her son is studying for A-Levels. He is the family's one chance.",
      "When the rice price hits, she won't rage. She has no political vocabulary for rage.",
      "She'll do the arithmetic - Rs 1,350 minus Rs 250 per kilo times five mouths - and the numbers won't resolve.",
      "She'll feed the children first. Then her husband. Then her mother-in-law.",
      "She'll eat what's left.",
      'She is the two hundred years no one has answered for.',
      'We built a system that knows Selvamani exists.',
    ],
  },
  nepal: {
    key: 'nepal',
    code: 'NP',
    name: 'Kalpana Tamang',
    headlineName: 'Kalpana Tamang, 38.',
    headlineMeta: 'Sindhupalchok. Farmer, goat keeper, FCHV health volunteer.',
    scribbles: [
      {
        text: 'ECONOMY OF\nSILENCE',
        className: 'scribble--top-left scribble--xl',
      },
      {
        text: 'Qatar /\ntransfer /\nroof still leaks',
        className: 'scribble--bottom-right scribble--lg',
      },
    ],
    bodyLines: [
      'Her husband went to Qatar through a Kathmandu manpower agency three years ago.',
      'He paid Rs 250,000 to the agent - borrowed from a moneylender at 36% interest.',
      'He sends Rs 30,000 a month. It used to cover everything.',
      'Her house was cracked in the earthquake. The reconstruction grant fixed the walls but the roof still leaks.',
      'She video-calls him every evening at eight.',
      "When the rice price hits, she'll do what she always does - absorb it.",
      "She'll switch from rice to maize for three meals a week.",
      "She'll delay her son's school uniform purchase by a month.",
      "She'll tell her husband everything is fine.",
      "She won't tell him she hasn't bought her own blood pressure medication in six weeks.",
      'She is the economy that runs on silence and bKash and faith that the transfer will come on the fifteenth.',
      'We built a system that knows Kalpana exists.',
    ],
  },
}

export const AGENT_FEED_POSTS = [
  {
    meta: 'BD · Bangla · garments worker · Gazipur',
    language: 'bengali',
    content: 'আজকে বাজারে গিয়ে কাঁদছিলাম। চাল ৮০ টাকা কেজি। আমার বেতন ১২,০০০।',
  },
  {
    meta: 'PK · Urdu · textile worker · Faisalabad',
    language: 'arabic',
    content: 'چاول 40% بڑھا، آٹا 35%، بجلی ڈبل، گیس غائب۔ عمران خان جیل میں، ملک تباہ۔',
  },
  {
    meta: 'LK · Tamil · tea plucker · Nuwara Eliya',
    language: 'tamil',
    content: 'Rs 1,350 ÷ Rs 250/kg = 5.4 kg. 5 people. ஒரு நாள் வேலையில ஒரு kg அரிசி வாங்க முடியாது.',
    tone: 'mono',
  },
  {
    meta: 'NP · Nepali · wife · Sindhupalchok',
    language: 'devanagari',
    content: 'बुढालाई भन्नु पर्छ - तर कसरी भन्ने? उहाँ त्यहाँ गर्मी मा काम गर्दै हुनुहुन्छ। 😢',
  },
  {
    meta: 'IN · Hindi · Swiggy rider · Delhi',
    language: 'latin',
    content: 'Ek din ki kamaai mein khaana bhi nahi milega. 😤',
  },
  {
    meta: 'PK · Sindhi · voice message transcription',
    language: 'latin',
    content: '[voice message - Lakhi, 40, Tharparkar] "Sahib ji, gehun ka daam itna badh gaya..."',
  },
  {
    meta: 'LK · English · IT professional · Colombo',
    language: 'latin',
    content: 'Sorry Sri Lanka. 💔 Applying for the skilled visa tomorrow.',
  },
  {
    meta: 'BD · Bangla · student · Dhaka University',
    language: 'bengali',
    content: '#খাদ্যসংকট We did not bleed in July for THIS.',
  },
]

export const WHAT_IT_KNOWS = [
  'A garments worker in Chittagong EPZ is a migrant from Noakhali - not a local woman. A local middle-class Chatgaayan woman in a garment factory faces social ruin. The migrant does not. Same factory. Same city. Two completely different people. Every other simulation treats them as one.',
  '3.5 million Indian women classified as volunteers run the public health system on less than minimum wage. They are trained, politically organized, and angry enough to strike for a hundred days. They are the most important node in any health campaign simulation. No other system even has them as a category.',
  'An Ahmadi engineer in Lahore cannot say Assalamu Alaikum without risking arrest. His entire digital presence is concealment. His silence is not disengagement. It is survival strategy encoded at the identity level. Miss that and your Pakistan simulation is fiction.',
  "A Nepali wife in Sindhupalchok manages the farm, the goats, the school fees, the mother-in-law's medication, and the moneylender - on Rs 30,000 a month from Qatar that used to cover everything and no longer does. She is not unemployed. She is the economy. No labor survey counts her.",
  'Selvamani the tea plucker earns Rs 1,350 a day. Rice is Rs 250 a kilo. She has five people in a room built by the British for workers they considered less than permanent. She responds to a price shock with despair. Not anger. Despair is the correct emotion for someone with two hundred years of inherited powerlessness and no political vocabulary for rage.',
]

export const WHAT_IT_DOES = [
  "You describe a scenario. A policy announcement. A price shock. A flood warning that may or may not be believed. A health campaign targeting women who won't come to the clinic. An election narrative before it's deployed.",
  "Murmur generates the population that will receive it. Not a segment. Not a demographic average. Specific people with names, dialects, income sources, shame thresholds, political affiliations they will never say out loud, and fears that shape everything they do.",
  'It runs the scenario through them. Hour by hour. WhatsApp voice message to Facebook post to bazaar rumor to family phone call to silence that spreads faster than noise.',
  'It shows you what 750 people do - in their languages, with their emotions, at their speeds, through their networks - with cascade architecture, amplifier identification, and the specific behavioral math of who shares and who absorbs and why.',
  'Before it happens to you.',
]

export const WHO_ITS_FOR_INTRO = [
  "You have a decision that will reach millions of people whose names you don't know, whose languages you don't speak, whose fears you have never felt, whose silence you cannot measure.",
  'You need to know what they will do before you make it.',
]

export const WHO_ITS_FOR_LINES = [
  'A government about to cut a subsidy.',
  "A health campaign that will fail if it doesn't reach the women who distrust the clinic.",
  'A disaster warning in a language the affected population does not trust.',
  'A price shock hitting five countries in the same week with no relief plan.',
  'A brand entering a market where the wrong word triggers a boycott in forty minutes.',
]

export const WHO_ITS_FOR_OUTRO = 'Murmur is the rehearsal. What happens in the simulation before it happens in the street, the feed, or the ministry\'s inbox.'

export const LEGITIMACY_LINES = [
  'Built in Dhaka. Five countries. Hundreds of zones.',
  '1,200 hours of recorded conversation. 25 years of documentary fieldwork.',
  'From inside South Asia. Not pointed at it.',
  'Private. Paid. High-context. Not a chatbot.',
]
