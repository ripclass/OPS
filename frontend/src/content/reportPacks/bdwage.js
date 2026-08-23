// Report and interview content for the bdwage scenario pack.
// A wage board announcement landing in Eid bonus season at Shubarna Apparels,
// Gazipur. Union body: Poshak Sromik Oikko. Employer body: Poshak Malik Forum.
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

export const BDWAGE_REPORT = {
  reportSections: [
    {
      title: 'Phase by phase: what the cascade actually did',
      paragraphs: [
        'The run covers forty rounds. The floor knows what it thinks by round five and the factory does not receive any version of it until round thirty-nine, when it arrives as an empty overtime list rather than as a sentence. That distance is what this report exists to describe.',
        '**Rounds 1 to 8. The announcement, and the silence that answers it.** At round two the wage board announces a new minimum as a monthly figure. Nobody on the floor is confused about the number. What they immediately want to know is what it does to the Eid bonus, which is calculated on the old one. At round five that question is not asked out loud, because the supervisor is standing two metres away and the supervisor writes the attendance and the overtime list. Silence on the line is not confusion and it is not consent. It is a safety behaviour, and it is the first data point in the run.',
        '**Rounds 9 to 18. Two statements, neither of them an answer.** At round nine Poshak Sromik Oikko says publicly that the new board cannot be used to cut the Eid bonus and demands written assurance factory by factory. At round twelve the real conversation happens at the teashop at ten at night: who gets how much, who gets nothing, what people are telling their families. No supervisor is present and no record is made. At round sixteen the Poshak Malik Forum tells a business page that the new structure will be implemented in full and on time, a sentence about compliance addressed to buyers, which answers nothing anybody on the floor asked.',
        '**Rounds 19 to 30. The squeeze and the arithmetic.** At round twenty Shafiq is asked for a figure by sixty operators and for a target by production and holds authority over neither, and he passes nothing upward, because passing it up reads as failing to manage the line. At round twenty-four a labour rights page posts a worked example showing the bonus falling short. It is shared thousands of times, mostly by people who have never stood on a line, and its real function is to give the floor language for a sum the floor finished a fortnight ago. At round twenty-nine Monowara tells the village nothing, because a wrong figure said out loud at home is worse than no figure at all.',
        '**Rounds 31 to 40. The notice and the quiet withdrawal.** At round thirty-four HR posts a Bangla notice on the board beside the gate. It is read by workers walking out at the end of a shift and rewritten five times before it reaches the mess. At round thirty-nine nobody calls anything a protest and nobody stops a machine. People simply stop staying for overtime, one shift at a time, and go home. The factory records this as a scheduling problem. It is the answer.',
      ],
    },
    {
      title: 'Segment by segment: who moved, and in which direction',
      paragraphs: [
        '### Sewing floor operators',
        'The largest lane and the most disciplined. Eleven years on the same machine teaches you exactly what can and cannot be said within earshot of the person who allocates overtime. This lane reaches a settled, detailed, entirely accurate view of the bonus problem by round five and transmits none of it inside the building. Its response is not speech, it is attendance: which shifts get taken, which get declined, and how fast the line empties at seven.',
        '### Women on the sewing floor and in the helper section',
        'The lane with the least room to speak and the most exposed household arithmetic. The bonus is not discretionary money here, it is the Eid transfer, the debt payment and the school fee already committed against a number nobody has confirmed. In this run the characteristic behaviour is holding the news back from the family: no figure goes home until the envelope is in hand, because a wrong number spoken in the village is harder to take back than silence.',
        '### Line supervisors',
        'The pressure joint of the whole scenario. Shafiq is held responsible for a figure he did not set and a target he cannot move, is asked about both from opposite directions, and has no authority over either. He absorbs pressure from above and below and transmits almost nothing in either direction, because escalating reads as an admission that he cannot manage sixty people. If any lane in this run could have carried an accurate message quickly, it was this one, and it was given nothing to carry.',
        '### Mess canteens and tea stalls',
        'The trade lane, and the best-informed institution in the scenario. There is no consumer retail here in the ordinary sense; the counter that matters is the one that feeds four hundred people at ten at night. It hears every figure, every rumour about what the factory across the road paid, and every plan to refuse overtime, a full week before HR does. It reports none of it to anyone, because the canteen owner has to serve those workers tomorrow and that supervisor as well.',
        '### Village households waiting for the bonus',
        'Downstream, unconsulted, and budgeting around a number that does not exist yet. Eid spending in the village is committed weeks before the money moves, on the strength of an expectation. When the transfer lands short, the adjustment happens four hundred kilometres from any lane in this run, and it never travels back as a complaint, only as a smaller Eid.',
        '### The union lane and the labour rights pages',
        'Highest visibility, and split in two. Poshak Sromik Oikko is believed on the floor because it is asking the actual question, in Bangla, about the bonus. The rights page carries far more reach and far less standing: it supplies arithmetic and vocabulary to an audience that mostly does not work in garments. Together they make the issue legible to the outside world without moving one figure inside Shubarna Apparels.',
        '### The owners forum and the HR compliance desk',
        'Speaking accurately to the wrong room. The Poshak Malik Forum answers buyers and regulators about implementation, which is the question its audience asks. HR answers the floor with a gate notice, which is a document posted where people are leaving rather than a sentence delivered where people are working. Both are honest. Neither is an answer, and the gap between them and the floor is filled by whoever rewrote the notice on the way to the mess.',
      ],
    },
    {
      title: 'THE SILENCE LANE: the factory floor, where the person who writes the overtime list is standing two metres away',
      paragraphs: [
        'This is the finding. Everything else in this report is context for it.',
        'The lane with the strongest view in this entire run is the lane that produces no text at all. Sixty operators on a line have worked out, correctly and within hours, what the new board does to the Eid envelope. Not one of them says it at the machine. This is routinely read upstairs as calm, and it is the exact opposite: silence on a garment floor is a measurement of how much authority the listener has, not of how much agreement there is. The quieter the line, the more precisely the workers understand who is standing in it.',
        '**What the silence is made of.** Three things. First, proximity to power: the supervisor two metres away writes the attendance register and allocates overtime, so a sentence said at the machine has a price attached and the price is paid privately, next month, in hours not offered. Second, the absence of any channel that is not him: there is no route from an operator to HR that does not pass through the person the complaint is about, and everybody on the floor can name a person for whom that route went badly. Third, timing: this is bonus season, the envelope is four weeks away, and nobody risks the envelope four weeks before it arrives.',
        '**Where it is nevertheless visible.** The lane leaves four traces and not one of them is in a listening tool. Overtime acceptance, which falls before anything else moves and is recorded as a rostering issue. Attendance on the days after payday. Mess canteen volume at ten at night, which is where the sentence actually gets said and where the canteen owner hears the plan a week early. And what the village is told, or rather is not told, because a worker who stops naming a figure on the weekly phone call has already concluded the figure will disappoint.',
        '**The sentence that matters, and where it goes.** At the teashop at ten at night the floor is precise, specific, unhesitating and completely correct about its own arithmetic. That conversation has no supervisor in it, no record, and no return path into the building. What the factory eventually receives is a fifth-hand version, a week later, if at all, usually through a rumour about another factory. Management therefore consistently hears the least accurate account of its own workforce, and hears it last.',
        '**Why it outlasts the visible conversation.** The rights page moves on after round twenty-four and the news pages after the notice. Nothing about that decay changes an overtime decision. A worker who stopped staying late in bonus season is still leaving at seven in the second month, because the reason was never the announcement, it was what the announcement revealed about who would decide. Read the quiet as resolved and you will schedule a production plan against hours nobody has agreed to work.',
      ],
    },
    {
      title: 'Amplifier profiles: the four actors that decided the reach',
      paragraphs: [
        '### Poshak Sromik Oikko, the union voice',
        'Low volume, high standing, narrow ask. Its statement at round nine is the only public sentence in the run that names the actual question, the Eid bonus, and asks for the only thing that would settle it, written assurance factory by factory. It is believed on the floor because it is asking what the floor is asking. Its weakness is enforcement: it can put the question into the air and cannot put a figure into an envelope. Treat it as the clearest available statement of the requirement, not as an opponent to be managed.',
        '### The labour rights page',
        'Highest reach, lowest presence. The worked example at round twenty-four is shared thousands of times, overwhelmingly by people who have never worked a line, and its accuracy is the reason it travels. Its real effect inside the factory is linguistic: it hands the floor a public vocabulary for a private calculation, which makes the grievance quotable at the exact moment it becomes usable. Arguing with the arithmetic in public is the worst available move, because the arithmetic is right.',
        '### The teashop table and the mess network',
        'No account, no admin, no reach in any measurable sense, and the highest-fidelity channel in the run. It carries the truthful version of what every worker thinks, nightly, at ten, to an audience of exactly the people who matter, and it carries it in both directions between buildings. Nothing said here is aimed at the company and nothing said here reaches it. Any organisation that wants to know what its floor thinks has to be present at that hour or accept that it will never know.',
        '### The Poshak Malik Forum',
        'Highest institutional weight, aimed entirely outside. Its press line at round sixteen is about implementation in full and on time, which is precisely what buyers and regulators need to hear and precisely not what sixty operators asked. Its motivation is order book protection, which is legitimate and which makes it structurally incapable of answering the envelope question in public. The response should stop expecting it to, and put that answer somewhere else.',
      ],
    },
    {
      title: 'Trust map: who is believed, by whom, about what',
      paragraphs: [
        'Trust in this run is not a number about management. It is a map of who is believed about which kind of claim, and no single actor holds more than one layer of it.',
        '**About what the envelope will actually contain, nobody is believed, including the union.** This is the only question the floor is asking and no lane in the run answers it. In the absence of an answer the floor believes the most pessimistic figure in circulation, which usually arrives from another factory by way of the mess.',
        '**About what other factories are paying, the mess and the teashop are believed absolutely.** What the factory across the road paid last Eid is treated as fact, because somebody at the table worked there. This channel is faster and more accurate than anything the company operates, and it is invisible to it.',
        '**About intent, the union is believed and the owners forum is not so much disbelieved as considered irrelevant.** Poshak Sromik Oikko is asking the right question, so it is trusted. The Poshak Malik Forum is answering a compliance question honestly to an audience of buyers, so on the floor it does not register as an answer at all.',
        '**About the supervisor, everyone is accurate and nobody says so.** Both the floor and production know Shafiq controls neither the figure nor the target. The floor still directs the question at him because he is the only management surface it can reach, and production still holds him responsible because he is the only management surface it can reach either.',
        '**About the gate notice, the document is trusted and its journey is not.** A Bangla notice posted at the gate is read by people walking out and rewritten five times before it reaches the mess. By the time it arrives it is no longer the notice, it is what someone remembers of it.',
        'The practical reading: this is not a credibility problem, it is a delivery problem. The company has one accurate sentence to say and it keeps saying it in the two places the floor does not read.',
      ],
    },
    {
      title: 'What your dashboard will show, and why it is wrong',
      paragraphs: [
        'Through the whole of this run the operational dashboard at Shubarna Apparels stays clean, and every number on it is true.',
        '- **No stoppage, no gate incident, no grievance filed.** The formal grievance channel records nothing all month. It records nothing because it runs through the supervisor, and the supervisor is the reason for the silence in the first place.',
        '- **Attendance holds and output holds.** People come in, hit the target, and leave at seven. The refusal in this run is invisible to attendance because it lives entirely in the hours after the shift, which are voluntary and therefore not measured as sentiment by anyone.',
        '- **Social listening shows a spike among people who do not work here.** The rights page arithmetic drives the visible volume at round twenty-four. It is real reach, and almost none of it belongs to anybody on the floor, so the sentiment curve describes an audience rather than a workforce.',
        'One number to hold onto: overtime acceptance turns at round thirty-nine while the count of formal grievances for the same period is zero. The one lane that moved is the one lane nobody classified as communication.',
      ],
    },
    {
      title: 'Recommendations',
      paragraphs: [
        '**1. Answer the envelope question, in taka, on paper, in Bangla.** Everything in this run follows from a single unanswered question: what the Eid bonus will be under the new board. One worked example on the payslip, with the calculation shown, settles more than every statement issued by either body. If the answer is bad, saying it early costs less than letting the mess supply a worse one.',
        '**2. Instrument overtime acceptance as your earliest sentiment metric.** It is already recorded, it costs nothing to read differently, and in this run it moves while the grievance count is zero. A daily line showing offered hours against accepted hours per line is the closest thing this factory has to a listening tool.',
        '**3. Ask the question somewhere the supervisor is not.** No channel that runs through the line supervisor will ever return anything useful, because he is the risk. A written box, a phone line, or a session run by someone with no role in scheduling gives the floor its first non-lethal route, and even a low response rate is infinitely more than zero.',
        '**4. Deliver the notice where people are working, not where they are leaving.** A board at the gate is read on the way out and rewritten five times before the mess. Read the same text aloud at the start of a shift, on the floor, and hand out a copy small enough to put in a pocket and photograph.',
        '**5. Give supervisors a number and the authority to say it.** Shafiq is the highest-bandwidth channel in the building and he is currently carrying nothing. Brief line supervisors first, with the figure and the arithmetic, before the notice goes on any board, and let them answer instead of deflecting.',
        '**6. Write a line the worker can send home.** The village is budgeting on a guess, and the worker will not name a figure until the envelope is in hand. A single forwardable Bangla sentence confirming when the bonus is paid and how it is calculated moves the pressure off the phone call and out of the household, at a cost of nothing.',
      ],
    },
  ],

  reportAgentAnswers: {
    first: 'The earliest signal is not a complaint, it is silence. At round five the line goes quiet with the supervisor standing two metres away, which is a safety behaviour rather than agreement. The same evening at the teashop the same people are precise, specific and entirely correct about what the new board does to the Eid envelope.',
    spread: 'It spreads through the mess and the building network, not through the factory and not through the pages. A rights page posting worked arithmetic at round twenty-four gives the floor a public vocabulary for a sum it finished a fortnight earlier, and the fastest route between two factories in Gazipur is a canteen at ten at night.',
    trust: 'Trust splits by question. About the envelope nobody is believed, including the union, because no lane in the run answers it. About what other factories paid, the mess is believed absolutely. About intent, Poshak Sromik Oikko is trusted because it is asking the right question, and the Poshak Malik Forum is not so much disbelieved as considered irrelevant, because it answered a compliance question addressed to buyers.',
    quiet: 'The silence lane is the factory floor itself. Sixty operators know exactly what they think by round five and none of it is said inside the building, because the person who writes the attendance and the overtime list is standing two metres away. The sentence that matters is said at the teashop at ten at night, with no supervisor in the room and no route back into the factory, so management hears the least accurate version of its own workforce and hears it last.',
    retail: 'There is no consumer counter in this run. The trade lane is the mess canteens and tea stalls, and they are the best-informed institution in the scenario: they hear every figure, every rumour about what the factory across the road paid, and every plan to refuse overtime, a week before HR does. They report none of it, because the canteen has to serve those workers tomorrow and that supervisor as well.',
    women: 'Women on the sewing floor and in the helper section carry the most committed household arithmetic and the least room to speak. The bonus is already spent on paper: the Eid transfer, a debt payment, a school fee, all set against a figure nobody has confirmed. The characteristic behaviour in this run is telling the village nothing, because a wrong number said out loud at home is harder to take back than silence.',
    young: 'The labour rights page carries the reach and none of the exposure. Its worked example at round twenty-four is accurate, which is why it travels, and it is shared overwhelmingly by people who have never stood on a line. Its real effect inside the factory is linguistic, and arguing with the arithmetic in public is the worst move available, because the arithmetic is right.',
    timeline: 'Four phases across forty rounds. Rounds one to eight are the announcement and the silence that answers it. Rounds nine to eighteen are two public statements, from Poshak Sromik Oikko and the Poshak Malik Forum, neither of which answers the bonus question, while the teashop settles it privately at round twelve. Rounds nineteen to thirty are the supervisor squeeze and the rights page arithmetic. Rounds thirty-one to forty are the gate notice and the quiet withdrawal from overtime at round thirty-nine.',
    compare: 'Compare the lane with the reach and the lane with the exposure. The rights page produced thousands of shares from people with nothing at stake. The floor produced no text at all and changed the only thing it controls, which is whether it stays after seven. Everything measurable in this run belongs to the first group and everything consequential belongs to the second.',
    worst: 'The biggest risk is reading floor silence as acceptance and scheduling against it. No stoppage, no grievance and full attendance all read as calm, while overtime acceptance is already turning. Build the Eid production plan on hours nobody has agreed to work and the shortfall arrives in the last week, when there is no way left to recover it.',
    recover: 'Recovery runs through the payslip and the line supervisor, not through a notice or a press line. Show the bonus arithmetic in taka on the payslip, and brief supervisors with the figure before anything goes on a board, so the person the question is actually asked can answer it. A gate notice is rewritten five times before it reaches the mess, and what arrives is not the notice but what somebody remembers of it.',
    recommend: 'Six things. Answer the envelope question in taka on the payslip, with the calculation shown. Read overtime acceptance daily as your earliest sentiment metric, because it moves while the grievance count is zero. Open one route to the floor that does not run through the supervisor. Deliver the notice at the start of a shift rather than at the gate on the way out. Brief line supervisors with the figure and the authority to state it. And write one forwardable Bangla sentence the worker can send home to a village that is budgeting on a guess.',
  },

  interviewAgents: [
    {
      name: 'Village household head',
      role: 'Family waiting for the Eid bonus',
      segment: 'rural',
      responses: [
        'He is budgeting Eid around a figure nobody has confirmed, and he will find out what it was when the money either arrives or does not.',
        {
          when: ['told', 'call', 'phone', 'know', 'figure', 'how much'],
          text: 'On the weekly call the amount stopped being mentioned about three weeks ago. Nobody said anything was wrong. The number simply left the conversation, and that is how the household knew.',
        },
        {
          when: ['spend', 'plan', 'eid', 'debt', 'shop', 'buy'],
          text: 'The shopping is already committed. Cloth is taken on account at the bazaar in the expectation of the bonus, so a short envelope in Gazipur becomes a shopkeeper in the village carrying a debt he did not agree to.',
        },
        {
          when: ['union', 'news', 'page', 'hear', 'announcement'],
          text: 'The wage board announcement reached here as good news and nothing since has corrected it. The village is four hundred kilometres from the teashop where the real figure is known.',
        },
        'Nobody in this household will ever complain to anyone. The adjustment happens quietly, at Eid, and no lane in this run records that it happened.',
      ],
    },
    {
      name: 'Sewing machine operator',
      role: 'Eleven years on the same floor',
      segment: 'urban_working',
      responses: [
        'She said nothing on the line, because the supervisor stands two metres away and writes the overtime list. The full sentence came out at the teashop at ten that night.',
        {
          when: ['speak', 'say', 'silent', 'quiet', 'afraid', 'why not'],
          text: 'Nothing happens to you the day you speak. It happens next month, in hours you are not offered, and nobody can prove that is what it was.',
        },
        {
          when: ['overtime', 'hours', 'stay', 'late', 'refuse', 'protest'],
          text: 'Nobody is calling it anything. People are simply going home at seven. It is the only reply available that cannot be written up as an incident.',
        },
        {
          when: ['bonus', 'envelope', 'figure', 'how much', 'calculate'],
          text: 'The floor did the sum in an afternoon. Everyone knows what the new board does to a bonus calculated on the old one. What nobody knows is what the envelope will actually hold, and that is the only question being asked.',
        },
        'Eleven years teaches you exactly what can be said and where. The quietest line in the building is the one that understands its supervisor best.',
      ],
    },
    {
      name: 'Line supervisor',
      role: 'Answers to production and to sixty operators',
      segment: 'middle_class',
      responses: [
        'He is asked for a figure by sixty operators and for a target by production, and he sets neither. What he passes upward is nothing, because passing it up reads as failing to manage the line.',
        {
          when: ['upward', 'report', 'hr', 'management', 'escalate', 'tell'],
          text: 'Reporting that the line is unhappy is heard upstairs as an admission that he cannot handle sixty people. So the most reliable channel in the building carries nothing in either direction.',
        },
        {
          when: ['answer', 'ask', 'question', 'operator', 'floor'],
          text: 'They ask him because he is the only piece of management they can reach. He answers with what he has, which is a target and no figure, and both sides know it is not an answer.',
        },
        {
          when: ['notice', 'gate', 'hr', 'document', 'brief'],
          text: 'He read the gate notice at the same time as the workers did, walking out. Nobody briefed him first, and he is the person they will ask about it in the morning.',
        },
        'Give him the number and the permission to say it and he becomes the fastest channel in the factory. He is currently the most loaded and the emptiest.',
      ],
    },
    {
      name: 'Owners forum representative',
      role: 'Speaks for a group of factories',
      segment: 'corporate',
      responses: [
        'He answered the question the buyers asked about compliance, which was the wrong question, and he will not learn that until the overtime lists come in short.',
        {
          when: ['buyer', 'brand', 'order', 'compliance', 'audit', 'export'],
          text: 'The order book is the thing he is actually protecting, and implementation in full and on time is the sentence that protects it. It is true, it is necessary, and it has never once been read by a worker.',
        },
        {
          when: ['floor', 'worker', 'hear', 'reach', 'answer'],
          text: 'Nothing the forum says is built to reach a sewing floor. It is a press line, and the floor asked about an envelope. Those two things are not in contact at any point in this run.',
        },
        {
          when: ['data', 'metric', 'dashboard', 'measure', 'grievance', 'number'],
          text: 'No stoppage, no gate incident, no grievance filed all month. He reads that as a month handled. The grievance channel runs through the supervisor, so it was never going to record anything.',
        },
        'He will find out at the end of bonus season, from a production shortfall, and it will be filed as a rostering problem.',
      ],
    },
    {
      name: 'Migrant worker in factory housing',
      role: 'First season in Gazipur, family in the north',
      segment: 'migration_workers',
      responses: [
        'He came for the bonus month specifically. Everything about this job was priced on what Eid pays, and that figure is now the one thing nobody will confirm.',
        {
          when: ['home', 'village', 'send', 'family', 'money', 'remit'],
          text: 'He has stopped naming an amount when he calls home. The plan was to send the bonus in one go, and now he would rather send nothing than send a number he has to correct later.',
        },
        {
          when: ['stay', 'leave', 'quit', 'another factory', 'move', 'job'],
          text: 'Two people in the room have already said they will go to the factory across the road after Eid. Nobody resigns in bonus season, they resign the week after, and the exit interview will say personal reasons.',
        },
        {
          when: ['mess', 'room', 'talk', 'teashop', 'night'],
          text: 'The room is where the figures get compared. Eight men, four factories, and by ten at night everybody knows what every one of those four is paying. Nothing about that reaches any of the four.',
        },
        'He has no history in this town and no union contact, so he is the least protected person on the floor and the least likely to say anything at all.',
      ],
    },
    {
      name: 'Labour rights page admin',
      role: 'Runs a rights page with national reach',
      segment: 'students',
      responses: [
        'He posted the worked arithmetic and gave the floor language for a sum it had already finished. The reach came from people who have never stood on a line.',
        {
          when: ['accurate', 'true', 'check', 'verify', 'source', 'fact'],
          text: 'The arithmetic is correct and he can show the working. That is exactly why it travelled, and it is why arguing with it in public would be the worst move the employer could make.',
        },
        {
          when: ['worker', 'floor', 'reach', 'audience', 'who'],
          text: 'Most of the sharing is students and office staff. Workers read it and forward almost none of it, because the account you forward from is the account somebody at work can see.',
        },
        {
          when: ['union', 'oikko', 'together', 'coordinate', 'link'],
          text: 'Poshak Sromik Oikko is asking for written assurance factory by factory and he is supplying the sum that makes the ask legible. Neither of them can put a taka in an envelope.',
        },
        'By round thirty he is on to another factory. Overtime at this one is still being declined every evening.',
      ],
    },
    {
      name: 'Mess canteen owner',
      role: 'Feeds four hundred workers at ten at night',
      segment: 'retailers',
      responses: [
        'He hears everything at ten at night and repeats none of it to anyone from the factory. The canteen knows a week before HR does.',
        {
          when: ['tell', 'report', 'hr', 'management', 'why not', 'pass'],
          text: 'He has to serve those workers tomorrow and that supervisor as well. Repeating anything in either direction costs him half the room, so he keeps the best information in Gazipur to himself.',
        },
        {
          when: ['hear', 'talk', 'night', 'figure', 'other factory'],
          text: 'Four factories eat here. By the end of the week he can tell you what each one is paying and who is lying about it, because somebody at every table worked at one of the others.',
        },
        {
          when: ['credit', 'bill', 'money', 'spend', 'sale', 'bakite'],
          text: 'The clearest sign is not the talk, it is the account book. More people eating on credit and smaller plates, three weeks before Eid, which is the wrong direction for this month.',
        },
        'Nobody from any factory has ever asked him a single question, which is remarkable given that he is the only person in this town who hears all of it.',
      ],
    },
    {
      name: 'Helper section worker',
      role: 'Sends the bonus home to Kurigram',
      segment: 'women',
      responses: [
        'She has not told the family what the bonus will be, because she does not know, and a wrong number said out loud in the village is worse than no number at all.',
        {
          when: ['spend', 'plan', 'debt', 'school', 'commit', 'budget'],
          text: 'The money is already spent on paper. A debt payment, the school fee, and the Eid transfer, all committed against a figure nobody has confirmed to anyone.',
        },
        {
          when: ['speak', 'say', 'silent', 'quiet', 'floor', 'supervisor'],
          text: 'The helper section is the last place in the building where anybody would risk a sentence. Everything above it can be replaced slowly and this can be replaced in a morning.',
        },
        {
          when: ['union', 'oikko', 'rights', 'page', 'help'],
          text: 'The union statement was read out in the mess by somebody who had it on a phone. Nobody in the room has ever spoken to anyone from it and nobody would, in bonus season.',
        },
        'When the envelope comes she will know in one second what the whole month of statements did not tell anybody, and then it will be too late to plan anything differently.',
      ],
    },
    {
      name: 'Mess building caretaker',
      role: 'Retired operator, now keeps the worker quarters',
      segment: 'elderly',
      responses: [
        'He has seen four wage boards from the inside of this town, and he can tell you the shape of this one before it finishes.',
        {
          when: ['before', 'previous', 'history', 'remember', 'last time', 'again'],
          text: 'Every board arrives as a monthly figure and every dispute afterwards is about how the bonus is calculated. That is not a coincidence, it is the same gap left open the same way each time.',
        },
        {
          when: ['calm', 'settle', 'anger', 'protest', 'stoppage'],
          text: 'Nothing will stop. That was the old response and it cost people their jobs. What happens now is quieter and slower and there is no way for management to answer it, because there is nothing to answer.',
        },
        {
          when: ['rent', 'room', 'building', 'leave', 'move'],
          text: 'Two rooms have asked to pay rent late this month, before the bonus is even due. He gives everybody a fortnight because he knows what the fortnight is for.',
        },
        'The building knows the state of the floor better than the floor manager does, and nobody has ever come down here to ask.',
      ],
    },
  ],
}
