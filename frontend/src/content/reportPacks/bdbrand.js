// Report and interview content for the bdbrand scenario pack.
// Contamination rumour against Rongdhonu Noodles, Eid campaign week, Dhaka.
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

export const BDBRAND_REPORT = {
  reportSections: [
    {
      title: 'Phase by phase: what the cascade actually did',
      paragraphs: [
        'The run covers forty rounds. The product leaves a tiffin box at round two. The brand says its first word about it at round thirty-three. Thirty-one rounds separate the behaviour from the response, and that gap is what this report exists to describe.',
        '**Rounds 1 to 8. Private removal.** A screenshot carrying a batch number lands inside a school-mother group at round two, and Sharmin asks the question that actually decides this scenario, which is not whether the claim is true but whether it is worth the risk: bacchader tiffin e deya thik hobe. By round seven a group admin has forwarded it with the only instruction anyone will follow, apatoto bacchader na deowai bhalo. At round four the scheduled Eid campaign post publishes on its original calendar, forty minutes behind the screenshot, so the brand arrives in the room celebrating while the room is asking whether the food is safe. Nothing has been verified and nothing has been posted publicly. The packet is already out of the box.',
        '**Rounds 9 to 18. The joke phase.** At round eleven the meme page converts the batch number into a punchline, Eid er khushi ek plate e, lead o ek plate e, and the joke reaches more people in two hours than the campaign reached in two days. Humour is the format that survives fact-checking, because a joke makes no claim that can be denied. At round fifteen Kamrul reads the other half of the same event off the shelf: three cartons unsold, nobody asking, nobody explaining. The two lanes never touch each other and only one of them is visible to the brand.',
        '**Rounds 19 to 30. Offline settlement.** At round nineteen Nasrin buys a different brand at the bazaar and tells nobody, which is the modal behaviour of the entire run. At round twenty-four the teashop table passes on a school notice that nobody has seen, and it is believed anyway, because it arrived from a person rather than a page. At round twenty-eight the BSTI sample-testing notice is issued in procedural language with no verdict in it, and both sides read it as proof of their own position. This is the phase where the question stops being open. After round thirty the market has an answer, and it is not the answer the brand would have given.',
        '**Rounds 31 to 40. Official arrival.** At round thirty-three the English-language compliance statement publishes. It is accurate, it is well written, and it enters a segment that had barely stopped buying. It does not enter a single mother group and it does not reach a single shopkeeper. At round thirty-eight Kamrul gives the verdict that matters commercially: statement er por o order kori nai, ami wait kortesi. The clarification changed the conversation and did not change the reorder, and the reorder is the revenue.',
      ],
    },
    {
      title: 'Segment by segment: who moved, and in which direction',
      paragraphs: [
        '### School-mother groups',
        'The decision layer of the whole scenario and the fastest mover in it. The purchase stops before the opinion forms: the packet comes out of the tiffin box at round two and the question is asked afterwards, in that order, because a mother evaluating a food risk is not weighing evidence, she is weighing regret. This lane never argues with the brand and never appeals to it. It simply reallocates a fifty taka line item and moves on, and it takes the households of everyone else in the group with it inside a week.',
        '### Mudi dokan retailers',
        'The earliest hard indicator and the least consulted. Kamrul knows the exact size of the damage by round fifteen because he can count the cartons, and he knows it days before it registers as sentiment anywhere. What he does not have is a reason: customers switch without saying why, so he holds a precise measurement with no explanation attached and no route by which to send either of them upward. By round thirty-eight he is running his own risk policy, holding the reorder until customers come back, which converts a two-week scare into a quarter of lost shelf presence.',
        '### Campus and meme pages',
        'Lowest exposure, highest reach, and no grievance at all. Tanvir is not angry at Rongdhonu. He is running a humour page and the batch number is the funniest object available that week. That distinction is the single most useful thing in this report, because it means the amplifier is not an opponent and cannot be defeated, only out-supplied. This lane peaks at round eleven, decays by round thirty, and changes almost nobody who had not already taken the packet out.',
        '### Office tiffin groups and middle-class households',
        'The segment the clarification actually reaches, and the segment that needed it least. Teachers, nurses, bank clerks and tutors read the English compliance statement, find it credible, and quietly assume the matter is closed. Their own purchase barely moved. This is the lane that will report the crisis as over, in good faith, while the mother group next door has been on another brand for three weeks.',
        '### Garment floor and shared-kitchen households',
        'Bulk buyers, shared budgets, and the shortest path from doubt to substitution. Nasrin buys for a kitchen that feeds several people, so one decision at round nineteen moves a volume no single household could, and it moves without a word being spoken. Price sensitivity works against the brand here in an unusual direction: the substitute costs the same, so switching is free, and a free switch never has to be justified to anyone.',
        '### Para committee elders and older buyers',
        'Slow to change what they buy, quick to settle what the street believes. This lane reaches for precedent, remembers two previous food scares and how each of them ended, and will state a conclusion in a tone that closes the discussion. It is the only lane in the run that reliably reaches households with no group chat in them, and no part of the response goes anywhere near it.',
        '### The brand side: category, media and communications',
        'The most active and least effective segment in the run. The campaign calendar keeps publishing through rounds four to thirty because a scheduled post is part of a quarterly commitment and pausing it requires a decision nobody wants to own. Meanwhile the response is written for legal safety in the language of certificates, which is exactly the register that fails in a mother group. This lane measured reach, sentiment and share of voice throughout, and every one of those numbers was real, and not one of them was about the households that stopped buying.',
      ],
    },
    {
      title: 'THE SILENCE LANE: the households that changed the tiffin box and never said a word',
      paragraphs: [
        'This is the finding. Everything else in this report is context for it.',
        'The population that moved the most produced no text at all. In this run the households that stopped buying Rongdhonu did so between rounds two and nineteen, without a complaint, a comment, a tag, a review, or a call. They did not boycott, because a boycott is a public act. They substituted, which is a private one. By the time the meme lane was at its loudest, the commercial damage was already done and none of it was written down anywhere a listening tool could find it.',
        '**What the silence is made of.** Three things, and none of them is apathy. First, there is nothing to file: a suspicion about a food product is not a complaint, it has no counterparty and no remedy, and a mother who is only ninety percent sure will not accuse a company of poisoning children. Second, switching is free. The substitute sits on the same shelf at the same price, so the decision costs nothing and therefore requires no justification to anybody. Third, saying it out loud has a price the brand never pays: to announce that you stopped buying it is to announce that you were feeding it to your child until last Tuesday.',
        '**Where it is nevertheless visible.** The lane leaves four traces and not one of them is text. A carton that does not move, which the shopkeeper can date to the day. A reorder that quietly does not get placed, which is the trace that lasts longest and is held by a person nobody in the brand has ever spoken to. A substitution pattern at the bazaar counter, where the same customer buys the same basket with one packet different, week after week. And a change in what school-mother groups ask each other, which shifts from is this safe to what do you pack now, a question that has already conceded the answer.',
        '**Why it outlasts the visible conversation.** The joke dies around round thirty because jokes have a shelf life. The substitution does not, because it turns into a habit that the household never revisits. A child who has eaten the other brand for three weeks develops a preference for it. A shopkeeper who skipped one reorder cycle discovers that the shelf space is already sold to someone else. The public conversation clears in a fortnight and the shelf takes a quarter, and anybody reading the fortnight as recovery will declare this over at the exact moment the loss is being locked in.',
      ],
    },
    {
      title: 'Amplifier profiles: the four accounts that decided the reach',
      paragraphs: [
        '### Tanvir, the meme page admin',
        'The largest reach in the run and the smallest grievance. His motivation is performance, not anger, which means the framing he chose was the one that would travel and not the one he believed. He put the batch number in the comments because a specific number is funnier than a vague accusation, and specificity is what made the claim feel checkable to people who never checked it. He cannot be argued with and he cannot be sued into silence without producing a bigger story. He can be out-supplied: he will post something accurate at the same speed if the accurate thing is worth posting.',
        '### The community group admin',
        'Low reach per post, decisive effect. This is the person who converted a screenshot into an instruction at round seven, and the instruction is what households actually acted on. He forwarded it as caution rather than as accusation, which is the format an official denial cannot compete with, because caution costs the forwarder nothing if it turns out to be wrong. There are perhaps forty of these accounts in the run and they are the cheapest correction channel available. Nobody in the brand knows a single one of them by name.',
        '### Kamrul, the mudi dokan owner',
        'The highest-trust node in the scenario and the one with the least information. He is asked about the product across the counter all week by people who have shopped with him for years, and he answers with whatever he heard last, because nothing correct has ever been put in his hands. He is not amplifying deliberately. He is simply where the question gets asked, which makes him the single cheapest place in this run to put a true sentence, and the last place anyone thought to put one.',
        '### The Bangla health and news pages',
        'Highest raw volume, weakest effect on behaviour. This lane carried the rumour and the BSTI notice within the same hour and treated them as the same kind of object, which is how a procedural sampling notice became evidence for both sides. On a dashboard this lane looks like the centre of the crisis. In the run it changed almost nobody who had not already decided, and it is the lane the brand spent the most energy monitoring.',
      ],
    },
    {
      title: 'Trust map: who is believed, by whom, about what',
      paragraphs: [
        'Trust in this run is not one number. It is a map of who is believed about which kind of claim, and the four layers barely overlap.',
        '**About safety, another mother is believed absolutely.** No verification is sought and none is expected, because the claim being made is not this is contaminated, it is I would not risk it, and nobody argues with a parent being careful about a child. This is the layer that decided the outcome and it is completely closed to institutional voices.',
        '**About the shelf, the shopkeeper is believed and is never asked to explain.** Customers accept his substitution suggestion without discussion. If he says the other packet is moving better, that settles it, and he is trusted precisely because he has no visible reason to say so.',
        '**About compliance, the English statement is believed by the people who never stopped buying.** It reads as competent to a segment that reads English documents for a living and as nothing at all to everyone else, because it did not arrive in front of them. The statement recovered credibility it had not lost, from an audience that had not withdrawn it.',
        '**About the regulator, nobody reads a procedure as a verdict.** The BSTI notice at round twenty-eight says a sample will be tested and says nothing else, so the suspicious read it as confirmation that there was something to test and the loyal read it as confirmation that the brand is being cleared. A neutral document in a decided room is not neutral, it is ammunition for both sides.',
        'The practical reading: this is a distribution problem, not a message problem. The correct information existed inside the company from round one. By round forty it had reached everyone except the mother, the shopkeeper and the group admin, who between them made every decision in the run.',
      ],
    },
    {
      title: 'What your dashboard will show, and why it is wrong',
      paragraphs: [
        'Between rounds nine and thirty-three this scenario produces a clean, confident and entirely misleading set of numbers.',
        '- **Mention volume spikes and then falls.** The fall looks like recovery. It is a meme page losing interest on its own schedule, and it has no relationship whatsoever to whether a single household has put the product back in the tiffin box.',
        '- **Sentiment reads as mild.** Most of the visible content is jokes, and a joke scores closer to neutral than to negative. The lane doing the actual damage wrote nothing at all, so the sentiment score is calculated on the population that stayed.',
        '- **Reach on the clarification looks excellent.** It travelled well, and it travelled entirely inside the segment that had not moved. Impressions against an audience that never left is the most flattering and least useful metric in this whole run.',
        'One number to hold onto: the visible conversation is generated by a lane that accounts for roughly a fifth of the households that actually switched. Four fifths of the commercial damage in this scenario never produced a single character of text.',
      ],
    },
    {
      title: 'Recommendations',
      paragraphs: [
        '**1. Kill the scheduled campaign inside the hour, not inside the week.** The round four post did more damage than the round eleven meme, because it proved the brand was not paying attention. Give one named person standing authority to pause the calendar without a meeting, and treat that authority as cheaper than the media it wastes.',
        '**2. Answer in the group, in Bangla, in one line.** The claim lives in mother groups and it is settled there. A single short Bangla sentence that a group admin can forward without embarrassment will outperform any statement the brand publishes on its own page, because forwarding is the only distribution mechanism this lane has.',
        '**3. Put a true sentence into the hands of the shopkeeper, on paper.** Forty mudi dokans in the affected wards, one printed line each, delivered by the same distributor van that is already going there. This costs almost nothing, it reaches the person who is actually being asked, and it is the only intervention in this list that also collects information on the way back.',
        '**4. Instrument the reorder, not the timeline.** Reorder rate across a fixed panel of thirty retailers, read weekly, would have caught this at round fifteen with a precise magnitude. Every listening tool in the market caught it at round eleven with no magnitude at all, and the eleven was the joke rather than the loss.',
        '**5. Ask the regulator for a sentence, not a certificate.** A procedural notice will be read as guilt by half the room. A dated, plain-Bangla line saying what was tested and what was found is worth more than the certificate it is based on, and it is the only artefact in this scenario that a group admin will forward without being asked.',
        '**6. Measure the recovery at the shelf, twelve weeks out.** The conversation clears in a fortnight and the substitution takes a quarter to reverse, if it reverses. Set the review at week twelve on reorder volume, and do not let a clean sentiment chart at week three close the file.',
      ],
    },
  ],

  reportAgentAnswers: {
    first: 'The earliest signal is inside a closed school-mother group at round two: a forwarded screenshot with a batch number, and Sharmin asking whether it is still safe to pack it. Nothing is public, nothing is verified, and the packet is already out of the tiffin box before anyone posts a word.',
    spread: 'It spreads twice, on two different rails. A group admin forwards it at round seven as caution, which is the format a denial cannot compete with, and a meme page turns the batch number into a joke at round eleven, which reaches more people in two hours than the campaign did in two days. Humour travels further than accusation because a joke makes no claim you can deny.',
    trust: 'Trust splits four ways. About safety, another mother is believed absolutely and nobody checks. About the shelf, the shopkeeper is believed and never asked why. About compliance, the English statement is believed by the middle-class segment that had barely stopped buying. And the BSTI notice is procedural, so both sides read it as proof of their own position.',
    quiet: 'The quiet lane is the finding. The households that stopped buying between rounds two and nineteen filed nothing: no complaint, no comment, no review, no call. There is nothing to file, the substitute costs the same so switching is free, and saying it out loud means admitting you were feeding it to your child until last week. It shows up only as a carton that stops moving and a reorder that never gets placed.',
    retail: 'The mudi dokan is the earliest hard indicator in the run and the least consulted. Kamrul can count three unsold cartons at round fifteen and date the change to the day, but no customer explains the switch, so he holds a precise measurement with no reason attached and no route upward. By round thirty-eight he is holding the reorder himself, which turns a two-week scare into a quarter of lost shelf.',
    women: 'School-mother groups decided this scenario. The purchase stops before the opinion forms, because a mother evaluating a food risk is weighing regret rather than evidence, and ninety percent sure is enough. One group message moves twenty households in an afternoon and produces no measurable content while doing it.',
    young: 'The meme page carries the reach and holds no grievance. Tanvir is not angry at Rongdhonu, he is chasing a good post, and the batch number is the funniest thing available that week. That means this lane cannot be defeated, only out-supplied, and it will carry something accurate at exactly the same speed if the accurate thing is worth posting.',
    timeline: 'Four phases across forty rounds. Rounds one to eight are private removal, with the screenshot at two, the scheduled campaign post at four and the group admin forward at seven. Rounds nine to eighteen are the joke phase, the meme at eleven and the first unsold cartons at fifteen. Rounds nineteen to thirty are offline settlement, the silent bazaar switch at nineteen and the procedural BSTI notice at twenty-eight. Rounds thirty-one to forty are the official arrival, an English statement at thirty-three that changes the conversation and not the reorder.',
    compare: 'The comparison that matters is between the lane that posts and the lane that buys. Meme pages generated most of the visible content and almost none of the loss. Mother groups and shared kitchens generated almost none of the content and all of the loss. The two are not correlated, and in this run they are not even in the same direction.',
    worst: 'The biggest risk is reading the decay of the joke as recovery. Mentions fall around round thirty because the meme page moved on, not because a single household went back. Stand the response down there and you stand it down at the exact point the substitution is hardening into a habit and the shelf space is being reallocated.',
    recover: 'Recovery runs through the group admin and the shopkeeper, not through the brand page. One short Bangla line that a group admin will forward without embarrassment, and one printed line in forty mudi dokans delivered by the van that is already going there. Both routes are the ones the rumour used, and they are the only two that reach the people who already moved.',
    recommend: 'Six things. Pause the campaign calendar within the hour and give one person the authority to do it. Answer in Bangla, in the group, in one line. Put a true sentence into the hands of the shopkeeper on paper. Instrument reorder rate across thirty retailers instead of watching the timeline. Ask the regulator for a dated plain sentence rather than a certificate. And review at week twelve on shelf volume, because the conversation clears in a fortnight and the substitution takes a quarter.',
  },

  interviewAgents: [
    {
      name: 'School-group mother',
      role: 'Mother who packs the daily tiffin box',
      segment: 'women',
      responses: [
        'She took the packet out of the tiffin box the morning she saw the screenshot, and asked the group about it that evening. The purchase stopped days before the opinion formed.',
        {
          when: ['sure', 'true', 'verify', 'check', 'proof', 'evidence', 'real'],
          text: 'She is not sure it is true and never claimed to be. With a child and a food product, being ninety percent sure is the same as being certain, because the two outcomes are not the same size.',
        },
        {
          when: ['post', 'complain', 'comment', 'speak', 'boycott', 'why not'],
          text: 'She has not written anything anywhere and will not. Announcing that she stopped buying it means announcing that the child was eating it every day until last Tuesday, and no one volunteers that.',
        },
        {
          when: ['statement', 'clarification', 'brand', 'english', 'compliance', 'apolog'],
          text: 'She never saw the statement. It was in English and it was on the brand page, and she has not opened the brand page since the campaign post that came out forty minutes after the screenshot.',
        },
        'The other brand is in the box now and the child prefers it. Three weeks of that is harder to reverse than anything the rumour did.',
      ],
    },
    {
      name: 'Mudi dokan owner',
      role: 'Para grocery shopkeeper',
      segment: 'retailers',
      responses: [
        'He watched three cartons sit unsold in a week and read that as the verdict. Same customers, same days, one packet different in the basket.',
        {
          when: ['ask', 'customer', 'explain', 'why', 'reason', 'tell you'],
          text: 'Not one customer explained the switch. They just reached for the other packet, and if he asks, they smile and say nothing, so he has a number and no reason to attach to it.',
        },
        {
          when: ['report', 'upward', 'company', 'distributor', 'sales rep', 'brand', 'told'],
          text: 'The distributor rep came on the usual day and asked for the order, not for the news. Nobody has ever asked him what is happening at the counter, so it stops at the counter.',
        },
        {
          when: ['reorder', 'stock', 'shelf', 'order', 'buy again', 'restock'],
          text: 'He has not reordered since, and he will not until customers ask for it by name. Holding the order costs him nothing and putting the wrong stock on a small shelf costs him everything.',
        },
        'One printed line in Bangla, handed over the counter, would have given him something to say to twenty people a day. Nobody brought one.',
      ],
    },
    {
      name: 'Meme page admin',
      role: 'Campus humour page moderator',
      segment: 'students',
      responses: [
        'He is not angry at Rongdhonu. He is chasing reach, and a batch number is the funniest object available that week.',
        {
          when: ['true', 'check', 'verify', 'accurate', 'fact', 'source'],
          text: 'He did not check it and would not have posted it if he had. Checking is what turns a good post into a bad one, and the joke was never a claim in the first place.',
        },
        {
          when: ['harm', 'damage', 'responsib', 'guilt', 'fault', 'regret'],
          text: 'He does not think the post did anything, because in his lane nothing feels like it lands. The idea that a shopkeeper in Mirpur stopped ordering because of a punchline has never occurred to him.',
        },
        {
          when: ['stop', 'respond', 'legal', 'takedown', 'correct', 'brand', 'reach out'],
          text: 'A legal notice would be the best post of the month and he knows it. Something genuinely funny and true from the brand side would move him faster, at the same speed the joke moved.',
        },
        'By round thirty he has moved on to something else. Nothing in the retail lane moved with him.',
      ],
    },
    {
      name: 'School teacher',
      role: 'Middle-class household, office tiffin group',
      segment: 'middle_class',
      responses: [
        'He read the English statement, found it credible, and concluded the matter was closed. His own household barely paused.',
        {
          when: ['group', 'mother', 'neighbour', 'others', 'around you', 'community'],
          text: 'He has no idea the mother group in the next building moved to another brand three weeks ago. Those two conversations never touched, and only one of them has anything written in it.',
        },
        {
          when: ['statement', 'english', 'language', 'bangla', 'reach'],
          text: 'The statement was competent and it was in the language he reads at work. That is exactly why it convinced him and exactly why it convinced nobody who had stopped buying.',
        },
        {
          when: ['bsti', 'regulator', 'test', 'notice', 'official'],
          text: 'He read the testing notice as reassurance that the system works. At the teashop the same notice was read as proof that there was something worth testing.',
        },
        'This is the lane that will tell you the crisis is over, and it will be telling you the truth about itself.',
      ],
    },
    {
      name: 'Garment floor supervisor',
      role: 'Bulk buyer for a shared kitchen',
      segment: 'urban_working',
      responses: [
        'He buys for a kitchen that feeds several people, so one decision at the bazaar moved a volume no single household could. He did not discuss it with anyone.',
        {
          when: ['price', 'cost', 'cheap', 'expensive', 'afford', 'money'],
          text: 'The substitute costs the same. That is the whole reason the switch was easy: a free decision never has to be defended, so it never becomes a conversation.',
        },
        {
          when: ['post', 'complain', 'phone', 'online', 'facebook', 'speak'],
          text: 'He has an account and uses it for Eid photographs. Nothing about noodles is going on it, because none of that is worth typing.',
        },
        {
          when: ['back', 'return', 'again', 'recover', 'trust'],
          text: 'He would take it back if it was clearly settled and someone at the bazaar said so out loud. Nobody at the bazaar has said anything, so the new packet stays.',
        },
        'The shared kitchen reached its full response in one afternoon and produced nothing measurable while doing it.',
      ],
    },
    {
      name: 'Para committee elder',
      role: 'Older buyer who settles what the street believes',
      segment: 'elderly',
      responses: [
        'He does not spread the rumour, he settles it, and this run shows he can settle it in either direction depending on what he heard at the teashop that week.',
        {
          when: ['before', 'previous', 'history', 'remember', 'past'],
          text: 'He has seen two food scares before this one. Both ended without an announcement, which is why he assumes this one will too, and why his conclusion arrives long before any evidence does.',
        },
        {
          when: ['reach', 'group', 'phone', 'whatsapp', 'offline', 'who listens'],
          text: 'The households on his lane with no group chat in them hear it from him and from nowhere else. No page reaches them and no statement reaches them.',
        },
        {
          when: ['brand', 'company', 'contact', 'asked', 'response'],
          text: 'Nobody from the company has ever spoken to him, and he would have listened. He has been buying from the same shop for thirty years and holds an opinion twelve families repeat.',
        },
        'What he says at the teashop on the day the notice lands decides how the notice is read on that whole street.',
      ],
    },
    {
      name: 'Village shopkeeper',
      role: 'Rural retail lane, one week behind Dhaka',
      segment: 'rural',
      responses: [
        'The rumour reached him a week after Dhaka and arrived fully formed, with no screenshot attached and no way to check it.',
        {
          when: ['dhaka', 'city', 'urban', 'arrive', 'late', 'hear'],
          text: 'What reaches the village is the Dhaka conclusion rather than the Dhaka argument. By the time it gets here it is no longer a question, it is a fact that a relative in the city has already settled.',
        },
        {
          when: ['stock', 'supply', 'distributor', 'shelf', 'order'],
          text: 'The distributor stopped bringing it before anyone here stopped asking for it. So the shelf gap looks like a demand collapse and it is actually a supply decision made in a city office.',
        },
        {
          when: ['statement', 'correction', 'clarif', 'english', 'notice'],
          text: 'Nothing official has reached this shop in any language. If the company had wanted to correct it here, the van that comes every fortnight was the only vehicle available and it came empty.',
        },
        'This lane will be the last to come back and nobody is counting it, because it is small per shop and there are a great many shops.',
      ],
    },
    {
      name: 'Remittance household manager',
      role: 'Household with a family member working abroad',
      segment: 'migration_workers',
      responses: [
        'He heard about it from Muscat before he heard about it in Mirpur. The meme travelled out with the diaspora and came back as a phone call at midnight.',
        {
          when: ['abroad', 'gulf', 'call', 'family', 'overseas', 'outside'],
          text: 'The family member abroad saw the joke on a Bangladeshi page and rang home to ask what was being fed to the children. That call carried more weight than any group message did.',
        },
        {
          when: ['buy', 'stop', 'switch', 'brand', 'household'],
          text: 'The household switched that same week, and the instruction came from four thousand kilometres away. No dashboard in Dhaka has a field for that.',
        },
        {
          when: ['statement', 'trust', 'back', 'return', 'convince'],
          text: 'He would need to hear it settled twice, once locally and once from the page his family abroad follows, before the old packet goes back in the basket.',
        },
        'This lane is small in volume and long in memory, and it keeps the story alive after the local conversation has stopped.',
      ],
    },
    {
      name: 'Retail category manager',
      role: 'Brand side, category and communications',
      segment: 'corporate',
      responses: [
        'He is watching mention volume and sentiment, both of which are real numbers, and both of which describe the segment that changed least.',
        {
          when: ['data', 'metric', 'dashboard', 'measure', 'number', 'sentiment'],
          text: 'The dashboard showed a spike at round eleven and a decay by round thirty. The spike was a joke and the decay was the joke ending. Nothing in the tool corresponds to a carton that stopped moving.',
        },
        {
          when: ['campaign', 'schedule', 'post', 'pause', 'calendar'],
          text: 'The Eid post published forty minutes after the screenshot because pausing the calendar needed three approvals and nobody wanted to own the wasted spend. That post cost more than the meme did.',
        },
        {
          when: ['recommend', 'fix', 'better', 'instrument', 'next time'],
          text: 'Thirty retailers reporting reorder rate weekly would have given him the magnitude at round fifteen. Every tool he pays for gave him round eleven with no magnitude at all.',
        },
        'He will report containment around round thirty-six, and he will be describing the noise rather than the shelf.',
      ],
    },
  ],
}
