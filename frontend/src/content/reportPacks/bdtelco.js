// Report and interview content for the bdtelco scenario pack.
// Akashlink data pack repricing and a midnight throttling rumour, Dhaka.
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

export const BDTELCO_REPORT = {
  reportSections: [
    {
      title: 'Phase by phase: what the cascade actually did',
      paragraphs: [
        'The run covers forty rounds. The price rises at round two, the first speed test is posted at round five, and the first SIM tray is opened at round thirteen. The operator does not have a number describing any of that until round twenty-one, and the number it does have at round twenty-six is measuring the wrong people.',
        '**Rounds 1 to 8. The claim gets a proof.** At round two the tariff post publishes on schedule: notun data pack, notun daam. The post was scheduled and the comment section was not. At round five Tanjim posts a midnight speed test, 0.6 mbps against a remembered eighteen, and asks the question that decides the run: eta throttling na hoile ki. The repricing is arguable and the throttling claim is not, and that is exactly why the throttling claim wins. A tariff sheet can be disputed by an expert. A speed test can be reproduced by anybody holding a phone, and within hours thousands of people are running their own and finding what they were told to look for.',
        '**Rounds 9 to 18. The two lanes separate.** At round nine Mim starts a comment storm, proti mash e daam baray service ek i, boycott Akashlink, and keeps the number. At round thirteen a rider group does something quieter and far more expensive: ami dui SIM e chalai, ekhon Akashlink ta shudhu call er jonno rakhsi, data onno ta te. Nobody asked and nobody was told. At round seventeen a Bangla tech page correctly explains that a throttle cannot be proved from one speed test. The explainer performs well and changes nobody who has already run the test on their own phone, because you do not argue somebody out of an observation.',
        '**Rounds 19 to 30. The till turns.** At round twenty-one Nazma reads the change off the counter: Akashlink recharge is sharply down, people are loading other operators, and keu karon bole na, shudhu number ta bodle jay. At round twenty-six care line volume rises by a fifth and the operator reads that as the size of the problem. At round thirty a household bill manager moves the whole family onto another operator in one decision at the kitchen table and leaves the old SIM in the phone for OTP codes. Four connections change behaviour and none of them changes status.',
        '**Rounds 31 to 40. Official arrival.** At round thirty-four the regulator publishes a tariff filing. It is procedural, it says nothing about speed, and both the operator and the campaign pages quote it as support for their own position. At round thirty-nine Shakil states the whole scenario in two sentences: ami complain kori nai, complain korle time jay, order miss hoy, ami shudhu tray ta khule SIM ta ulta kore dilam. He is still an active subscriber. He has not spent anything since round thirteen.',
      ],
    },
    {
      title: 'Segment by segment: who moved, and in which direction',
      paragraphs: [
        '### Campus and gaming pages',
        'The loudest lane, the most reachable, and the least likely to leave. Students set the framing at round five and hardened it at round nine, and they did it with the single most dangerous kind of claim available: one that other people can verify for themselves. Mim wrote three furious comments and kept the number, because the whole friend group is on it and moving costs more socially than it saves monthly. This lane will produce the entire visible crisis and almost none of the revenue loss.',
        '### Delivery riders and shift workers',
        'The lane with the strongest reason to leave and the least time to complain. A rider lives on data all day and can price the difference to the taka, so the decision is arithmetic and takes about four seconds. Complaining, by contrast, costs a call, a queue and a missed order. At round thirteen the group works out the answer together and executes it privately: keep the old number alive for calls, move the data. Nothing about that appears in any system the operator owns.',
        '### Flexiload and recharge points',
        'The earliest reliable indicator in the run and the one nobody reads. Nazma can date the fall in Akashlink recharge to the week, can name which operator the load moved to, and hears no explanation from anybody, because a customer changing which operator he tops up does not owe the counter a reason. She holds the truest measurement in the scenario and there is no route by which it reaches the retention team, so it stops at the till.',
        '### Household bill managers',
        'Small in headcount, disproportionate in effect, and completely invisible as complaint. When one person buys the packs for a whole family, one decision at a kitchen table moves four connections at once and none of the four ever writes anything. This lane also decides slower and reverses slower: the switch was made on a monthly budget line, so it will be reviewed on a monthly budget line, not in response to a campaign.',
        '### Small traders, tutors and middle-class households',
        'The lane with the highest switching friction and the most patience. A number printed on a signboard, given to customers, tied to a bank account and a mobile wallet, is genuinely expensive to abandon, so this segment does the split rather than the move: the old number stays alive as an address and everything that consumes data goes elsewhere. On any subscriber report these people are perfectly retained. In revenue terms they are half gone.',
        '### Para committee elders and long-held numbers',
        'The most loyal subscribers in the run and the most effective spreaders of the churn. A number held for eleven years is not going to change, and the holder will say so proudly. He will also tell the entire building group which operator his grandson moved to and why, and in that lane a recommendation from an elder carries more weight than any campaign ever will.',
        '### The operator side: care, retention and marketing',
        'Busy, well instrumented and pointed in the wrong direction. Care volume rose by a fifth and was read as the size of the damage. The campaign calendar kept publishing into a comment section it had already lost, which turned the brand page into the venue for the complaint rather than the answer to it. Retention has an offer, a budget and a targeting engine, and it is aimed at everybody except the accounts that quietly stopped spending, because nothing in the stack flags an active connection with a collapsed recharge.',
      ],
    },
    {
      title: 'THE SILENCE LANE: the subscribers who stayed connected and stopped spending',
      paragraphs: [
        'This is the finding. Everything else in this report is context for it.',
        'Almost every phone in this population already holds a second SIM. That single fact removes every friction that churn normally has: there is no porting request, no visit, no call, no cancellation, and no moment where anybody has to defend a decision to anybody. There is a tray, a fingernail, and about two seconds. In this run the churn began at round thirteen, was well advanced by round thirty, and produced no ticket, no complaint, no survey response and no status change of any kind. The subscriber is still counted. The connection is still active. Only the money is gone.',
        '**What the silence is made of.** Three things. First, there is nothing to say: you do not announce that you have changed which SIM the data runs on, because it is not a grievance, it is a purchase. Second, complaining has a price and switching does not, which is precisely backwards from what the operator assumes: a rider loses an order to a call queue and loses nothing at all to a tray swap. Third, the old number is genuinely useful. It holds the OTP codes, the bank alerts, the family calls and the signboard, so nobody deletes it, and the account that would have shown up as a loss shows up as a retained customer instead.',
        '**Where it is nevertheless visible.** The lane leaves four traces, none of them in a care system. Recharge value per active connection, which falls while connection count holds perfectly steady. The flexiload counter, where the operator mix at the till changes weeks before anything else moves. Data volume per subscriber against voice volume per subscriber, where the divergence is the churn, drawn precisely. And a household pattern: four connections on one billing decision, three of which stop consuming in the same week for no reason anyone recorded.',
        '**Why it outlasts the visible conversation.** Complaint volume peaks around round twenty-six and falls, because complaining is tiring and the tech page explainer gave the argument somewhere to end. The tray swap does not reverse on the same schedule, or on any schedule. A rider who has run three months on the other network has moved his hotspot, his family group, his ride app and his wallet number across, and the second SIM is now the first one. Nothing in the operator response ever arrives in front of him, because every retention message goes to a customer list that still has him marked as active and content.',
      ],
    },
    {
      title: 'Amplifier profiles: the four accounts that decided the reach',
      paragraphs: [
        '### Tanjim, the gaming page admin',
        'The most consequential account in the run, and the only one that supplied a method rather than an opinion. A speed test screenshot is not an argument, it is an instruction, and everybody who followed it produced a personal confirmation that no explainer can take away from them afterwards. His motivation is standing inside a group that cares about latency, which means he cannot be bought and cannot be argued down, but he can be beaten at his own game by an operator willing to publish per-hour median speeds and invite the test.',
        '### Mim and the comment storm',
        'Highest visible volume, lowest commercial consequence, and the reason the operator misread the whole month. This account is angry, articulate, present in every thread and still paying, because the friend group is on the network and leaving costs more socially than it saves financially. Treating this lane as the crisis is what produced a response aimed entirely at people who had not left, and it is worth noting that it can be won back cheaply, precisely because it never went anywhere.',
        '### The rider group',
        'The quietest amplifier and the most expensive one. This is a closed group where practical advice moves faster than outrage, and the advice at round thirteen was operational: keep the old SIM for calls, put the data on the other one. Advice travels further than complaint because it has a use, and it converts on contact. Nothing published on a public page reaches this lane, and nothing this lane decides ever leaves it.',
        '### The Bangla tech page',
        'Correct, well argued and almost entirely ineffective. The round seventeen explainer says truthfully that one speed test cannot prove a throttle, and it convinces the people who never ran a test. Everyone who did run one now holds an observation, and an observation beats an explanation in every population on earth. This lane is where the operator will feel best about the response and where the response accomplished the least.',
      ],
    },
    {
      title: 'Trust map: who is believed, by whom, about what',
      paragraphs: [
        'Trust in this run is not one number. It is a map of who is believed about which kind of claim, and the layers are decided by whether the listener can check the claim personally.',
        '**About speed, the phone in your own hand is believed and nothing else is.** This is the layer that lost the operator the month. A reproducible claim installs itself as personal knowledge, and personal knowledge is not reachable by a statement, a certificate or a regulator filing.',
        '**About price, the tariff sheet is believed and resented.** Nobody in this run disputes what the pack now costs. The price is not a credibility problem, it is a permission problem: it gave the throttling claim a motive, and the motive is what made the claim plausible.',
        '**About what to do next, the rider group and the flexiload counter are believed.** Practical advice from someone in your own position carries more weight here than any official communication, and it is the only layer in the map that actually changes behaviour rather than opinion.',
        '**About the operator, nothing said on the operator page is believed while the comment section is open beneath it.** The scheduled campaign post is not read as information, it is read as evidence that nobody is listening. The regulator filing at round thirty-four fares no better: it is procedural, so both sides quote it, and a document that supports everybody supports nobody.',
        'The practical reading: this is not a message problem, it is an evidence problem. The claim was checkable and the answer was not. Until the operator publishes something a customer can verify on his own phone, every correct statement it makes will be filed as public relations.',
      ],
    },
    {
      title: 'What your dashboard will show, and why it is wrong',
      paragraphs: [
        'Between rounds nine and thirty-four the operator instruments produce three numbers that are individually true and collectively backwards.',
        '- **Care line volume rises by a fifth and is read as the size of the crisis.** Every caller in that queue is a customer who has not left and still expects a fix. It is the least representative sample available anywhere in the scenario, and it is the one the executive summary is built on.',
        '- **Active subscriber count does not move.** Dual SIM churn produces no disconnection, because the old number stays alive for OTP codes, bank alerts and the signboard. The retention report is technically correct and describes a customer base that has stopped buying.',
        '- **Sentiment recovers after the tech page explainer.** Argument volume falls because arguing is tiring, not because anybody came back. The recovery in the chart is the sound of a conversation ending, and the tray swaps continue after it.',
        'One number to hold onto: connection count in this run is flat and recharge value per active connection is not. Every complaint that was logged corresponds to several switches that were not, and the operator built the entire response around the logged ones.',
      ],
    },
    {
      title: 'Recommendations',
      paragraphs: [
        '**1. Switch the churn metric to recharge value per active connection, this week.** Connection count cannot see a dual SIM move and never will. A simple weekly read of data spend against voice spend on the same connection draws the churn precisely, it uses data the billing system already holds, and it would have fired at round thirteen instead of round twenty-six.',
        '**2. Put a panel of forty flexiload counters on a weekly question.** Which operator is the load going to, and since when. Nazma had the answer at round twenty-one and there was no way to send it anywhere. This is the cheapest early-warning instrument available in the market and it also tells you the direction of the loss, which no internal metric does.',
        '**3. Answer a reproducible claim with a reproducible answer.** An explainer arguing that one speed test proves nothing loses to a speed test. Publish per-hour median speed by area, invite people to check it, and accept the bad hours in public. The only thing that beats an observation is a better observation.',
        '**4. Take the campaign off the brand page for ten days.** A scheduled post into an angry comment section is read as proof that nobody is listening, and it converts the brand page into the venue for the complaint. Move the spend, keep the page for replies only, and give one named person the authority to pause the calendar without a meeting.',
        '**5. Build the silent switcher list and make it an offer inside fourteen days.** Active connections whose data recharge collapsed while voice held are the churn, individually identifiable and currently receiving nothing. They are also cheap to win back in the first month and effectively unreachable after the third, because by then the second SIM has become the first one.',
        '**6. Staff the care line as retention, not as a crisis gauge.** The people calling are the loyal remainder and they are the easiest save in the run. Give the agents something to give away, stop reporting the queue length as the size of the damage, and read the queue as a list of customers who still expect the operator to fix it.',
      ],
    },
  ],

  reportAgentAnswers: {
    first: 'The earliest signal is a midnight speed test posted into a gaming group at round five, 0.6 mbps against a remembered eighteen. It is reproducible, so within hours thousands of people have run the same test on their own phones and confirmed it to themselves, which is a much harder thing to undo than a rumour.',
    spread: 'It spreads because the claim can be checked on any phone. The repricing at round two supplied the motive and the speed test supplied the method. Rider groups and campus pages then carried it as practical advice rather than as accusation, and advice travels further than outrage because it has a use at the other end.',
    trust: 'Trust splits by whether a claim can be checked personally. About speed, the phone in your own hand is believed and nothing else is. About price, the tariff sheet is believed and resented. About what to do next, the rider group and the flexiload counter are believed. And nothing on the operator page is believed while the comment section is open underneath it.',
    quiet: 'The quiet lane is the finding. Almost every phone here already holds a second SIM, so churn needs no porting request, no call and no decision anybody has to defend. It needs a tray and two seconds. The connection stays active for OTP codes and family calls, the subscriber is still counted, and only the recharge value falls, which means the loss never appears as a loss anywhere.',
    retail: 'The flexiload counter is the earliest reliable indicator in the run. Nazma can date the fall in Akashlink recharge to the week and name which operator the load moved to, weeks before complaint volume peaks. No customer explains the switch, because changing which operator you top up does not owe the counter a reason, and there is no route by which what the till knows reaches the retention team.',
    women: 'Household bill managers are small in headcount and disproportionate in effect. One person buys the packs for the whole family, so a single decision at the kitchen table moves four connections at once and not one of the four appears as a complaint. That lane also reverses slowly, because the switch was made on a monthly budget line and will be reviewed on one.',
    young: 'Students carry the reach and stay. Mim wrote three furious comments and kept the number, because the friend group is on the network and moving costs more socially than it saves monthly. Tanjim the gaming page admin is the consequential one: he supplied a method rather than an opinion, and everyone who followed it produced a personal confirmation no explainer can remove.',
    timeline: 'Four phases across forty rounds. Rounds one to eight are the claim getting a proof, the tariff post at two and the midnight speed test at five. Rounds nine to eighteen split the lanes, a loud comment storm at nine, a silent tray swap in the rider group at thirteen, a correct and ineffective explainer at seventeen. Rounds nineteen to thirty are where the till turns, recharge down at twenty-one, care volume up at twenty-six, a whole family moved at thirty. Rounds thirty-one to forty are the procedural regulator filing and a rider stating the obvious at thirty-nine.',
    compare: 'Compare the complainers with the switchers. The complainers are visible, articulate, countable and still paying. The switchers are invisible, silent, still counted as active subscribers and no longer spending. They are two different populations, the operator has instrumentation for the first one only, and in this run they are not even correlated.',
    worst: 'The biggest risk is reading care line volume as the size of the damage. Call volume rose by a fifth and every one of those callers is somebody who has not left. Build the response around them and you spend the entire budget reassuring the loyal remainder while the tray swaps continue quietly underneath, and after three months the second SIM has become the first one.',
    recover: 'Recovery runs through the recharge counter and the rider group, not through the brand page. Build the list of active connections whose data spend collapsed while voice held, and make them an offer inside fourteen days, because they are cheap to win back in the first month and effectively unreachable after the third. Then answer the speed claim with something a customer can verify on his own phone.',
    recommend: 'Six things. Change the churn metric to recharge value per active connection this week. Put forty flexiload counters on one weekly question about where the load is going. Answer a reproducible claim with a reproducible answer, per-hour median speeds by area. Take the campaign off the brand page for ten days. Build the silent switcher list and make an offer inside fourteen days. And run the care line as retention rather than as a crisis gauge.',
  },

  interviewAgents: [
    {
      name: 'Delivery rider',
      role: 'Rider running on data all day',
      segment: 'urban_working',
      responses: [
        'He did not call and did not post. He opened the tray between two deliveries and moved the data to the other SIM, because a complaint costs time and time costs an order.',
        {
          when: ['complain', 'call', 'care', 'ticket', 'post', 'why not'],
          text: 'A call to the care line is fifteen minutes on hold and two orders gone. Switching is free and takes four seconds, so the complaint is the expensive option and nobody chooses it.',
        },
        {
          when: ['old number', 'keep', 'otp', 'sim', 'still', 'active'],
          text: 'The old number is still in the phone and always will be. It holds the OTP codes, the bank alerts and the family calls, so he is still counted as a customer while spending nothing.',
        },
        {
          when: ['back', 'return', 'offer', 'win', 'recover', 'come back'],
          text: 'An offer in the first month would have brought him back. Three months in, the hotspot, the ride app and the wallet number are all on the new SIM, and moving back is now the expensive direction.',
        },
        'Nobody has ever asked him anything. In the whole run he sent one message to a rider group and it moved more people than the comment section did.',
      ],
    },
    {
      name: 'University student',
      role: 'Campus page and gaming group member',
      segment: 'students',
      responses: [
        'She wrote three furious comments and kept the number, because the whole friend group is on it and moving costs more socially than it saves monthly.',
        {
          when: ['speed test', 'throttl', 'midnight', 'test', 'prove', '0.6'],
          text: 'The point of the speed test was never the number, it was that anyone could run it. Once you have seen it on your own phone at one in the morning, no explainer is going to talk you out of it.',
        },
        {
          when: ['explainer', 'tech page', 'article', 'correction', 'convince'],
          text: 'The tech page was probably right and it did not matter. It argued with the measurement instead of taking one, and you cannot argue somebody out of something they watched happen.',
        },
        {
          when: ['leave', 'switch', 'churn', 'stay', 'boycott'],
          text: 'She said boycott and did not leave. The number is in every group, every account and every friend contact list, and none of that is worth two hundred taka a month.',
        },
        'The loudest voice in this whole run never cost the operator a single taka, and the operator spent the month answering it.',
      ],
    },
    {
      name: 'Flexiload counter operator',
      role: 'Recharge point in a Mirpur lane',
      segment: 'retailers',
      responses: [
        'She watches the till, not the news. Akashlink recharge fell first, nobody at the counter has ever explained why, and so there is nothing to pass upward.',
        {
          when: ['when', 'first', 'date', 'week', 'start', 'notice'],
          text: 'It showed in the second week, clearly enough to name the day. Same faces at the counter, same money in the hand, different operator on the screen.',
        },
        {
          when: ['why', 'reason', 'ask', 'customer', 'tell', 'explain'],
          text: 'Nobody says why and nobody owes an explanation for it. Changing which operator you load is not a complaint, it is just a purchase, so the reason never gets spoken out loud at all.',
        },
        {
          when: ['report', 'company', 'operator', 'upward', 'rep', 'know'],
          text: 'The distributor comes to collect and to sell, never to ask. He could tell them the exact week it turned and which operator took the money, and in eight years nobody has asked him a single question.',
        },
        'The counter knows before the company does, every single time, and the counter has no way to say so.',
      ],
    },
    {
      name: 'Household bill manager',
      role: 'Buys the data packs for the whole family',
      segment: 'women',
      responses: [
        'She buys the packs for the whole family, so one decision at the kitchen table moves four connections at once, and not one of the four appears as a complaint.',
        {
          when: ['decide', 'family', 'kitchen', 'who', 'household', 'four'],
          text: 'Nobody else in the house was consulted and nobody objected. The packs simply arrived on a different operator that month, and by the second month it was just how things are.',
        },
        {
          when: ['price', 'budget', 'cost', 'money', 'taka', 'save'],
          text: 'It is a monthly line in a budget that has several other monthly lines under pressure. When the price moved, that line got reviewed, and once a line has been reviewed it does not go back without a reason.',
        },
        {
          when: ['back', 'return', 'offer', 'campaign', 'convince'],
          text: 'A campaign will not move him. A better price, seen at the recharge counter, at the moment the next month is being planned, would.',
        },
        'This household changed four connections and generated nothing that any system anywhere recorded as a change.',
      ],
    },
    {
      name: 'Private tutor',
      role: 'Runs online classes at night on a data pack',
      segment: 'middle_class',
      responses: [
        'He teaches over data after ten at night, which is exactly the window the throttling claim is about, so for him the rumour was not a rumour, it was a work problem.',
        {
          when: ['test', 'speed', 'check', 'prove', 'midnight', 'night'],
          text: 'He ran the test himself for four nights and wrote the numbers down, because a dropped class is a lost student. That notebook is better evidence than anything either side published.',
        },
        {
          when: ['switch', 'leave', 'number', 'signboard', 'keep', 'split'],
          text: 'The old number is printed on the coaching leaflets and known to every parent, so it stays. Everything that uses data went to the other SIM, and on the operator books that reads as a fully retained customer.',
        },
        {
          when: ['complain', 'call', 'care', 'post', 'ticket'],
          text: 'He called once, waited, explained the problem to somebody who read a script back to him, and did not call again. One bad call is enough to close that door permanently.',
        },
        'He is the customer the operator thinks it still has, and it has half of him.',
      ],
    },
    {
      name: 'Para committee elder',
      role: 'Held the same number for eleven years',
      segment: 'elderly',
      responses: [
        'He has held the same number for eleven years and will not change it, but he told the whole building group which operator his grandson moved to.',
        {
          when: ['loyal', 'stay', 'change', 'switch', 'why not'],
          text: 'The number is on every document he owns and in every phone that matters to him. Changing it is not a price decision, it is an identity problem, and no offer will touch it.',
        },
        {
          when: ['tell', 'advice', 'building', 'group', 'others', 'recommend'],
          text: 'He is asked what to do by half the building because he is the one who is always at home. What he says on a Friday afternoon is what four households do on Saturday.',
        },
        {
          when: ['believe', 'trust', 'operator', 'statement', 'regulator'],
          text: 'He read the regulator notice and understood it as government paper that settles nothing. What he believes is what his grandson showed him on a phone screen at midnight.',
        },
        'The most loyal subscriber in the run is also one of the most effective reasons other people left.',
      ],
    },
    {
      name: 'Village shopkeeper',
      role: 'Rural subscriber with one usable network',
      segment: 'rural',
      responses: [
        'He heard the whole argument and could do nothing with it, because out here only one network is usable and the choice everybody in Dhaka has does not exist.',
        {
          when: ['switch', 'second sim', 'choice', 'option', 'other operator'],
          text: 'The second SIM is in the phone and gets no signal past the bazaar. So the price rise here is simply absorbed, and absorption produces no data at all.',
        },
        {
          when: ['price', 'cost', 'pack', 'smaller', 'less'],
          text: 'He buys a smaller pack instead of a different one. The spend falls without the customer moving, which looks the same in the accounts as churn and needs a completely different response.',
        },
        {
          when: ['hear', 'dhaka', 'city', 'rumour', 'reach', 'group'],
          text: 'The throttling argument reached him a week late through a relative in the city, fully settled and no longer a question. Nothing from the operator reached him at all.',
        },
        'This lane never complains and never leaves, and it is quietly spending less every month while being reported as stable.',
      ],
    },
    {
      name: 'Remittance household manager',
      role: 'Household with a family member in the Gulf',
      segment: 'migration_workers',
      responses: [
        'The family calls happen after midnight because of the time difference, which puts this household in exactly the window the throttling claim is about.',
        {
          when: ['call', 'video', 'gulf', 'abroad', 'family', 'night'],
          text: 'A video call that breaks up at one in the morning is not a technical complaint, it is a missed conversation with somebody far away. That is why this lane took the claim personally when the students took it as an argument.',
        },
        {
          when: ['switch', 'sim', 'change', 'move', 'data'],
          text: 'The household moved the calling data to the other SIM within a fortnight and told nobody. The old number stays for the bank messages, which is where the remittance alert lands.',
        },
        {
          when: ['complain', 'care', 'report', 'post', 'ticket'],
          text: 'Nobody here calls a care line. The person who would make that call is working a shift in Muscat and the person at home does not consider it his place to argue with a company.',
        },
        'The loss in this lane is a monthly data pack that simply stops being bought, and every metric the operator holds will show the connection as healthy.',
      ],
    },
    {
      name: 'Retention analyst',
      role: 'Akashlink retention and reporting',
      segment: 'corporate',
      responses: [
        'He reports call volume as the measure of the damage, and the number is real. It is also a precise count of the customers who have not left.',
        {
          when: ['data', 'metric', 'dashboard', 'churn', 'measure', 'number'],
          text: 'Connection count is flat and he has been reporting it as retention. Recharge value per active connection is not flat, and it sits in a billing extract nobody puts on the weekly slide.',
        },
        {
          when: ['dual sim', 'tray', 'switch', 'silent', 'invisible'],
          text: 'The stack has no concept of a connection that is alive and not spending. Every churn model he owns starts from a disconnection event, and in this market the disconnection event never happens.',
        },
        {
          when: ['fix', 'recommend', 'better', 'instrument', 'next', 'offer'],
          text: 'Data spend against voice spend on the same connection draws the churn precisely, using data already held. That list would have existed at round thirteen and every account on it is cheap to save in the first month.',
        },
        'He will report the month as contained around round thirty-six, and he will be describing the queue rather than the till.',
      ],
    },
  ],
}
