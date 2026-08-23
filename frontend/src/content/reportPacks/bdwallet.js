// Report and interview content for the bdwallet scenario pack.
// Cashout fee rumour and a quiet run on Sylhet agent points.
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

export const BDWALLET_REPORT = {
  reportSections: [
    {
      title: 'Phase by phase: what the cascade actually did',
      paragraphs: [
        'The run covers forty rounds. The balances start leaving at round seven. The first number inside the company that anyone could act on does not exist until round twenty-eight, and even then it is flat. That gap is what this report exists to describe.',
        '**Rounds 1 to 8. The forward and the first withdrawal.** At round two Belal forwards the circular screenshot into a para committee group with an honest caveat attached: he could not verify it. The caveat travels with the image and changes nothing, because prudence does not need proof. At round four Shonchoy Pay publishes a scheduled Eid campaign post into the same feeds, cheerful and completely unaware, and to anyone holding the screenshot it reads as a brand talking about shopping while the money is in question. By round seven Rahela has taken the whole balance out and told nobody. Nothing measurable has happened yet.',
        '**Rounds 9 to 18. The joke and the float.** At round eleven a campus meme page turns the balance limit into a joke about worrying whether twelve taka crosses it, and that joke gets more reach in one evening than the helpline gets calls in a week. Reach is not the damage. The damage lands at round fifteen, when Suhel is out of cash by eleven in the morning, has taken not one deposit all day, and finds the distributor dry as well. The first real measurement in this run is an empty drawer, and there is no field for it anywhere.',
        '**Rounds 19 to 30. The correction that misses, and the group decision.** At round nineteen a Bangla business page reports, correctly, that no circular exists and the fee schedule is unchanged. It circulates among people who read business pages and reaches no agent point at all. At round twenty-four Jesmin tells the twenty women whose savings book she holds to keep this month in cash, and twenty households empty their balances in a day on one decision made by one person. At round twenty-eight the helpline is still flat, because a plan does not generate a ticket.',
        '**Rounds 31 to 40. The cash leaves the system.** By round thirty-three the bazaar is short of cash and traders are selling on credit, which everyone in the bazaar reads as a bazaar problem rather than a wallet problem. At round thirty-eight Shonchoy Pay publishes a fee table in Bangla and English. It is accurate, it is calm, it is well made, and it is addressed to the people who still have a balance.',
      ],
    },
    {
      title: 'Segment by segment: who moved, and in which direction',
      paragraphs: [
        '### Remittance receiving households',
        'The core lane and the quietest. These households hold the largest balances in the run and the least tolerance for risk, because the money in the wallet is not savings, it is somebody else working a night shift eight hours away. Response is immediate, complete and unannounced: the balance goes to zero in one visit, not in instalments. They do not need the rumour to be true. Being wrong about it costs a small charge and being right about it costs the month.',
        '### Women receiving transfers',
        'The decision layer inside that lane. In this run the withdrawal is made by the person who receives the transfer, and it is made before the household discusses it. The money moves into the tin in the house and the family finds out by seeing it there. This is also the lane with the least appetite for a phone call to a helpline, because a helpline conversation about whether your money is safe is a conversation in which you have to describe how much of it there is.',
        '### Agent point operators and mudi dokan agents',
        'The earliest reliable indicator in the whole run and the only one with a hard number attached. Suhel reads the run as float: the same customers, the same hours, and no deposits at all. By round fifteen he has a precise reading of the damage and no route by which to report it, because the distributor asks how much cash he needs and never why he needs it. He is also, separately, the highest-trust node in the scenario, which makes him the cheapest place a correct sentence could have been put.',
        '### Shomiti groups and para committees',
        'The multiplier. These are not audiences, they are decision structures: Jesmin does not persuade twenty households, she decides for them, and Belal does not argue a case, he forwards a caution. A single message in a group of this kind converts directly into twenty withdrawals on the same day, with no intervening discussion for anyone to observe. No amount of public messaging reaches inside these groups, because the company has never been in one.',
        '### Campus meme pages',
        'Highest reach, zero exposure. The meme page has twelve hundred taka in the wallet and no reason to move it, and it produced the loudest artefact in the run. Its contribution is not information and not even grievance, it is recognisability: it gave the fear of a balance limit a shape people could laugh at and forward, which is a far more durable format than a claim.',
        '### Bazaar traders and wholesalers',
        'The lane that feels the second-order effect and never connects it to the cause. By round thirty-three cash is short across the bazaar and trade moves onto credit. Traders describe this as a bad week for cash, not as a wallet story, so the clearest downstream evidence in the run is filed under the wrong heading by the people holding it.',
        '### The senders abroad',
        'The lane nobody in the country can see. A household that has emptied the wallet also tells the sender to hold the next transfer, or asks for it through a friend coming home on leave. That money never enters the system, so it is never recorded as having left. The true size of this run is partly a number in Muscat that no dashboard in Sylhet will ever show.',
      ],
    },
    {
      title: 'THE SILENCE LANE: a bank run that arrives one polite customer at a time',
      paragraphs: [
        'This is the finding. Everything else in this report is context for it.',
        'A run on a wallet does not look like a run. It looks like an ordinary Tuesday. Nobody announces anything, nobody raises a voice, nobody queues in a way a photograph would find interesting. Households arrive at the agent point one at a time, greet the operator, take everything, and go home. Each withdrawal on its own is completely unremarkable and entirely within the rules. Together, inside four hours, they are a run. In this scenario the wallet loses most of the balance it holds in one upazila and receives, in exchange, not a single complaint.',
        '**What the silence is made of.** Three things. First, taking out your own money is not a grievance: there is no counterparty, nobody did anything to you, and a complaint needs somebody to complain about. Second, the cost of being wrong is lopsided. Withdrawing early costs a cashout charge and being frozen costs the whole balance, so the rational move is to act on a rumour you do not actually believe, and nobody defends in public a position they never took. Third, saying out loud that you are pulling your money out is either an accusation you cannot support or an announcement of what you hold, and in a para where everyone knows everyone, neither is a safe thing to say.',
        '**Where it is nevertheless visible.** The lane leaves four traces, and not one of them is in a listening tool. Cash out against cash in at each agent point, which inverts before anything else in the run moves. The distributor resupply request, which spikes and then cannot be met. A shomiti savings book, where twenty decisions get written down by hand on the same day. And bazaar credit, because cash that has left the wallet and gone into a tin at home is cash that is not circulating, which the traders feel as a liquidity problem a fortnight later.',
        '**Why it outlasts the visible conversation.** The joke dies around round thirty. The screenshot stops being forwarded. Nothing about that decay puts a single taka back into the wallet. A household holding cash in a tin has no trigger to reverse the decision, because there was no argument to lose and no announcement to be reassured by: reversal requires a positive reason to deposit, and none is ever supplied. Six weeks after the noise ends the withdrawals have recovered and the deposits have not, which is the only number in this scenario that actually describes the damage.',
      ],
    },
    {
      title: 'Amplifier profiles: the four accounts that decided the reach',
      paragraphs: [
        '### Belal, the para committee secretary',
        'The origin node and the most misread. His motivation is not grievance, it is duty: he considers it his job to tell the committee what is going around, and he said plainly that he could not verify it. That caveat is exactly what made the message safe to forward and impossible to refute, because he never claimed it was true. His reach is small and dense, perhaps two hundred households, all of whom know him personally. A denial aimed at the public does nothing here. A correction from a name this committee recognises would move the same evening.',
        '### Jesmin, the shomiti group leader',
        'Not an amplifier at all in the usual sense, and the most consequential actor in the run. She does not spread a claim, she makes a decision on behalf of twenty households who have handed her the savings book precisely so that they do not have to decide. Her motivation is protective and conservative: if this turns out to be nothing, the money goes back in and nobody has lost much. Twenty balances move on one sentence at round twenty-four. There are perhaps forty women like her in this upazila and the company can name none of them.',
        '### The campus meme page',
        'Highest raw reach, lowest stake, and the reason the claim outlived the screenshot. It is not attacking the wallet; the limit joke was simply the strongest post available that week. This matters because it means the page is not an opponent, it is an appetite, and it will carry an accurate and funny thing exactly as fast as it carried this. Treating it as hostile is the one response guaranteed to produce a second joke by the evening.',
        '### The Bangla business page',
        'The only actor in the run that got the facts right, at round nineteen, in public, for free. It reported that no circular exists and the fee schedule is unchanged. Its audience is people who read business pages, which is to say people who were never going to empty an account over a forwarded image. High accuracy, real reach, and close to zero effect on behaviour: this is the lane that will make the dashboard look like the story was covered.',
      ],
    },
    {
      title: 'Trust map: who is believed, by whom, about what',
      paragraphs: [
        'Trust here is not a score for the brand. It is a map of who is believed on which kind of question, and on the question that actually drove this run the brand does not appear on the map at all.',
        '**About the fee, the agent point operator is believed absolutely.** He is standing next to the drawer, he handles the charge every day, and he has no visible reason to lie. Nobody checks him and nobody needs to. He is also answering with whatever he heard from the previous customer, because nobody has ever sent him the correct line.',
        '**About whether a rule exists, the forwarder is believed, precisely because he did not claim it was true.** A message that says this is going around and I could not verify it is unfalsifiable. There is nothing in it to correct. A denial can defeat a claim; it cannot defeat a caution.',
        '**About whether the money is safe, nobody is believed yet, and Shonchoy Pay least of all.** A brand publishes a fee table when fees are in question, so at round thirty-eight the clarification reads to the affected households as confirmation. The company is in the worst possible position on this question: it is the only party with the answer and the only party with an obvious interest in the answer.',
        '**About what everyone else is doing, the shomiti book beats anything on a screen.** In a run, the decisive information is not whether the claim is true but whether your neighbours have already acted, and that is settled inside groups no institution can see into.',
        'The practical reading: the company has no standing on the only question being asked, and the two people who do have standing, the operator and the group leader, were never given anything to say.',
      ],
    },
    {
      title: 'What your dashboard will show, and why it is wrong',
      paragraphs: [
        'Between rounds seven and thirty this scenario produces the healthiest looking dashboard in the whole set, and every number on it is true.',
        '- **Complaint volume is flat.** Not low, flat, all week. It is read as containment. In fact it is the signature of the event: people cashing out do not have a complaint, they have a plan, and a plan does not generate a ticket.',
        '- **App engagement rises.** Sessions per user go up during a run, because people open the app to check a balance and then to move it. The engagement chart moves in the direction the team wants while the deposit base underneath it empties.',
        '- **Sentiment reads neutral with a mild positive.** The loudest thing anybody said about the wallet that week was a joke, and a joke scores as light. The households that emptied their accounts wrote nothing at all and are therefore absent from the sentiment number entirely.',
        'One number to hold onto: the balances leave between round seven and round twenty-four, and the earliest lane the company is actually watching does not register anything until after round twenty-eight. The team is monitoring the one signal in this run that moves last.',
      ],
    },
    {
      title: 'Recommendations',
      paragraphs: [
        '**1. Instrument the float, not the timeline.** Cash out against cash in, per agent point, twice a day. That ratio inverts at round fifteen in this run, thirteen rounds before anything else the company watches moves at all. Thirty agent points reporting it would have cost less than the campaign post that went out at round four.',
        '**2. Put the sentence in the hands of the operator.** One printed line in Bangla at the counter, saying what is true about limits and fees, given to every agent point in the district before anything is published anywhere. He is asked the question twenty times a morning and currently answers with whatever the last customer told him.',
        '**3. Hold the scheduled posts.** The Eid campaign post at round four did measurable harm by being cheerful in the wrong week. A rumour tripwire that pauses the content calendar for a district costs nothing and removes the most avoidable damage in the run.',
        '**4. Answer the freeze claim, not the fee claim.** The claim that moved money was that balances above a limit get frozen. The fee table published at round thirty-eight answers the smaller half of the rumour and confirms the frame. Say plainly that no balance has ever been frozen and no limit exists, in one sentence, in Bangla, in the format people are forwarding.',
        '**5. Go back down the route the rumour came up.** Give the correction to para committee secretaries and shomiti group leaders as a forwardable image from a named local person, because that is the object this population passes around. Twenty group leaders reached directly is worth more than any number of impressions on a business page.',
        '**6. Measure the return, not the calm.** Withdrawals recover on their own; deposits do not. Track cash in per agent point for six weeks after the conversation dies, and treat the deposit line, not the complaint line, as the definition of recovery.',
      ],
    },
  ],

  reportAgentAnswers: {
    first: 'The earliest signal is a forwarded circular image inside para committee and shomiti groups at round two, claiming cashout fees are rising and balances above a limit will be frozen. It carries a caveat that nobody could verify it, and it moves anyway. The first behavioural move follows five rounds later, when a household empties a balance and tells nobody.',
    spread: 'It spreads because forwarding it is an act of care rather than an accusation. A committee secretary passes it on as prudence, a shomiti leader converts it into a decision for twenty households at once, and a campus meme page gives it a second life as a joke at round eleven. None of those three is trying to damage the wallet, which is why none of them can be argued with.',
    trust: 'Trust splits by question. About the fee, the agent point operator is believed absolutely, because he is standing next to the drawer. About whether a rule exists, the forwarder is believed, because he never claimed it was true, only that it was going around. About whether the money is safe, nobody is believed yet, and Shonchoy Pay least of all, because a brand publishes a fee table when fees are in question.',
    quiet: 'The quiet lane is the whole event. This is a bank run that arrives one polite customer at a time: no complaint, no raised voice, no queue worth photographing, just households taking everything and going home. Taking out your own money is not a grievance, so it generates no ticket, and the only witness in the entire scenario is an agent point that is dry by eleven in the morning.',
    retail: 'The agent point is the earliest and most accurate instrument in the run and the least consulted. Suhel reads the event as float: same customers, same hours, no deposits at all. He has a precise reading of the damage by round fifteen and no route to report it, because the distributor asks how much cash he needs and never why.',
    women: 'Women receiving the transfers are the decision layer. Rahela empties the balance the same afternoon and tells nobody, including the household, and the money goes into a tin in the house. Jesmin, holding the savings book for twenty women, moves twenty balances with one sentence at round twenty-four. Neither action produces a single line of text anywhere.',
    young: 'The campus meme page carries the reach and holds none of the risk. It has twelve hundred taka in the wallet and no reason to move it, and it produced the loudest artefact in the run because the limit joke was the strongest post available that week. It is an appetite rather than an opponent, and it will carry something accurate at exactly the same speed.',
    timeline: 'Four phases across forty rounds. Rounds one to eight are the forward and the first silent withdrawal, with nothing measurable happening. Rounds nine to eighteen are the joke and the float collapse, and the agent point runs dry at round fifteen. Rounds nineteen to thirty are the correct explanation missing its audience while a shomiti group moves twenty households. Rounds thirty-one to forty are cash leaving the system and a fee table arriving for people who never moved.',
    compare: 'Compare the lane that posts with the lane that withdraws. The meme page produced the most reach in the run and moved no money it had any claim on. The shomiti group produced one sentence in a private group and emptied twenty balances the same day. Everything the company can see belongs to the first lane and everything that cost it money belongs to the second.',
    worst: 'The biggest risk is reading a flat helpline as containment and closing the incident when the fee table goes out. The withdrawals will recover by themselves; the deposits will not. A household holding cash in a tin has no trigger to reverse, because there was never an argument to lose, and six weeks later the deposit base is still down while every visible metric looks normal.',
    recover: 'Recovery runs through the counter, not through the app. The households now holding cash will not open a post from a page they do not follow, and the only person they will believe is the operator who tells them at the counter, next time they come in, that the money was never at risk. The second route is the shomiti leader who made the decision to withdraw, because she is the only one who can make the opposite decision.',
    recommend: 'Six things. Report cash out against cash in per agent point twice a day, because that ratio turns thirteen rounds before anything else. Put one printed Bangla line in the hands of every operator before publishing anything. Pause the scheduled campaign posts in an affected district. Answer the freeze claim rather than the fee claim, because the freeze is what moved the money. Hand the correction to committee secretaries and shomiti leaders as something forwardable from a local name. And measure the deposit line for six weeks after the talk stops, because that is the only definition of recovery that means anything.',
  },

  interviewAgents: [
    {
      name: 'Village household head',
      role: 'Rural household receiving transfers',
      segment: 'rural',
      responses: [
        'She keeps the money in the house now, in the same tin the family used before the wallet existed. Nothing has asked for it back.',
        {
          when: ['app', 'wallet', 'use', 'open', 'again', 'phone'],
          text: 'She has not opened the app since the day the balance came out. The phone still has it and the icon is now just something on the screen.',
        },
        {
          when: ['hear', 'rumour', 'circular', 'screenshot', 'who told', 'source'],
          text: 'It came from the committee, not from a page. Nobody here reads a business page and nobody needed to, because the person who sent it lives four houses away.',
        },
        {
          when: ['agent', 'point', 'far', 'distance', 'travel', 'queue'],
          text: 'The nearest agent point is a bus ride away. That is why the balance came out in one go rather than a little at a time, and it is why it will not go back in a little at a time either.',
        },
        'She is not angry with the company. She simply does not need it, and six weeks on that is a harder problem than anger would have been.',
      ],
    },
    {
      name: 'Wage receiving worker',
      role: 'Worker paid into the wallet',
      segment: 'urban_working',
      responses: [
        'His salary lands in the wallet whether he trusts it or not. On the first payday after the screenshot he took the entire month out within an hour of the message reaching him.',
        {
          when: ['choice', 'avoid', 'leave', 'stop using', 'quit', 'switch'],
          text: 'He cannot leave the wallet, the employer pays into it. What he can do is treat it as a letterbox, and that is what most of the floor did that month.',
        },
        {
          when: ['queue', 'wait', 'line', 'cash', 'agent', 'counter'],
          text: 'The queue at the agent point on payday was the usual length and took twice as long, because every person in it was taking the full amount instead of a part of it.',
        },
        {
          when: ['post', 'complain', 'helpline', 'call', 'report'],
          text: 'He called nobody. There was nothing to report. The money came out fine, the machine worked, the boy at the counter was polite. That is the problem.',
        },
        'Six weeks later he still empties it on payday and pays the charge every month to do it. What that charge buys him is worth knowing.',
      ],
    },
    {
      name: 'School teacher',
      role: 'Salaried app user',
      segment: 'middle_class',
      responses: [
        'He read the business page explainer at round nineteen, found it convincing, and never noticed that the households in his own building had settled the matter three weeks earlier on completely different evidence.',
        {
          when: ['fee table', 'clarification', 'official', 'statement', 'correction', 'post'],
          text: 'The fee table was the first useful thing the company said, and he was never worried in the first place. It was written for people like him, which is precisely the mistake.',
        },
        {
          when: ['balance', 'money', 'withdraw', 'move', 'keep'],
          text: 'He left the balance where it was. Two bills are paid from it and moving the money would have been more work than the risk was worth, which is a calculation only somebody on a salary can make.',
        },
        {
          when: ['believe', 'trust', 'who', 'source', 'doubt'],
          text: 'He believes the company over the committee group, and he is aware that in this building it makes him the exception rather than the sensible one.',
        },
        'He is the lane the correction reached and the lane that never moved, and those are the same fact stated twice.',
      ],
    },
    {
      name: 'Distribution channel manager',
      role: 'Wallet distribution and channel desk',
      segment: 'corporate',
      responses: [
        'He is watching complaint volume, it is flat, and he reads that as containment. The float reports land on a different desk and a week later.',
        {
          when: ['data', 'metric', 'dashboard', 'number', 'measure', 'engagement'],
          text: 'Engagement was up that week. People opened the app more often than usual and every one of those sessions was somebody checking a balance before taking it out. The number moved in the right direction for the worst possible reason.',
        },
        {
          when: ['float', 'cash', 'distributor', 'liquidity', 'agent', 'counter'],
          text: 'Cash out against cash in, per point, twice a day, would have shown this at round fifteen. The data exists. It has only ever been used for accounting, never as a warning.',
        },
        {
          when: ['recommend', 'fix', 'instrument', 'better', 'next', 'advice'],
          text: 'Thirty agent points reporting that ratio would have cost less than the Eid campaign post that went out at round four and did harm. That is the whole cost of catching this thirteen rounds earlier.',
        },
        'He will mark the incident closed when the fee table publishes. The deposit base will still be down in the second month and it will be filed under seasonality.',
      ],
    },
    {
      name: 'Transfer receiving household head',
      role: 'Household receiving from Muscat',
      segment: 'migration_workers',
      responses: [
        'He told the family in Muscat to hold the next transfer for a week. That money never entered the system at all, so the company will never record it as having left.',
        {
          when: ['abroad', 'muscat', 'gulf', 'son', 'send', 'transfer', 'remit'],
          text: 'It came home with a friend on leave instead. That route is slower, it is older than the wallet, and it never fully went away.',
        },
        {
          when: ['tell', 'explain', 'why', 'reason', 'talk'],
          text: 'He gave no reason on the call. Saying the money might be frozen sounds like an accusation, and saying it to somebody finishing a night shift eight hours away sounds like panic.',
        },
        {
          when: ['back', 'return', 'again', 'resume', 'trust'],
          text: 'He will use it again when a transfer is urgent enough. That is convenience, not trust, and it is a thinner thing to build on than the company thinks it is.',
        },
        'Nothing in this lane produces a complaint. It produces one transfer that took a different road and, a month later, a forecast that quietly misses.',
      ],
    },
    {
      name: 'Campus meme page admin',
      role: 'Student running a meme page',
      segment: 'students',
      responses: [
        'He is not angry at the wallet. The limit joke was the funniest thing available that week, and it carried the rumour much further than a complaint could have.',
        {
          when: ['true', 'accurate', 'check', 'verify', 'fact', 'real'],
          text: 'He never checked whether the circular existed. A joke does not have to be true to work, it only has to be recognisable, and everybody recognised the fear of a limit.',
        },
        {
          when: ['affect', 'own', 'money', 'balance', 'personal'],
          text: 'There is twelve hundred taka in his account and no reason to move it. The loudest voice in this run had nothing at stake in it.',
        },
        {
          when: ['stop', 'respond', 'brand', 'correct', 'reply', 'company'],
          text: 'A correction posted at him would have become a second joke by the evening. Something accurate and genuinely funny given to him first would have travelled further than either.',
        },
        'By round thirty he had moved on to something else entirely. The agent point was still dry.',
      ],
    },
    {
      name: 'Agent point operator',
      role: 'Cash point beside the bus stand',
      segment: 'retailers',
      responses: [
        'He ran out of cash by eleven and still cannot say what happened. No customer complained, they simply kept arriving, and there is nothing to pass upward except an empty drawer.',
        {
          when: ['ask', 'question', 'customer', 'explain', 'answer', 'say'],
          text: 'People ask him whether the limit is real, twenty times a morning, and he tells them what the last customer told him. Nobody has ever sent him the correct sentence.',
        },
        {
          when: ['report', 'upward', 'tell', 'distributor', 'company', 'data'],
          text: 'The distributor asks how much cash he needs and never asks why. There is no line on the form for a reason, so the earliest warning in this whole run stops at the drawer.',
        },
        {
          when: ['deposit', 'cash in', 'return', 'recover', 'back'],
          text: 'The number that matters is not the withdrawals, it is the deposits. He has taken almost nothing in for three weeks. Withdrawals came back by themselves and that side has not.',
        },
        'He is the only person in this scenario the households will believe, and the last person anybody thought to inform.',
      ],
    },
    {
      name: 'Transfer receiving household head',
      role: 'Woman receiving the monthly transfer',
      segment: 'women',
      responses: [
        'She took the whole balance out the same afternoon and told nobody. It was not a protest, it was arithmetic: the charge is small and losing the transfer is not.',
        {
          when: ['believe', 'true', 'sure', 'trust', 'doubt', 'real'],
          text: 'She does not think the circular was true. She also did not need it to be true, because being wrong about it costs a charge and being right about it costs the month.',
        },
        {
          when: ['post', 'complain', 'call', 'helpline', 'speak', 'report'],
          text: 'There is nothing to complain about. A complaint needs somebody to have done something to you, and nobody did anything. The money came out exactly as it should have.',
        },
        {
          when: ['keep', 'home', 'tin', 'store', 'cash', 'safe'],
          text: 'The cash is folded into the rice tin at home the way money was kept before any of this existed. It is not safer there and she knows it is not safer there.',
        },
        'She will put money back in when a transfer is too large to carry, and not before. Nobody at the company will ever learn that this decision was made.',
      ],
    },
    {
      name: 'Para committee secretary',
      role: 'Committee elder who forwards what people should know',
      segment: 'elderly',
      responses: [
        'He forwarded it as caution rather than as fact, and that is exactly why it worked. A warning from somebody known is much harder to withdraw than an accusation.',
        {
          when: ['verify', 'check', 'source', 'who wrote', 'true', 'proof'],
          text: 'He wrote in the message that he could not verify it. Everybody read that line and forwarded it anyway, because the caveat is what made it safe to pass on.',
        },
        {
          when: ['correct', 'denial', 'retract', 'fix', 'company', 'respond'],
          text: 'No one from the company has ever been in that group, before or since. A correction from a name the committee recognises would have moved the same evening.',
        },
        {
          when: ['old', 'before', 'previous', 'remember', 'history', 'again'],
          text: 'He remembers the year the savings cooperative shut and the people who waited lost everything. That memory is why a screenshot can empty an upazila in one morning.',
        },
        'He carries more weight in this run than every page in it combined, and no institution has ever asked him what he is telling people.',
      ],
    },
  ],
}
