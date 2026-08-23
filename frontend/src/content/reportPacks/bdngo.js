// Report and interview content for the bdngo scenario pack.
// Re-registration rumour against the Mayer Hashi maternal allowance, run by
// the Alor Shetu Foundation in Kurigram.
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

export const BDNGO_REPORT = {
  reportSections: [
    {
      title: 'Phase by phase: what the cascade actually did',
      paragraphs: [
        'The run covers forty rounds. A mother stops collecting at round eight. The programme office finds out at round twenty-nine, and it finds out from a register rather than from a person. Twenty-one rounds of silence sit in the middle of this scenario, and they are the reason the report exists.',
        '**Rounds 1 to 8. The warning becomes a decision.** At round two Anowara forwards a voice note into a shomiti group: bhata naki bondho hoiya jaitese, notun kore NID diya nam tulte hobe. It is passed on as a kindness, because warning a neighbour costs nothing and staying silent might cost everything. At round five the union office says out loud that no notice has arrived, and gives nothing in writing, so nobody believes it. At round eight Morjina makes the decision the whole run turns on and tells no one: ei mash e ar gelam na, giya jodi shuni nam kata, tar cheye na jaowai bhalo. Six rounds from voice note to non-collection, with no complaint anywhere.',
        '**Rounds 9 to 19. The rumour is furnished.** At round twelve a Dhaka commentary page posts the cut as established fact with a stock photograph of a queue attached, and gets more reach in one evening than the programme has had all year. At round sixteen the photocopy shop begins running NID copies from morning to close, without knowing whether anyone needs them. This is the phase where the rumour stops being a claim and starts being an activity, and an activity is much harder to deny than a sentence.',
        '**Rounds 20 to 30. The gatekeeper settles it.** At round twenty Rafiqul begins signing verification slips that nobody asked him to invent, and the queue outside his room becomes the strongest evidence available that the rumour is true. A physical queue is a fact. At round twenty-five thirty mothers gather at the union office and demand a written notice: they are loud, they are photographed, they are counted, and every one of them is a mother who never stopped collecting. At round twenty-nine Sirajul opens the register and finds forty names missing, with no column in the form for why.',
        '**Rounds 31 to 40. The correction misses.** At round thirty-four a Bangla fact page explains that no circular exists. It is shared enthusiastically by people who were never frightened, and it does not reach a single phone with no data on it. At round thirty-nine the Alor Shetu help desk publishes a Bangla notice and a hotline number, which is the correct content on the wrong wire: the mothers who left have no number saved, no reason to call a programme they believe has already removed them, and no way at all to learn that they were never removed.',
      ],
    },
    {
      title: 'Segment by segment: who moved, and in which direction',
      paragraphs: [
        '### Mothers who collect the allowance',
        'The largest lane, the fastest to act, and the one that produces no record of any kind. The decision is made inside a single calculation that the programme has never modelled: the cost of being told at the counter, in front of the queue, that the name is gone is far higher than the cost of not going. So they do not go. They do not ring, do not complain and frequently do not tell each other, because saying it out loud invites the question of whether the name really was struck off. This lane reaches its full response by round twelve and the programme does not see it until round twenty-nine.',
        '### Shomiti groups and char households',
        'The distribution network for both the fear and the eventual fix. A shomiti group is twenty women who meet with a book, which means a claim entering it at nine in the morning has been acted on by twenty households before dark. Anowara did not spread a lie, she passed on a warning, and passing on a warning is a form of care in a place where nobody is ever told anything officially. The char households furthest from the road hear this last and come back slowest, because everything reaches them by boat, including reassurance.',
        '### Union gatekeepers',
        'Small in number, decisive in effect, and outside the reach of every programme communication in this run. Rafiqul did not intend fraud. He responded to demand: mothers arrived asking for verification, so he verified something, and the act of signing manufactured the rule it appeared to confirm. Nothing in the programme design gives him a script, a stake, or a reason to check, and nothing gives him a phone number to ring when a hundred people turn up at his door with NID photocopies.',
        '### Alor Shetu field officers',
        'The most trusted node in the run and the most thinly spread. A field officer standing in a yard settles a question in one visit that no notice can settle in twenty. Sirajul covers nine villages, which means the households within an hour of him come back within a cycle and the households two ghats further out do not come back at all. He also learns about the panic from an attendance number rather than from a beneficiary, which tells you exactly how the information flows: upward, late, and stripped of its reason.',
        '### Photocopy shops and NID counters',
        'The earliest measurable indicator in the whole scenario and nobody is reading it. Nurul had the busiest week of the year at round sixteen and can name the day it started. He does not know what the rule is, has never been told, and is not lying to anyone: he is simply making copies people ask for. A photocopy counter in a union bazaar is a live sensor for administrative panic, it costs nothing to ask, and no programme in the district asks.',
        '### Dhaka commentary pages and college students',
        'Maximum reach, zero exposure, and no accountability at any point. Sohag posted the cut as fact because the screenshot existed and the reach was good. He has never been to the district and will never see the queue he helped create. This lane is also where the eventual correction did best, which is the whole problem: the correction performed brilliantly in the one population that was never going to lose an allowance.',
        '### The programme office and the donor side',
        'Watching a complaint log that is almost empty and reading it as calm. The instruments are all real and all backwards: grievances are counted, and the affected do not file grievances; disbursement variance is tracked, and it lands on a different desk a month later; the protest at round twenty-five produces the only qualitative evidence in the system and it comes from the wrong thirty women. This lane will report the month as stable and will not be lying.',
      ],
    },
    {
      title: 'THE SILENCE LANE: the mothers who stopped walking to the union office and told no one',
      paragraphs: [
        'This is the finding. Everything else in this report is context for it.',
        'Non-collection is the loudest signal in this scenario and it is completely inaudible. Between rounds eight and twenty-five, several hundred mothers across the union simply did not turn up on disbursement day. They did not protest, did not call the help desk, did not query anything at a counter, and in most cases did not tell the other women in their own shomiti. The programme has no field anywhere that records a person who was not there for a reason. The register writes it down as attendance, which is the same shape as a name that never existed.',
        '**What the silence is made of.** Three things, and none of them is ignorance. First, the counter is a public place. Being told in front of thirty neighbours that the name has been struck off is a humiliation with a long memory attached to it, and staying home costs nothing by comparison. Second, asking is dangerous. In a discretionary system, the widely held belief is that the person who makes trouble is the person who gets removed, so a question about your own eligibility feels like an application to lose it. Third, the journey itself is real work: a half day, a boat, sometimes a fare, and no mother spends that on a trip she has been told will end in nothing.',
        '**Where it is nevertheless visible.** The lane leaves four traces, and not one of them is a complaint. A disbursement point that is forty women short, which the field officer can count but cannot explain. A photocopy shop running NID copies at four times its normal volume, dated to the day. A queue outside a union parishad member room that nobody in the programme requested or authorised. And a change in what shomiti groups talk about, which shifts from the allowance to who is still getting it, a question that has already conceded the premise.',
        '**Why it outlasts the visible conversation.** The protest at round twenty-five is resolved in a week, because the women who protest are present and can be answered. The silence resolves in nothing, because it is invisible to every process the programme has for resolving anything. A mother who has missed two cycles has stopped budgeting around the allowance, has borrowed to cover the gap, and now has an interest in not finding out that she could have collected. Absence compounds: the longer a mother is off the list in her own mind, the more true it becomes, and no notice published anywhere will ever be read by somebody who has stopped believing the programme is about them.',
      ],
    },
    {
      title: 'Amplifier profiles: the four accounts that decided the reach',
      paragraphs: [
        '### Anowara, the shomiti group leader',
        'The highest-conversion amplifier in the run and the one with the best intentions. She forwarded the voice note as a warning, in the register of care, to twenty women who trust her with a savings book. That format is unanswerable by an official denial, because the denial argues with the facts while the warning argues with the risk. She is also the single best available correction channel in the union: the same twenty households would act on a true sentence from her within one afternoon, and nobody has ever given her one.',
        '### Rafiqul, the union parishad member',
        'The node that converted a rumour into an institution. He began signing verification slips at round twenty because people asked him to, and a signed slip is a physical object that outranks any spoken reassurance in a place where nothing official is ever spoken. His motivation is standing rather than money: being the man who can fix your problem is worth more locally than the fee. Any response that treats him as the culprit will fail. A response that gives him the real rule, in writing, on a paper he can show people, turns the strongest amplifier in the run into the strongest correction in it.',
        '### The photocopy and NID shop',
        'An accidental amplifier and a perfect sensor. Nurul makes no claim and holds no opinion, but a shop full of people photocopying NID cards is the most persuasive evidence in the union that re-registration is real, and every person who walks past it is convinced by it. He is also the cheapest listening post available anywhere in this scenario: one question a week to one shop would have dated the panic to round sixteen.',
        '### The Dhaka commentary page',
        'Highest raw reach, no local consequence, no local presence. Sohag turned a district rumour into a national fact at round twelve with a stock photograph and no reporting at all. This lane is the reason the story is unanswerable by anyone in Kurigram: the claim now has a source that is bigger than the union office, and the union office cannot reach the source. It is also the lane the correction reached best, which tells you the correction was aimed at the audience with the loudest voice rather than the one with the most to lose.',
      ],
    },
    {
      title: 'Trust map: who is believed, by whom, about what',
      paragraphs: [
        'Trust in this run is not one number. It is a map of who is believed about which kind of claim, and the four layers are almost completely separate populations.',
        '**About what will happen at the counter, another mother is believed absolutely.** No verification is sought. The claim is not the allowance has been cut, it is you will be turned away, and a warning about humiliation from someone who shares your position does not need evidence.',
        '**About the rule, a signature outranks a sentence.** The union office said no circular exists and was not believed. Rafiqul signed a piece of paper and was believed instantly. In an environment where every entitlement has arrived as a form, paper is the only thing that carries authority, and the programme spent this entire run talking instead of printing.',
        '**About the programme, only a field officer standing in the yard is believed.** Proximity is the whole variable. Households within an hour of Sirajul return within one cycle. Households two ghats out do not return at all, and the difference between them is not information, it is whether a known face physically arrived.',
        '**About silence, absence is read as confirmation.** This is the layer that costs the most. When the programme says nothing for three weeks, that is not received as neutral, it is received as evidence: a programme that intended to keep paying you would have said so. Every quiet week between round eight and round thirty-nine made the rumour more credible without anybody adding a word to it.',
        'The practical reading: this is not a communications failure, it is a delivery failure. The true statement existed on day one, in the right language, and by round forty it had reached the fact pages, the donor and the Dhaka commentary lane, and had not reached one shomiti group, one gatekeeper, or one mother who stopped coming.',
      ],
    },
    {
      title: 'What your dashboard will show, and why it is wrong',
      paragraphs: [
        'Between rounds eight and thirty-nine the programme instruments produce a set of numbers that are individually accurate and collectively backwards.',
        '- **The grievance log stays almost empty.** It is read as calm. It is a direct measurement of the households who still feel safe enough to complain, which is the exact opposite of the population in trouble, and the emptier it gets the worse the situation is.',
        '- **The protest at round twenty-five looks like the crisis.** Thirty women at the union office are visible, quotable and countable, and every one of them is a mother who never stopped collecting. The only qualitative evidence the programme captured came from the least affected group in the scenario.',
        '- **Disbursement variance arrives late and lands on a different desk.** The one number that would have told the truth shows up a month after the fact, on a finance report, as a percentage with no reason attached, and by then the communications review has already closed.',
        'One number to hold onto: thirty mothers were counted at the union office and roughly four hundred were not counted anywhere. The programme built a response for the thirty because the thirty were the only ones it could see.',
      ],
    },
    {
      title: 'Recommendations',
      paragraphs: [
        '**1. Print the rule and hand it to the gatekeeper.** Rafiqul will be asked either way, and he will answer either way. One dated Bangla page with a signature on it, delivered to every union parishad member in the coverage area, converts the strongest amplifier in this run into the strongest correction. Paper is the only medium that carries authority here, and it is the cheapest one.',
        '**2. Measure non-collection as an alarm, not as attendance.** Add one derived field: names on the list who did not collect this cycle and collected last cycle. It requires no new data, it would have fired at round twelve, and it is the only signal in the entire scenario that points at the right households.',
        '**3. Send the field officer to the absent, not to the assembled.** The thirty at the office can be answered by anyone. The four hundred who stayed home can only be reached by a known face arriving in the yard. Rank the visit list by non-collection, not by complaint volume, and start with the households furthest from the road because they come back slowest.',
        '**4. Reply to the shomiti in the format it uses.** The rumour arrived as a forty-second voice note. The correction arrived as a written notice and a hotline number. Record a forty-second voice note in the same dialect, from a person the group knows, and give it to twenty group leaders to forward. It is the only artefact in this list that travels on its own.',
        '**5. Ask the photocopy shop.** One question a week to the NID counter in each union bazaar gives an early, dated and honest reading of administrative panic across the whole coverage area, for the price of the question. No programme in this district has ever asked, and the answer was sitting there from round sixteen.',
        '**6. Never let silence stand for three weeks.** Absence is read as confirmation in this population, so the cost of saying nothing while an internal check runs is higher than the cost of saying something incomplete. Publish the holding line on the day the rumour is detected, and set the review at the next two disbursement cycles rather than at the end of the news cycle.',
      ],
    },
  ],

  reportAgentAnswers: {
    first: 'The earliest signal is a forwarded voice note in a shomiti group at round two, saying the allowance is being cut and every name must be re-registered with NID. It is passed on as a kindness rather than as news, and by round eight a mother has already stopped collecting and told nobody.',
    spread: 'It spreads on two rails. A shomiti group is twenty women with a savings book, so a claim entering at nine in the morning has moved twenty households by dark. Then a union parishad member starts signing verification slips at round twenty, and a queue outside his room is a physical fact that no spoken denial can compete with.',
    trust: 'Trust splits four ways. About what happens at the counter, another mother is believed without evidence. About the rule, a signature outranks a sentence, which is why the office denial failed and the slips worked. About the programme, only a field officer standing in the yard is believed. And silence is read as confirmation, so every quiet week made the rumour truer.',
    quiet: 'The quiet lane is the finding. Several hundred mothers stopped turning up between rounds eight and twenty-five without filing anything, because being told at the counter in front of thirty neighbours that the name is gone is worse than not going, and in a discretionary system asking about your own eligibility feels like applying to lose it. The register records that as attendance, which looks identical to a name that was never there.',
    retail: 'The photocopy shop is the earliest measurable indicator in the run and nobody reads it. Nurul ran NID copies at four times normal volume from round sixteen and can date the start to the day. He does not know what the rule is and has never been told, and a shop full of people copying NID cards is itself the most persuasive evidence in the union that the rumour is real.',
    women: 'Mothers who collect the allowance are the entire scenario. They act on a calculation the programme has never modelled: the cost of public humiliation at the counter against the cost of a missed payment, and humiliation wins. The response is complete by round twelve, it produces no text, and it is invisible until a register is opened at round twenty-nine.',
    young: 'The Dhaka commentary page carries the reach and holds none of the risk. Sohag posted the cut as fact at round twelve with a stock photograph and no reporting, and has never been to the district. That lane is also where the round thirty-four correction performed best, which is the problem in one sentence: the fix reached the only population that could not lose an allowance.',
    timeline: 'Four phases across forty rounds. Rounds one to eight are the warning becoming a decision, the voice note at two, an unwritten denial at five, the first silent non-collection at eight. Rounds nine to nineteen furnish the rumour, with the Dhaka page at twelve and the photocopy queue at sixteen. Rounds twenty to thirty are the gatekeeper settling it, slips at twenty, the protest at twenty-five, forty missing names at twenty-nine. Rounds thirty-one to forty are a correction on the wrong wire.',
    compare: 'Compare the thirty who protested with the four hundred who did not. The thirty were present, countable, quotable and still collecting. The four hundred had already lost the payment and left no record at all. The programme designed its whole response around the group it could see, and that group was the least affected one in the run.',
    worst: 'The biggest risk is reading an empty grievance log as calm. It is a direct measurement of the households who still feel safe enough to complain, so the emptier it gets the worse things are. Close the file on that reading and the four hundred never come back, because nothing in the process is looking for them.',
    recover: 'Recovery runs through the gatekeeper and the field officer, not through the help desk. Print the real rule on one dated Bangla page and put it in the hands of every union parishad member, then rank field visits by non-collection rather than by complaint. A known face arriving in the yard settles in one visit what twenty notices cannot.',
    recommend: 'Six things. Print the rule and hand it to the gatekeeper. Turn non-collection into an alarm field rather than an attendance number. Send field officers to the absent, starting with the households furthest from the road. Reply to the shomiti in the format the rumour used, a forty-second voice note from a known voice. Ask the photocopy shop once a week. And never let silence stand for three weeks, because here silence is read as confirmation.',
  },

  interviewAgents: [
    {
      name: 'Beneficiary mother',
      role: 'Mother collecting the Mayer Hashi allowance',
      segment: 'women',
      responses: [
        'She stopped walking to the union office the month the rumour started. She did not complain and did not call, because being turned away at the counter is worse than not going.',
        {
          when: ['ask', 'question', 'office', 'counter', 'check', 'find out', 'call'],
          text: 'Asking feels like applying to be removed. In a place where a name can be struck off by a decision nobody explains, the woman who makes trouble is the one who loses the payment, so nobody makes trouble.',
        },
        {
          when: ['tell', 'group', 'shomiti', 'neighbour', 'other women', 'friend'],
          text: 'She did not tell the group either. Saying it out loud invites everyone to ask whether his name really was cut, and that is a question with no good answer available.',
        },
        {
          when: ['money', 'manage', 'gap', 'borrow', 'budget', 'cope'],
          text: 'Two missed cycles were covered by borrowing from a neighbour against the next harvest. That debt is now the reason not to hope, because hoping and being wrong costs more than simply managing without it.',
        },
        'If a field officer had walked into the yard and said the name is still on the list, she would have gone the next morning. Nobody came, so she did not go.',
      ],
    },
    {
      name: 'Shomiti group member',
      role: 'Char household in a twenty-woman savings group',
      segment: 'rural',
      responses: [
        'He forwarded the voice note because it sounded like a warning, and passing on a warning is a kindness. Twenty households took the decision from him that afternoon.',
        {
          when: ['regret', 'wrong', 'fault', 'blame', 'sorry', 'responsib'],
          text: 'He does not think he did anything wrong and he is right. Nobody in the union had told him anything true for six months, so the only information available was the information that arrived.',
        },
        {
          when: ['correct', 'fix', 'true', 'notice', 'clarif', 'undo'],
          text: 'If someone he knows records forty seconds saying the payment is safe, that will go to the same twenty women in the same hour. A printed notice pinned to the office wall will not, because none of them walk past the office wall.',
        },
        {
          when: ['char', 'far', 'boat', 'road', 'distance', 'reach'],
          text: 'Two ghats further out the news arrives late and the correction never arrives at all. Everything crosses that water by boat, including reassurance, and reassurance is the thing nobody bothers to put in a boat.',
        },
        'The group still meets every week with the book. Whatever is said in that room on a Tuesday is settled across twenty households by Wednesday, in either direction.',
      ],
    },
    {
      name: 'Field officer',
      role: 'Alor Shetu officer covering nine villages',
      segment: 'middle_class',
      responses: [
        'He found out from the attendance register, not from a mother. Forty names simply were not there, and the register has no column for why.',
        {
          when: ['why', 'reason', 'explain', 'record', 'field', 'form'],
          text: 'There is nowhere in the form to write that somebody was frightened. The system records present or absent, and absent from fear looks exactly like absent from moving away.',
        },
        {
          when: ['visit', 'yard', 'house', 'reach', 'travel', 'nine villages'],
          text: 'Nine villages is more than one person can hold. The households within an hour of him came back inside a cycle and the ones two ghats out did not come back at all, and the only difference between them was whether he physically arrived.',
        },
        {
          when: ['office', 'report', 'upward', 'manager', 'told', 'headquarters'],
          text: 'He reported it, and it went up as a variance number. By the time it reached a desk that could act, it had lost the sentence that mattered, which is that the mothers think they were removed.',
        },
        'One visit settles what twenty notices cannot. That is not a communications insight, it is just what the run shows: presence works and paper alone does not.',
      ],
    },
    {
      name: 'Programme manager',
      role: 'Alor Shetu programme office',
      segment: 'corporate',
      responses: [
        'He is watching the complaint log, which is almost empty, and reading that as calm. The disbursement variance sits on a different desk and arrives a month later.',
        {
          when: ['data', 'metric', 'measure', 'dashboard', 'number', 'log'],
          text: 'An empty grievance log measures the households who still feel safe enough to complain. He now understands that the emptier it gets, the worse the month has been, and there is no version of the report that says so.',
        },
        {
          when: ['protest', 'thirty', 'union office', 'demonstration', 'crowd'],
          text: 'The thirty women at the union office generated every quote in the incident file, and all thirty had collected on time. The response was designed around the only group visible enough to design around.',
        },
        {
          when: ['fix', 'recommend', 'change', 'instrument', 'better', 'next'],
          text: 'One derived field would have caught this at round twelve: names that collected last cycle and did not collect this one. It needs no new data collection at all, which is why it is embarrassing that it does not exist.',
        },
        'He will report the month as stable and he will not be lying. He will simply be describing the part of the population that stayed in view.',
      ],
    },
    {
      name: 'Dhaka commentary page admin',
      role: 'Student running a national commentary page',
      segment: 'students',
      responses: [
        'He posted the cut as fact because the screenshot was there and the reach was good. He has never been to the district and will never see the queue he helped create.',
        {
          when: ['check', 'verify', 'source', 'true', 'confirm', 'evidence'],
          text: 'The stock photograph of a queue was not from Kurigram and he knew that. It was the right picture for the story, and nobody in his comments has ever asked where a photograph came from.',
        },
        {
          when: ['correction', 'fact page', 'retract', 'delete', 'apolog'],
          text: 'The correction post did well on his lane, which is the joke of the whole thing: everyone who read it was already safe. He did not delete the original because a deleted post looks worse than a wrong one.',
        },
        {
          when: ['ngo', 'programme', 'alor shetu', 'contact', 'reach out', 'respond'],
          text: 'Nobody from the programme contacted him for eleven rounds. If they had sent one line with a real name attached, he would have posted it, because a scoop from the source outperforms a rumour every time.',
        },
        'He was the biggest voice in a district he cannot find on a map, and there is nothing in his lane that will ever tell him what it cost.',
      ],
    },
    {
      name: 'Photocopy shop owner',
      role: 'NID copy counter in the union bazaar',
      segment: 'retailers',
      responses: [
        'He ran NID copies all week without knowing whether anyone needed them. The shop has never been busier and he still cannot say what the rule is.',
        {
          when: ['when', 'start', 'date', 'day', 'week', 'first'],
          text: 'It started on a Sunday and by Tuesday there was a line outside. He can name the day it began, which is more than anyone at the programme office can do.',
        },
        {
          when: ['rule', 'know', 'true', 'explain', 'told', 'ask'],
          text: 'Customers ask him whether re-registration is real, and he says he does not know, and they take that as a yes because the shop is full. Nobody has ever handed him a piece of paper with the actual rule on it.',
        },
        {
          when: ['queue', 'proof', 'evidence', 'convince', 'crowd'],
          text: 'The line outside his door convinced more people than any post did. Somebody walking past does not read a claim, he reads a crowd, and a crowd photocopying NID cards means the rule must have changed.',
        },
        'One question a week would have told the programme exactly when this started and how big it was. In eleven years nobody has ever asked him anything.',
      ],
    },
    {
      name: 'Char household elder',
      role: 'Older resident who has seen three programmes come and go',
      segment: 'elderly',
      responses: [
        'He has seen three programmes come and go and assumes every one of them ends without an announcement. Nothing in this month has argued with that.',
        {
          when: ['before', 'previous', 'history', 'remember', 'past', 'other programme'],
          text: 'The last one stopped in the middle of a season and nobody was ever told. People found out by standing in a queue that did not move, so this rumour did not need to be proved to him, it only needed to be mentioned.',
        },
        {
          when: ['believe', 'trust', 'notice', 'official', 'hotline'],
          text: 'A hotline number means nothing in this yard. Trust here is a face that comes back a second time, and the programme has never sent the same face twice.',
        },
        {
          when: ['advice', 'young', 'daughter', 'household', 'family', 'said'],
          text: 'He told the young women in the household not to walk to the office and waste the day. That advice moved four households and cost him nothing to give.',
        },
        'Silence from an office is never neutral out here. It is the sound of a decision that has already been taken somewhere else.',
      ],
    },
    {
      name: 'Brick field worker',
      role: 'Wage worker in a household that collects the allowance',
      segment: 'urban_working',
      responses: [
        'He heard it at the brick field before it reached the yard at home, and passed it on that evening as a warning rather than as news.',
        {
          when: ['work', 'wage', 'field', 'shift', 'money', 'income'],
          text: 'The allowance is a small share of what comes in and a large share of what is certain. Losing something certain changes the household planning more than losing something bigger and irregular would.',
        },
        {
          when: ['office', 'go', 'visit', 'time', 'day off', 'leave'],
          text: 'Going to the union office means losing a working day and the fare. He will not spend that on a trip everyone says will end in nothing.',
        },
        {
          when: ['nid', 'photocopy', 'document', 'papers', 'card'],
          text: 'The household got the NID copies done anyway, because copies cost twenty taka and being wrong costs a month. That is why the shop was full and why the queue proved nothing about the rule.',
        },
        'Nobody in this household has complained to anybody. They simply reorganised around the gap and stopped expecting the payment.',
      ],
    },
    {
      name: 'Seasonal migrant to Dhaka',
      role: 'Household member sending money home',
      segment: 'migration_workers',
      responses: [
        'He is the shock absorber. When the allowance stopped arriving, the gap closed by him staying one extra month in Dhaka and sending it home.',
        {
          when: ['send', 'money', 'transfer', 'home', 'remit', 'extra'],
          text: 'Nobody at home asked him for more. They described the situation as manageable twice, and the extra money went anyway, because that is what the arrangement is.',
        },
        {
          when: ['hear', 'know', 'told', 'phone', 'find out', 'when'],
          text: 'He found out three weeks late, on a phone call about something else. By then the household had already stopped planning around the payment.',
        },
        {
          when: ['return', 'back', 'collect', 'again', 'restart'],
          text: 'Even if the payment restarts, nobody in the household will walk to the office on the strength of a notice. It will take somebody arriving and saying it in the yard.',
        },
        'The real cost of this rumour left the district. It shows up as an extra month of work in Dhaka and it appears in no programme record anywhere.',
      ],
    },
  ],
}
