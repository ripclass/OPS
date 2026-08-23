// Report and interview content for the bangladesh scenario pack.
// Rice price shock in Dhaka, the week before Eid.
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

export const BANGLADESH_REPORT = {
  reportSections: [
    {
      title: 'Phase by phase: what the cascade actually did',
      paragraphs: [
        'The run covers forty rounds. The shock is visible in household behaviour from round four and does not reach a public argument until round nine, and that gap is what this report exists to describe.',
        '**Rounds 1 to 8. Private adjustment.** Nothing is posted. Portions shrink, the second fish of the week is dropped, and the Eid clothes budget is quietly moved into the food budget. In this phase the only observable trace of a forty percent rise is a change in what people buy, and nobody is measuring that.',
        '**Rounds 9 to 18. The relay phase.** The bazaar is the first place the change becomes shared knowledge, because the price board is a public object and everyone standing in front of it is doing the same arithmetic. Grocers photograph the board. The photograph moves faster than the Commerce Ministry notice explaining it, and it arrives without the notice attached.',
        '**Rounds 19 to 30. The framing hardens.** Campus pages convert the price into a story about who gets consulted and who does not. This is the moment the issue stops being about rice. Once the framing is institutional neglect rather than market movement, a correct explanation about supply and import duty answers a question nobody is asking any more.',
        '**Rounds 31 to 40. Official arrival.** Relief language and clarification land into an information environment that has already settled the matter. The clarification is accurate. It is also the fourth version of events most people have seen, and the first three came from someone they know.',
      ],
    },
    {
      title: 'Segment by segment: who moved, and in which direction',
      paragraphs: [
        '### Low-income urban households',
        'The largest lane and the quietest. Response is immediate, entirely behavioural, and entirely undocumented: smaller portions, cheaper rice, one fewer protein day. Almost no public posting. This segment reaches its full response before the first campus post exists.',
        '### Women managing household food',
        'The decision-making layer inside that lane. The cut is made here, and it is made before the household discusses it. The characteristic pattern in this run is a woman changing the shopping list and telling nobody, including the rest of the household, until the change becomes impossible to hide.',
        '### Students and campus pages',
        'Low direct exposure, highest reach. Students are not the worst affected and in this run are frequently not affected at all, but they own the framing and they set it fast. Their contribution is not information, it is language: they give the rest of the population a way to describe the shock as a decision rather than a price.',
        '### Neighbourhood grocers and market traders',
        'The earliest reliable indicator in the whole run. They see the change as basket size before anyone sees it as sentiment. Customers switch to cheaper rice without comment, so the grocer has a precise reading of the damage and no route by which to report it.',
        '### Remittance-linked households',
        'The only lane where the strain is transmitted abroad. The household absorbs first and asks second, and the ask is delayed by about a week because raising it early reads as failing to manage. The Eid transfer is the pressure valve, which means the true cost of this shock lands outside the country and outside every dashboard measuring it.',
        '### Garment workers in shared accommodation',
        'Mess and dormitory budgeting makes this lane semi-public early: the arithmetic is done out loud because the cost is shared. It is still not posted. The conversation happens in a room with no institution in it.',
        '### Elderly residents',
        'Slowest to change behaviour, fastest to interpret. This lane reaches for precedent immediately and reads the current rise against remembered ones, which makes it both calming and corrosive. The reassurance is real, and so is the assumption that the explanation will not arrive.',
        '### Salaried middle class',
        'Absorbs the rise without a visible change, and therefore consistently underestimates it when asked. This is the lane that reads the ministry notice, finds it reasonable, and reports the situation as stabilising. It is genuinely stabilising for them. The danger is that this is also the lane most likely to be in the room when the response is designed.',
        '### Rural growing households',
        'On the other side of the price and still worse off, because the rise reached them as an input cost weeks before it reached anyone as income. Most of them sold at the old rate. The assumption that the grower gained is the most common analytical error made about a staple price shock, and it is made in this run within the first ten rounds.',
      ],
    },
    {
      title: 'THE SILENCE LANE: the households that cut the meal and never posted',
      paragraphs: [
        'This is the finding. Everything else in this report is context for it.',
        'The population that changed its behaviour most is the population that produced the least text. In this run the households at the sharpest end of a forty percent rise reduced consumption within the first eight rounds and generated almost no public content at all: no complaint, no comment, no tagged post. Not because they were unaffected, and not because they were satisfied, but because complaining publicly about not affording food is a statement about yourself, and people do not make it.',
        '**What the silence is made of.** Three things, in order. Shame, which keeps the cut private inside the household. Futility, learned from previous price rises where speaking changed nothing. And time, because the people worst hit are also the ones with the least of it, and a complaint is unpaid work.',
        '**Where it is nevertheless visible.** The lane leaves four traces, none of them in a listening tool. A shift in what grocers sell. A drop in basket size that shopkeepers can describe precisely. A rise in the number of households buying rice daily rather than weekly, which is a cash-flow signal and not a price signal. And a request for an early or larger remittance transfer, which arrives abroad before it arrives anywhere in the country.',
        '**Why it matters after the meeting.** The visible conversation peaks around round thirty and decays. The silent adjustment does not decay: a household that moved to cheaper rice in week one is still on cheaper rice in week six, long after the public argument has moved on. Anyone reading the decay of the public conversation as recovery will stand the response down at exactly the wrong moment.',
      ],
    },
    {
      title: 'Amplifier profiles: the five nodes that decided the reach',
      paragraphs: [
        '### The campus page admin',
        'Sets the frame, owns the reach, carries the least exposure. Motivation is reach itself rather than grievance, which matters, because it means the framing chosen is the one that performs and not the one that is most accurate. Any response that treats this actor as an opponent will lose. Any response that gives him something better to post will not.',
        '### The neighbourhood grocer',
        'The highest-trust node in the run and the least addressed. He is asked about the price twenty times a day by people who have known him for years, and he answers with whatever explanation he currently holds. He is not amplifying anything deliberately. He is simply the person the question gets asked to, which makes him the single cheapest place to put a correct answer.',
        '### The imam and the neighbourhood mosque network',
        'Low volume, very high weight. This node does not spread the claim, it settles it, and it can settle it in either direction. It is also the only amplifier in the run that reliably reaches older men and the households furthest from a phone.',
        '### The Bangla news page',
        'Highest raw volume, weakest effect on behaviour. It amplifies both the queue photograph and the relief rumour in the same hour, which is why this lane can look like the centre of the crisis on a dashboard while changing almost nobody who had not already decided.',
        '### The garment mess room',
        'The amplifier nobody counts, because it produces no text at all. Eight people sharing a food budget do the arithmetic out loud every evening, and the version of the situation that leaves that room with each of them the next morning is more accurate and more detailed than anything on a timeline. It reaches perhaps forty people per room, it reaches them completely, and there is no instrument in this run that can see it happen.',
      ],
    },
    {
      title: 'Trust map: who is believed, by whom, about what',
      paragraphs: [
        'Trust in this run is not one number. It is a map of who is believed about which kind of claim, and the map has three clear layers.',
        '**About price, the grocer is believed absolutely.** He is standing next to the thing being discussed and he has no visible incentive. Nobody checks him.',
        '**About cause, the campus page is believed by everyone under thirty and by nobody over fifty.** The framing wins its audience completely and does not travel outside it. This split is the reason a single national message fails here: the two halves of the population are not disagreeing about the facts, they are running on different explanations of them.',
        '**About remedy, nobody is believed yet.** Relief promises enter a population that has heard relief promises before, and the default assumption is that the promise will be partially kept and late. In this run the institutional voice recovers no credibility from making the announcement, and would recover some from naming a date and hitting it.',
        'The practical reading: the institution has a distribution problem, not a message problem. The correct explanation exists and is publicly available by round thirty-four. It never reaches the grocer, who is the person actually being asked.',
      ],
    },
    {
      title: 'What your dashboard will show, and why it is wrong',
      paragraphs: [
        'Between rounds nine and thirty this scenario produces a clean, legible, entirely misleading set of metrics.',
        '- **Mentions spike and then decay.** The decay looks like resolution. It is the campus lane losing interest, which happens on its own schedule and has no relationship to whether any household has resumed buying normally.',
        '- **Sentiment reads as anger.** The angry population is the one that still has room to be angry. The population under the most pressure is not represented in the sentiment score at all, because it did not write anything to score.',
        '- **The most-affected districts look the calmest.** Lower posting rates read as lower impact. In this run the correlation runs the other way: the quieter the lane, the more it changed.',
        'There is a further trap in the geography. Posting rates track phone data and disposable time, not exposure, so a heat map of this conversation is very close to a heat map of who can afford to talk. Read as an impact map it points the response at the wrong wards, and it does so with the confidence of something that looks like real data.',
        'One number to hold onto: the visible conversation covers the segments that produced about a fifth of the actual behavioural change. Four fifths of the response in this run is invisible to text-based listening.',
      ],
    },
    {
      title: 'Recommendations',
      paragraphs: [
        '**1. Instrument the trade lane, not the timeline.** Twenty grocers reporting basket size weekly will tell you more about this shock, earlier and more accurately, than any volume of comment analysis. This is the cheapest instrument available and it is the one nobody builds.',
        '**2. Answer where the question is being asked.** The person being asked about the price is the grocer. Put the correct, short, Bangla answer in his hands, on paper, before you publish anything nationally. If the shopkeeper can answer, the rumour has nowhere to grow.',
        '**3. Speak to the two explanations separately.** A message pitched at the under-thirty framing and a message pitched at the over-fifty framing are different messages. Sending one is choosing which half to lose.',
        '**4. Name a date and hit it.** In this run the credibility damage comes from the shape of the promise rather than its size. A smaller, dated commitment that is met outperforms a larger one that arrives late.',
        '**5. Keep measuring past the decay.** The visible conversation ends around round thirty-five. The household adjustment does not. Set the review point four weeks after the noise stops, not when it stops.',
        '**6. Do not treat the campus lane as the problem.** It is the distribution network. It carried the grievance because nothing else was available to carry, and given something accurate and shareable it will carry that instead, at the same speed.',
      ],
    },
  ],

  reportAgentAnswers: {
    first: 'The earliest signal is not a post. It is a household reducing the rice portion and dropping a protein day, inside the first eight rounds, before any public content about the price exists at all. The first thing this scenario produces is a change in a shopping basket.',
    spread: 'It spreads through the bazaar price board, which is a public object everyone reads at the same time, and then through campus pages that convert the price into a story about who gets consulted. The photograph of the board travels faster than the notice explaining it, and it travels without the notice attached.',
    trust: 'Trust splits three ways. About price the grocer is believed absolutely, because he is standing next to the thing being discussed. About cause the campus framing wins everyone under thirty and reaches nobody over fifty. About remedy nobody is believed yet, because relief promises land in a population that has heard relief promises before.',
    quiet: 'The quiet lane is the finding. The households at the sharpest end of the rise cut consumption within eight rounds and produced almost no text, because complaining publicly about not affording food is a statement about yourself and people do not make it. It is visible only as basket size, as a shift to daily rather than weekly rice buying, and as an early remittance request that leaves the country before it appears in any local metric.',
    retail: 'The grocers are the earliest reliable indicator in the run and the most ignored. They read the damage as basket size days before it reads as sentiment, customers switch to cheaper rice without explaining, and there is no route by which what the grocer knows reaches anyone who could act on it.',
    women: 'Women managing household food are the decision layer of the silent lane. The cut is made there, before the household discusses it, and frequently the rest of the family learns about it by noticing rather than by being told. This is also the lane with the least time available to complain, because a complaint is unpaid work.',
    young: 'Students carry the reach and the least exposure. They set the framing inside ten rounds and they set it for performance rather than accuracy, which is why the issue becomes about consultation rather than about supply. Treating them as the opposition loses. Giving them something better to post does not.',
    timeline: 'Four phases across forty rounds. Rounds one to eight are private adjustment with no public trace. Rounds nine to eighteen are the relay phase, where the bazaar price board makes the change shared knowledge. Rounds nineteen to thirty are where campus framing hardens the story into institutional neglect. Rounds thirty-one to forty are the official arrival, which is accurate and fourth in line.',
    compare: 'The comparison that matters is between the lane that speaks and the lane that acts. Students posted most and changed least. Low-income households posted almost nothing and changed everything. Measuring the first tells you close to nothing about the second, and in this run the two are not even correlated in the same direction.',
    worst: 'The biggest risk is reading the decay of the conversation as recovery. Mentions fall around round thirty-five because the campus lane loses interest, not because any household resumed buying normally. Stand the response down there and you stand it down at the exact point the silent adjustment is hardening into a habit.',
    recover: 'Recovery runs through the grocer and the imam, not through a national statement. Both are asked directly, both answer with whatever explanation they currently hold, and neither has been given a correct one. Fix that and the correction travels the same route the rumour did, which is the only route that reaches the households that already moved.',
    recommend: 'Five things. Instrument twenty grocers on basket size rather than instrumenting the timeline. Put a short correct Bangla answer in the shopkeeper hands before publishing nationally. Write two messages, because the under-thirty and over-fifty framings are different problems. Name a date on relief and hit it, because the credibility damage is in the shape of the promise. And set the review four weeks after the noise stops rather than when it stops.',
  },

  interviewAgents: [
    {
      name: 'Household food manager',
      role: 'Woman managing the household food budget',
      segment: 'women',
      responses: [
        'She made the cut before she told anyone. The rice portion came down first, then the second fish of the week went, and the family noticed by tasting it rather than by being told.',
        {
          when: ['post', 'complain', 'why not', 'social', 'facebook', 'speak'],
          text: 'She has not posted anything and will not. Saying in public that the food is short is a statement about the household rather than about the price, and it stays inside the four walls.',
        },
        {
          when: ['eid', 'festival', 'plan'],
          text: 'The Eid clothes money went into the food money in the first week. Nobody was consulted about that either. It is the kind of decision that gets made and then simply becomes true.',
        },
        {
          when: ['help', 'relief', 'government', 'support'],
          text: 'She has heard relief announced before. The assumption is that it will be partly real and late, so it does not enter the planning at all.',
        },
        'By the sixth week the household is still on the cheaper rice. The argument outside ended a month ago and nothing in the kitchen went back.',
      ],
    },
    {
      name: 'Campus page admin',
      role: 'Student running a campus grievance page',
      segment: 'students',
      responses: [
        'He turned the price into a story about who gets consulted, because that is the version that travels. The number on its own is not a post.',
        {
          when: ['affect', 'personal', 'your own', 'own household'],
          text: 'His own household is fine. That is the uncomfortable part: the loudest lane in this run is not the most exposed one, it is the one with time and reach.',
        },
        {
          when: ['accurate', 'true', 'fact', 'check', 'verify'],
          text: 'He did not check the import duty figure before posting it, and he would not have posted it if he had. Accuracy is not what decided the framing, performance was.',
        },
        {
          when: ['stop', 'respond', 'response', 'brand', 'government', 'correct'],
          text: 'A correction from an institution will not move him. Something accurate and worth posting will, at the same speed the grievance moved, because the incentive is reach and reach is indifferent to direction.',
        },
        'By round thirty-five he has moved on. Nothing in the household lane moved with him.',
      ],
    },
    {
      name: 'Neighbourhood grocer',
      role: 'Mudi dokan owner',
      segment: 'retailers',
      responses: [
        'He watched the basket shrink before anyone said the word crisis. Same customers, same days, smaller bags, and a steady drift from the good rice to the cheap rice.',
        {
          when: ['ask', 'question', 'explain', 'why', 'customer'],
          text: 'He gets asked about the price twenty times a day by people who have known him for fifteen years, and he answers with whatever he heard last. Nobody has ever given him the correct answer to give.',
        },
        {
          when: ['report', 'tell', 'upward', 'data', 'know'],
          text: 'He knows the size of the damage precisely and there is no one to tell. No supplier asks, no association asks, no government office asks. It stops at the counter.',
        },
        {
          when: ['daily', 'weekly', 'cash', 'credit', 'bakite'],
          text: 'The clearest sign is not the switch to cheap rice. It is households that used to buy for the week buying for the day. That is a cash problem rather than a price problem, and it shows up here first.',
        },
        'Trust is the one asset he has in this. People believe him about the price because he is standing next to it and has nothing to gain, which is exactly why putting a correct line in his hands would have been the cheapest thing anyone could have done.',
      ],
    },
    {
      name: 'Garment worker',
      role: 'Garment worker in shared accommodation',
      segment: 'urban_working',
      responses: [
        'The mess budget is shared, so the arithmetic gets done out loud. It still never leaves the room. Eight people can agree the price is impossible and not one of them writes it down anywhere.',
        {
          when: ['home', 'village', 'family', 'send', 'remit'],
          text: 'He delayed the money home by a week and did not explain why. Explaining would have meant admitting the calculation, and the calculation is the private part.',
        },
        {
          when: ['work', 'wage', 'overtime', 'factory'],
          text: 'The response inside the factory is to want more overtime, not to complain. That is invisible as a grievance and shows up only as a scheduling change.',
        },
        {
          when: ['post', 'complain', 'union', 'speak'],
          text: 'He has an account and does not use it for this. What gets posted is Eid photographs. What gets discussed is the rice, and the two never occupy the same screen.',
        },
        'The dormitory reached its full response in the first week and produced nothing measurable while doing it.',
      ],
    },
    {
      name: 'Remittance household head',
      role: 'Household head with a family member working abroad',
      segment: 'migration_workers',
      responses: [
        'He waited a week before asking for more, because asking early reads as failing to manage. The gap between the price rising and the request going out is the whole story of this lane.',
        {
          when: ['abroad', 'gulf', 'son', 'transfer', 'send'],
          text: 'The real cost of this shock left the country. The extra transfer came out of someone in Muscat working an extra shift, and no metric here will ever see it.',
        },
        {
          when: ['eid', 'festival'],
          text: 'Eid is the pressure point, because the transfer that was supposed to cover clothes and meat now covers rice. The household still holds Eid. It simply holds a smaller one and says nothing.',
        },
        {
          when: ['tell', 'talk', 'explain', 'admit'],
          text: 'He described the situation to the family abroad as manageable, twice, before it stopped being manageable. Protecting morale at that distance is understood by everyone as part of the job.',
        },
        'Nothing in this lane produces a complaint. It produces a slightly larger number in a remittance corridor, four to six weeks later.',
      ],
    },
    {
      name: 'Local imam',
      role: 'Neighbourhood mosque network',
      segment: 'elderly',
      responses: [
        'He does not spread the claim, he settles it, and this run shows he can settle it in either direction depending on what he heard that week.',
        {
          when: ['calm', 'panic', 'settle', 'role'],
          text: 'He called for patience and acknowledged in the same sentence that people were already skipping meals. Both halves were heard, and the second half is what got repeated.',
        },
        {
          when: ['older', 'elder', 'reach', 'phone', 'offline'],
          text: 'He is the only node in this run that reliably reaches older men and the households furthest from a phone. No campus page touches them and no ministry notice does either.',
        },
        {
          when: ['before', 'previous', 'history', 'remember'],
          text: 'He has seen four of these. That memory is what makes him calming, and it is also what makes him certain the explanation will arrive late, because it always has.',
        },
        'Nobody from any institution has ever asked him what he is telling people, which is a remarkable thing given how much weight he carries.',
      ],
    },
    {
      name: 'School teacher',
      role: 'Government school teacher',
      segment: 'middle_class',
      responses: [
        'He read the ministry notice, found it reasonable, and did not notice that the households in the same lane had settled the matter three weeks earlier on completely different evidence.',
        {
          when: ['notice', 'official', 'statement', 'explain'],
          text: 'The explanation is accurate and it is fourth in line. By the time it arrived, most people had already been handed three versions by someone they know personally.',
        },
        {
          when: ['affect', 'own', 'household'],
          text: 'His household absorbed it without a visible change, which is why this segment consistently underestimates the size of the problem when asked.',
        },
        {
          when: ['student', 'children', 'school', 'class'],
          text: 'He can see it in the classroom before he can see it anywhere else. Tiffin boxes get lighter and attendance on market days gets worse, and neither of those is anybody official statistic.',
        },
        'This lane is the one that reports the situation as stabilising, and it is genuinely the lane where it has.',
      ],
    },
    {
      name: 'Rural household farmer',
      role: 'Village household farmer',
      segment: 'rural',
      responses: [
        'He is on the other side of this price and it has still cost him, because the rise reached him as an input cost long before it reached him as income.',
        {
          when: ['benefit', 'gain', 'sell', 'farmer', 'profit'],
          text: 'Everyone assumes the grower gained. He sold at the old rate, weeks before the board changed, and watched the difference get made further up the chain.',
        },
        {
          when: ['city', 'dhaka', 'urban', 'hear'],
          text: 'What reaches the village is the Dhaka version of the argument, arriving through a phone, describing a market he does not sell into.',
        },
        {
          when: ['relief', 'government', 'support'],
          text: 'Relief in this lane is understood as an urban instrument. He does not expect any of it and he is not wrong.',
        },
        'The village response is slower, quieter and longer than the city one, and it appears in no part of this run that anyone is watching.',
      ],
    },
    {
      name: 'Policy researcher',
      role: 'Corporate and policy analyst',
      segment: 'corporate',
      responses: [
        'He is reading mention volume and sentiment, both of which are real numbers, and both of which describe the segment that changed least.',
        {
          when: ['data', 'metric', 'measure', 'dashboard', 'number'],
          text: 'The dashboard shows a spike and a decay. The decay is a campus lane losing interest. Nothing in it corresponds to a household resuming normal purchase, and there is no field in the tool that would have shown the difference.',
        },
        {
          when: ['district', 'region', 'map', 'worst'],
          text: 'The districts that look calmest are producing the least text, and in this run the correlation runs backwards: the quieter the lane, the more it moved.',
        },
        {
          when: ['recommend', 'fix', 'instrument', 'better'],
          text: 'Twenty grocers reporting basket size weekly would have caught this earlier and more accurately than every comment in the run put together, and it would have cost almost nothing.',
        },
        'He will report containment around round thirty-five, and he will be describing the noise rather than the shock.',
      ],
    },
  ],
}
