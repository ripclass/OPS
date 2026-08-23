// Report and interview content for the bdhealth scenario pack.
// Dengue season in Dhaka, a beds full rumour, and the fictional Shapla General.
//
// Split out of demoFlowPacks.js because the report is the meeting-room
// artefact and it is long. Section paragraphs are rendered as markdown, so
// ### subheads, **bold** leads and - bullets all work.
//
// TWO AUTHORING RULES FOR THIS FILE AND ITS SIBLINGS:
//
//   1. No em dashes and no en dashes anywhere in user-visible text.
//   2. Never write the word "her" or "hers" in an interview response. The
//      runtime rewrites a scripted answer to the gender of whoever is actually
//      being interviewed, and possessive "her" is indistinguishable from
//      objective "her", so it comes out as "him sister" on a male agent. Use
//      "his" and "him"; both convert correctly in either direction.

export const BDHEALTH_REPORT = {
  reportSections: [
    {
      title: 'Phase by phase: what the cascade actually did',
      paragraphs: [
        'The run covers forty rounds. The first household decides not to come at round nine. The hospital finds out at round thirty-five, when that decision arrives at the front desk as a patient on day eight of a dengue fever. Everything in this report sits in that gap.',
        '**Rounds 1 to 8. The photograph, and the joke that outruns it.** At round two a corridor image enters a building committee group. It has no date, no facility name and no source, and the person forwarding it says plainly that he does not know who took it. That is not a weakness of the claim, it is the format: it is passed on as care rather than as assertion, which is a thing a household cannot argue with and an official denial cannot displace. At round five a health meme page compares looking for a hospital bed to looking for parking in Dhaka, and the joke reaches people the photograph never would.',
        '**Rounds 9 to 18. Care seeking relocates.** At round nine Shefa is on day five of a fever with two children and decides not to go, because a night on a corridor floor is worse than another day of paracetamol. She buys saline and napa and starts writing temperatures in a notebook. At round thirteen Masum reports the counter selling three times the usual paracetamol and saline, and customers asking him what a platelet count means. He is not a clinician, and he is the only person in the conversation. At round seventeen Arafat, who carries the sick for a living, repeats what a passenger told him about being turned away, and the stand adopts it as the state of the city.',
        '**Rounds 19 to 30. The inversion.** At round twenty-one Tania counts four empty beds on the night ward at Shapla General on a night the whole city is certain there are none, and has no route by which to say so that anyone outside the building would hear. At round twenty-six a counter sells a fourth day of paracetamol to the same household and advises a platelet test, and that advice is the only clinical triage that patient receives. At round thirty the district health office publishes bed availability by facility. It is accurate, it is public, and it is opened by journalists and by nobody with a fever at home.',
        '**Rounds 31 to 40. The cost lands in the wrong column.** At round thirty-five a household that should have presented on day four arrives on day eight, in poor condition. The delay was caused by a rumour and the file records late presentation. At round thirty-nine Shapla General posts that beds are available. It reaches the people who were always going to come. The households that already decided see no reason to check again, because as far as they are concerned the matter was settled two weeks ago.',
      ],
    },
    {
      title: 'Segment by segment: who moved, and in which direction',
      paragraphs: [
        '### Households with a fever at home',
        'The lane the whole scenario is about and the one that produces no record of any kind. The decision is taken at home, at night, by two people, and it is not a refusal of care: it is a substitution of care, made on the belief that the hospital has nothing to offer tonight. It happens once and then holds, because a household that has already committed to managing a fever at home does not revisit the decision daily. In this run the movement in this lane is complete by round eighteen and nothing after that changes it.',
        '### Mothers watching a fever chart',
        'The decision layer inside that lane. The chart in the notebook is the entire clinical record for four days: times, temperatures, doses. It is careful, disciplined work done by somebody with no training and no way to know what to escalate on. The characteristic pattern in this run is a mother choosing the saline over the taxi fare, not out of poverty alone, but because a wasted trip costs the money and the night and the two children left at home.',
        '### Para pharmacy counters',
        'The earliest and most accurate instrument in the run, and the only one holding a number. Masum sees three times the usual paracetamol and saline volume days before any hospital number moves, and he sees it as retail rather than as epidemiology. He is also, by default, the triage service: households ask him what a platelet count means, and he answers, because refusing to answer would leave them with nobody. The counter keeps no register, so none of this exists anywhere afterwards.',
        '### Hospital ward staff',
        'Correct, present, and structurally mute. Tania can see the beds the city says are gone. She has no channel that reaches a building committee group, no standing to post it, and no reason to believe anyone outside would take a nurse account of occupancy over a photograph. The most valuable true fact in the run is held all week by the people with the least ability to distribute it.',
        '### Rickshaw stands and the people who carry the sick',
        'The unrecognised relay. This lane physically transports patients and therefore holds a running sample of what happened to the last twenty people who tried. That sample is not statistical, it is the most recent anecdote, and it is repeated with total confidence. One passenger turned away at midnight becomes the state of every hospital, and it becomes that inside a network that talks to every household in the para.',
        '### Building and para committees',
        'The distribution system. The photograph moves because a committee group is where people put things that others should know, and because forwarding a warning costs nothing and refusing to forward it feels careless. These groups have no institution in them, so a correction has no way in unless a person already in the group carries it.',
        '### Health meme pages and the health office',
        'Two lanes at opposite ends and neither one changes a household. The meme page has the reach and no clinical content, and it extends the claim past the point where anyone remembers the photograph. The district health office has the correct occupancy data, publishes it accurately, and reaches journalists. Between them they generate almost all of the visible activity in this run and almost none of the behaviour.',
      ],
    },
    {
      title: 'THE SILENCE LANE: the households that never arrive, and the four days added to the fever',
      paragraphs: [
        'This is the finding. Everything else in this report is context for it.',
        'The hospital does not lose the patients who argue at the front desk. It loses the ones who never walk in. In this run the entire event happens in living rooms between nine at night and midnight, in conversations with no institution present, and it produces no complaint, no call, no post and no cancelled appointment, because there was never an appointment. A decision not to seek care leaves no trace at the place the care was not sought. The scenario is at its most dangerous precisely where it is least observable.',
        '**What the silence is made of.** Three things. First, there is no counterparty: nobody turned you away, you simply did not go, so there is nothing to report and nobody to report it to. Second, the arithmetic of a wasted trip. A night on a corridor floor, the fare both ways, and the children left at home are all certain costs, while the benefit of going is uncertain, so the household rationally buys another day of saline and waits for clarity that will not come. Third, the decision is framed as care rather than as avoidance: the family is treating the fever, keeping a chart, buying the medicine the counter recommends. Nobody in that house believes they are refusing treatment, which is why nobody in that house ever seeks a second opinion on the decision.',
        '**Where it is nevertheless visible.** The lane leaves four traces and not one of them is in a listening tool. Paracetamol and saline volume at para pharmacy counters, which triples days before any hospital number moves. Walk-in platelet tests at small diagnostic labs, ordered by nobody and paid for in cash. Night trips at rickshaw stands, which fall, and then spike late and in worse condition. And the day of illness at presentation, which drifts from four to eight while admissions stay flat or fall.',
        '**How the evidence gets destroyed.** This is the part that matters most and is easiest to miss. When the household finally arrives on day eight, the clinician writes late presentation in the file, and that phrase is medically accurate and causally empty. The rumour has just been converted into a patient characteristic. Every audit afterwards will read a record showing that patients presented late, and none will read a record showing that a photograph nobody could date persuaded a whole para to wait four extra days. The single most expensive thing in this run erases itself on entry.',
        '**Why it outlasts the visible conversation.** The meme page loses interest after round twenty. The photograph stops circulating. Neither of those events reaches the household that already decided, because that household is not waiting for an update, it has closed the question. A family that managed one fever at home will manage the next one at home too, and the belief transmits sideways to neighbours as experience rather than as rumour, which is a much harder thing to correct. Stand the response down when the mentions fall and you leave the behaviour running for the rest of the season.',
      ],
    },
    {
      title: 'Amplifier profiles: the four accounts that decided the reach',
      paragraphs: [
        '### The building committee group forward',
        'The origin node and the most benign. The image arrives with the honest admission that nobody knows who took it, and it is forwarded anyway, because in a building group a warning that turns out to be nothing costs the sender nothing and a warning withheld costs him everything. Reach is small and total: every flat, all at once, from somebody whose name is known. This is also the only group in the run that a correction could travel through, and no facility has a person in it.',
        '### The health meme page',
        'Highest reach, zero clinical content, and the reason the claim survives the photograph. The parking joke at round five is funny because it is recognisable, and recognisability is a more durable transport mechanism than evidence. It is not campaigning against any hospital and holds no position it would have to defend. Given something accurate and equally shareable it will move that just as fast, which makes it the cheapest distribution in the scenario and the one nobody approaches.',
        '### The rickshaw stand organiser',
        'The most underrated actor in the run. Arafat is not spreading a rumour, he is reporting the last thing that happened to a passenger, which he considers, reasonably, to be first-hand knowledge. His sample size is one and his confidence is complete, and he is consulted by households at the precise moment of decision, standing at the gate at eleven at night. No public health communication in this country is addressed to him and he decides more journeys than any of it.',
        '### The para pharmacy counter',
        'An amplifier by accident and the highest-trust node in the run. Masum did not start anything and does not want the role, but when a household asks whether the hospitals are full he answers, because he answers everything else they ask. He is simultaneously the best surveillance sensor available and the most efficient possible correction channel, and he is currently pointed the wrong way, repeating the rumour to the exact people who could still act on the truth.',
      ],
    },
    {
      title: 'Trust map: who is believed, by whom, about what',
      paragraphs: [
        'Trust in this run is not a number about the hospital. It is a map of who is believed about which kind of claim, and the layers barely overlap.',
        '**About whether beds exist tonight, the last person who went is believed, and nobody else is.** One passenger turned away at midnight outranks a published occupancy table, because at the moment of decision a household wants testimony rather than data. This is the layer the whole cascade runs on.',
        '**About what to do with the fever, the pharmacy counter is believed.** It is two lanes away, it is open, it has seen a lab report before, and it does not charge for the conversation. In this run the counter is the primary care system for four extra days and every party involved knows it is not one.',
        '**About occupancy figures, journalists believe the district health office and households do not read it.** The notice at round thirty is correct and well made. Trust is not the problem with it; distribution is. Nobody deciding at eleven at night whether to move a child opens a facility-level availability table.',
        '**About the hospital speaking for itself, credibility is structurally low.** A hospital saying it has beds is a hospital advertising, and everyone hears it that way. Shapla General is the only party with the number and the last party that will be believed about it, which is why the number has to be carried by somebody else.',
        '**About the ward, nobody is asked.** Tania is the most reliable witness in the run and holds no channel at all. The correct fact exists inside the building every single night of this scenario.',
        'The practical reading: the hospital does not have a credibility problem, it has a witness problem. What travels here is testimony from a known person, and the institution has not put its number into the hands of a single one of them.',
      ],
    },
    {
      title: 'What your dashboard will show, and why it is wrong',
      paragraphs: [
        'Through the middle of this run every number the hospital watches looks acceptable, and each of them is true.',
        '- **Admissions are flat or falling.** In the second week of a dengue season that reads as the season easing. It is the opposite: presentations are falling because people stopped coming, and a falling admission line in a rising season is the worst number in this report.',
        '- **Front desk complaints are near zero.** Nobody complains about a hospital they did not go to. The complaint log measures the experience of people who arrived, which in this scenario is exactly the population that was never at risk of staying away.',
        '- **Social mentions spike at round five and decay after round twenty.** The decay is a meme page losing interest. No household reversed a decision in that window, and nothing in the mention curve corresponds to anybody deciding to come in.',
        'One number to hold onto: mean day of illness at presentation moves from four to eight while admissions stay flat. That single figure describes the entire event, it is already being collected on every admission form in the building, and nobody reads it as a communications metric.',
      ],
    },
    {
      title: 'Recommendations',
      paragraphs: [
        '**1. Instrument twenty para pharmacy counters, not the timeline.** Paracetamol and saline volume, plus a tally of platelet questions, reported twice a week by twenty counters, turns days before any hospital number does. It is the cheapest early warning system available in this scenario and the one nobody builds, and the counters will do it for a phone call.',
        '**2. Read day of illness at presentation as a communications metric.** It is already on the admission form. Plot it weekly against admissions. When the mean drifts from four to eight, that is not a clinical trend, it is a rumour, and it is the only quantitative proof of one you will ever get.',
        '**3. Put the bed count for tonight in the hands of the counter and the rickshaw stand.** One number, sent daily by SMS to every pharmacy and every stand within three kilometres, written so it can be read out loud. These are the two people a household actually asks at eleven at night, and both are currently answering with the last thing they heard.',
        '**4. Answer the fear, not the claim.** Saying beds are available does not address what the household is actually avoiding, which is a night on a corridor floor and a wasted fare. Say what happens when you arrive: how the triage works, how long the wait is, and what it costs. The claim is about beds and the decision is about the corridor.',
        '**5. Get a named person into the committee groups.** The photograph moved through building and para groups and a hospital post cannot follow it there. One ward staff member or one community health worker, present in those groups by name before the season starts, gives a correction the only route it has.',
        '**6. Keep measuring for six weeks after the noise stops.** The visible conversation ends around round twenty. The habit of managing a fever at home does not, and it passes to neighbours as experience rather than as rumour, which is much harder to reverse. Set the review point well past the point where the dashboard looks calm.',
      ],
    },
  ],

  reportAgentAnswers: {
    first: 'The earliest signal is an undated corridor photograph forwarded into a building committee group at round two, with the honest note that nobody knows who took it. It is shared as care rather than as a claim, which is the format that cannot be argued with. The first behavioural move follows at round nine, when a household on day five of a fever decides not to come.',
    spread: 'It spreads through the people who carry the sick and the people who sell the medicine. A rickshaw stand repeats what the last passenger said, a building group forwards a warning because withholding one feels careless, and at round five a meme page turns the whole thing into a parking joke that reaches everyone the photograph never did.',
    trust: 'Trust splits by the hour of the question. About whether beds exist tonight, the last person who went is believed and nobody else is, because at eleven at night a household wants testimony rather than data. About what to do with the fever, the pharmacy counter is believed. About occupancy figures, journalists believe the health office and households never open it, and a hospital saying it has beds is heard as advertising.',
    quiet: 'The silence lane is care seeking itself. Households never arrive, so there is no complaint, no call and no cancelled appointment, because there was never an appointment. The fever is managed for four extra days at a para pharmacy counter that keeps no register, and when the patient finally comes in on day eight the file records late presentation, which is medically accurate and causally empty. The rumour erases itself from the record of what happened.',
    retail: 'The para pharmacy counter is the earliest and most accurate instrument in the run. Masum sees paracetamol and saline triple days before any hospital number moves, and he sees it as retail rather than as epidemiology. He is also the triage service by default, answering platelet questions he is not qualified to answer because refusing would leave the household with nobody at all.',
    women: 'Mothers watching the fever chart are the decision layer. The notebook of times and temperatures is the entire clinical record for four days, kept carefully by somebody with no training and no way to know what to escalate on. The choice is the saline over the taxi fare, and it is made not only on cost but on the certainty of the wasted night against the uncertainty of the benefit.',
    young: 'The health meme page carries the reach and none of the risk. The parking joke at round five is funny because it is recognisable, and recognisability travels further than evidence. It holds no position it would have to defend, which means it will carry something accurate and equally shareable at exactly the same speed. It is the cheapest distribution in the scenario and nobody has approached it.',
    timeline: 'Four phases across forty rounds. Rounds one to eight are the undated photograph and the joke that outruns it. Rounds nine to eighteen are the relocation of care to the pharmacy counter and the rickshaw stand. Rounds nineteen to thirty are the inversion, with four empty beds at Shapla General on a night the city is certain there are none, and an accurate occupancy notice read by journalists. Rounds thirty-one to forty are a day eight admission written up as late presentation and a clarification that reaches the people who were always coming.',
    compare: 'Compare the lane with the reach and the lane with the fever. The meme page and the health office produced almost all of the visible activity in this run between them and changed nobody. The building group and the rickshaw stand produced almost no measurable content and decided every journey that was not taken.',
    worst: 'The biggest risk is reading falling admissions as the season easing. Admissions fall in this run because people stopped coming, and a falling admission line in a rising dengue season is the worst number in the report. Stand the response down when the mentions decay and the habit of managing a fever at home runs for the rest of the season, passing to neighbours as experience rather than as rumour.',
    recover: 'Recovery runs through the counter and the stand, not through a post. Send the bed count for tonight by SMS to every para pharmacy and rickshaw stand within three kilometres, written so it can be read out loud, because those are the two people a household actually asks at eleven at night. And answer the fear rather than the claim: what people are avoiding is the corridor floor and the wasted fare, not a bed count.',
    recommend: 'Six things. Instrument twenty pharmacy counters on paracetamol and saline volume rather than instrumenting the timeline. Read day of illness at presentation as a communications metric, because it is already on the admission form and it moves from four to eight in this run. Send the nightly bed number to the counters and the stands. Answer the corridor fear, not the bed claim. Put a named ward person inside the building committee groups before the season starts. And keep measuring six weeks past the point where the dashboard looks calm.',
  },

  interviewAgents: [
    {
      name: 'Village household head',
      role: 'District household outside the city',
      segment: 'rural',
      responses: [
        'He heard that the Dhaka hospitals are full and concluded the district hospital was pointless too, which nobody in Dhaka said and nobody in the district can correct.',
        {
          when: ['dhaka', 'city', 'district', 'local', 'here', 'travel'],
          text: 'Nothing in the message was about this upazila. It did not need to be. If the big hospitals are gone, the small one is obviously worse, and that reasoning has never once been challenged out here.',
        },
        {
          when: ['fever', 'sick', 'treat', 'medicine', 'what did'],
          text: 'The fever in this house was treated by the pharmacy in the bazaar for six days. That is normal here in any season, so nobody noticed that this time it was a decision rather than a habit.',
        },
        {
          when: ['notice', 'official', 'health office', 'government', 'correct'],
          text: 'No notice from any health office has ever reached this house. What reaches this house is what a relative in Dhaka forwards, and that is one photograph and one joke.',
        },
        'The district lane moves later, quieter and for longer than the city one, and it is the last place anybody will look for this.',
      ],
    },
    {
      name: 'Rickshaw stand organiser',
      role: 'Carries the sick to hospital, or does not',
      segment: 'urban_working',
      responses: [
        'He repeats whatever the last passenger said, and the last passenger said they were turned away. That is the entire evidence base behind a hundred journeys not taken.',
        {
          when: ['know', 'sure', 'evidence', 'check', 'how many', 'sample'],
          text: 'He is not repeating a rumour as he sees it. He carried the man himself and brought him back. One trip, seen with his own eyes, is worth more to him than any number on a page, and he is not wrong to think so.',
        },
        {
          when: ['ask', 'household', 'night', 'decide', 'gate', 'advice'],
          text: 'People come to the stand at eleven at night and ask him whether it is worth going. He is the last person consulted before the decision, and nobody official has ever sent him a single word.',
        },
        {
          when: ['trip', 'fare', 'work', 'night', 'business', 'count'],
          text: 'Hospital trips at night dropped for two weeks and then came back all at once, worse. He noticed both, and there is nobody he would report either to.',
        },
        'Give him the bed number every evening and he will tell it to twenty households before midnight, for nothing, because they are already asking him.',
      ],
    },
    {
      name: 'Ward nurse',
      role: 'Night shift at Shapla General',
      segment: 'middle_class',
      responses: [
        'She had four empty beds on a night the whole city was certain there were none, and no way to tell anyone outside the building.',
        {
          when: ['tell', 'say', 'post', 'channel', 'why not', 'speak'],
          text: 'Staff do not post about occupancy. It would be read as the hospital advertising, and it would be a nurse contradicting a photograph, which is not a fight the photograph loses.',
        },
        {
          when: ['late', 'day eight', 'presentation', 'condition', 'arrive'],
          text: 'The ones who do come are arriving on day seven and day eight instead of day four. It is written in the file as late presentation, and that sentence makes a rumour disappear into a clinical category.',
        },
        {
          when: ['pharmacy', 'counter', 'saline', 'napa', 'before'],
          text: 'By the time they reach the ward they have four days of counter treatment behind them and a notebook of temperatures. The notebook is often the most useful document in the room.',
        },
        'The correct fact was inside this building every night of the scenario and it never got out once.',
      ],
    },
    {
      name: 'Hospital communications officer',
      role: 'Shapla General front of house',
      segment: 'corporate',
      responses: [
        'She posted that beds are available and watched engagement rise. Every person who saw it was already willing to come.',
        {
          when: ['data', 'metric', 'dashboard', 'admission', 'number', 'measure'],
          text: 'Admissions were flat and complaints were near zero, and both were read as a quiet week. Admissions were flat because people stopped arriving, and nobody complains about a hospital they did not go to.',
        },
        {
          when: ['reach', 'audience', 'who saw', 'engagement', 'post'],
          text: 'The post reached followers of the page. A household deciding at eleven at night is not a follower of the page and has no reason to become one in the next twenty minutes.',
        },
        {
          when: ['recommend', 'fix', 'instrument', 'better', 'next time'],
          text: 'Day of illness at presentation is already on the admission form. Plotted weekly it would have shown this at round twenty. It is the only quantitative proof of a rumour anybody in this building will ever get.',
        },
        'She will record the clarification as the resolution of the incident, and the next fever in that para will still be managed at a counter.',
      ],
    },
    {
      name: 'Household head with family abroad',
      role: 'Treatment paid for from overseas',
      segment: 'migration_workers',
      responses: [
        'The hospital money in this house comes from a brother in Malaysia, and asking for it means admitting the fever got serious. So the fever is given a few more days to not be serious.',
        {
          when: ['ask', 'call', 'money', 'send', 'abroad', 'brother'],
          text: 'He waited until day seven to make the call. Asking early would have looked like panic and asking at all costs somebody a week of overtime, so the delay is a courtesy that nearly cost more than it saved.',
        },
        {
          when: ['cost', 'fare', 'afford', 'private', 'bill'],
          text: 'If the beds really were gone, the trip is a wasted fare, a wasted night, and a private clinic bill afterwards. That whole chain is what the rumour actually threatened, not the bed.',
        },
        {
          when: ['hear', 'group', 'forward', 'photo', 'who told'],
          text: 'The photograph came to him twice from two different groups on the same evening, which is what made it feel confirmed. It was the same image both times.',
        },
        'The cost of this delay is paid abroad and the delay itself is recorded here as late presentation, so no part of it appears in the same place twice.',
      ],
    },
    {
      name: 'Health meme page admin',
      role: 'Runs a health meme page',
      segment: 'students',
      responses: [
        'He is not warning anyone. The bed shortage joke was the strongest post available that week, and it carried the claim to people the photograph never reached.',
        {
          when: ['true', 'accurate', 'check', 'verify', 'source', 'fact'],
          text: 'He did not check anything and would not have posted it if checking were the standard. A joke has to be recognisable, not true, and everybody recognised the fear of arriving somewhere with a sick child and being sent home.',
        },
        {
          when: ['harm', 'responsible', 'blame', 'consequence', 'damage'],
          text: 'He does not think of himself as part of a health event. He thinks of himself as somebody who posted a good line about Dhaka traffic and hospitals in the same sentence.',
        },
        {
          when: ['stop', 'correct', 'hospital', 'respond', 'reply', 'fix'],
          text: 'A hospital correcting him publicly becomes the next joke within an hour. A hospital sending him the nightly bed number as material becomes the fastest correction in the city, at no cost.',
        },
        'He stopped posting about it around round twenty. Nothing in the households that had already decided moved when he did.',
      ],
    },
    {
      name: 'Para pharmacy counter',
      role: 'Sells more paracetamol than in any week this year',
      segment: 'retailers',
      responses: [
        'He sold three times the usual paracetamol and answered platelet questions he is not qualified to answer, because he was the only person in the conversation who had ever seen a lab report.',
        {
          when: ['register', 'record', 'data', 'report', 'count', 'tell'],
          text: 'He keeps no register and nobody has ever asked him for one. He could tell you which households are on a fourth day and which ones have gone quiet, and there is no form anywhere for that.',
        },
        {
          when: ['advice', 'triage', 'doctor', 'refer', 'test', 'platelet'],
          text: 'He tells them to get a platelet test. That is the only clinical decision made about some of these patients for four days, and he makes it standing behind a counter in a lane.',
        },
        {
          when: ['beds', 'hospital', 'full', 'ask', 'say'],
          text: 'When somebody asks him whether the hospitals are full, he answers, because he answers every other question they bring him. He is repeating what he heard, to the exact people who could still act on the truth.',
        },
        'Twenty counters reporting saline and paracetamol volume twice a week would see this whole event coming, and every one of them would do it for a phone call.',
      ],
    },
    {
      name: 'Mother watching a fever chart',
      role: 'Two children, day five of a fever',
      segment: 'women',
      responses: [
        'She did not go, because a night on a corridor floor with two children at home was worse than a fifth day of paracetamol. The temperature is going into a notebook instead.',
        {
          when: ['notebook', 'chart', 'record', 'temperature', 'track'],
          text: 'Times and temperatures, four a day, written in a school exercise book. It is careful work by somebody who has no idea which of those numbers is the one to run on.',
        },
        {
          when: ['cost', 'fare', 'afford', 'money', 'taxi'],
          text: 'The fare both ways buys five days of saline. That is not the whole reason, but it is the part that gets said out loud in the room when the decision is made.',
        },
        {
          when: ['tell', 'complain', 'call', 'hospital', 'anyone'],
          text: 'There is nobody to tell. She did not go anywhere, so nothing happened to anyone, and a decision taken in a bedroom at eleven at night is not the kind of thing that gets reported.',
        },
        'When the fever finally wins she will go, on day eight, and the file will say late presentation as if that were a description of the family rather than of the week.',
      ],
    },
    {
      name: 'Building committee elder',
      role: 'Forwards what the building should know',
      segment: 'elderly',
      responses: [
        'He forwarded the photograph as care, not as news. In a building group a warning that turns out to be nothing costs you nothing, and a warning you kept to yourself costs you everything.',
        {
          when: ['source', 'who took', 'date', 'verify', 'check', 'proof'],
          text: 'He wrote in the message that he did not know who took it. Nobody minded. The caveat travelled with the image and stopped nothing, because a caution does not need to be proved the way a claim does.',
        },
        {
          when: ['correct', 'hospital', 'notice', 'denial', 'reach'],
          text: 'No hospital and no health office has ever been in that group. If a doctor from Shapla General were in it by name, the whole thing would have been settled in one message the same night.',
        },
        {
          when: ['before', 'remember', 'history', 'season', 'previous'],
          text: 'He has watched several dengue seasons from this building. The pattern he recognises is not the fever, it is the year everyone waited too long, and the memory of that is exactly what makes the photograph land.',
        },
        'He carries more weight in this run than any page in it, and no institution in the city has ever asked him what he is telling people.',
      ],
    },
  ],
}
