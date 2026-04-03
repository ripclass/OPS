"""
OPS-native population generation service.
"""

import concurrent.futures
import json
import math
import random
import re
import unicodedata
from typing import Any, Dict, List, Optional

from openai import OpenAI

from ..config import Config
from ..utils.logger import get_logger
from .oasis_profile_generator import OasisAgentProfile, OasisProfileGenerator
from .zep_entity_reader import EntityNode

logger = get_logger("ops.population")


SEGMENT_ALIASES = {
    "rural": "rural",
    "urban working class": "urban_working",
    "urban_working": "urban_working",
    "urban-working": "urban_working",
    "middle class": "middle_class",
    "middle_class": "middle_class",
    "middle-class": "middle_class",
    "corporate": "corporate",
    "migration workers": "migration_workers",
    "migration worker": "migration_workers",
    "migration_workers": "migration_workers",
    "migration-workers": "migration_workers",
    "students": "students",
    "student": "students",
    "women": "women",
    "woman": "women",
    "elderly": "elderly",
    "elder": "elderly",
}

RUN_TYPE_ALIASES = {
    "domestic": "Domestic",
    "diaspora": "Diaspora",
    "corridor-based": "Corridor-based",
    "corridor_based": "Corridor-based",
    "regional multi-country": "Regional multi-country",
    "regional_multi_country": "Regional multi-country",
    "regional-multi-country": "Regional multi-country",
}

COUNTRY_ALIASES = {
    "bangladesh": "Bangladesh",
    "india": "India",
    "pakistan": "Pakistan",
    "nepal": "Nepal",
    "sri lanka": "Sri Lanka",
    "srilanka": "Sri Lanka",
    "sri_lanka": "Sri Lanka",
}

GENERIC_SEGMENT_RULES = {
    "rural": "Rural agents should reflect higher food and transport vulnerability, tighter community visibility, and stronger shame pressure.",
    "urban_working": "Urban working-class agents should show wage, rent, or utility pressure and dense peer influence.",
    "middle_class": "Middle-class agents should balance cost anxiety, family status, and long-term stability.",
    "corporate": "Corporate agents should feel more polished, professionally cautious, and income-stable.",
    "migration_workers": "Migration workers should show remittance obligations, family separation, and job-security anxiety.",
    "students": "Students should have high platform intensity, faster peer amplification, and more rumor exposure.",
    "women": "Women-specific agents should reflect gendered safety, household, and reputation pressures.",
    "elderly": "Elderly agents should show lower posting intensity, stronger memory of past shocks, and slower but durable opinion change.",
}

COUNTRY_SETTINGS: Dict[str, Dict[str, Any]] = {
    "Bangladesh": {
        "segment_weights": {
            "rural": 0.35,
            "urban_working": 0.24,
            "middle_class": 0.15,
            "corporate": 0.05,
            "migration_workers": 0.09,
            "students": 0.07,
            "women": 0.03,
            "elderly": 0.02,
        },
        "regions": {
            "dhaka": "Dhaka (22+ million metro): garments hub (Gazipur/Savar/Ashulia), NGO HQ city (BRAC/Grameen), corporate sector, highest income disparity. Mirpur/Mohammadpur = working-class garments neighborhoods. Gulshan/Banani = elite corporate/diplomatic zone. Old Dhaka = conservative trading families. Slums (Korail/Bauniabandh) = climate migrants doing anything for survival. Garment workers here are MIGRANTS from rural districts, not local.",
            "chittagong": "Chittagong: port city, second-largest economy, strong Chatgaayan cultural identity and dialect (not mutually intelligible with Dhaka Bangla). Conservative Muslim majority. Trading tradition. Ship-breaking at Sitakunda (dangerous male-dominated work). EPZ garment factories — but workers are MIGRANTS from Noakhali/Comilla/Feni, NOT local Chatgaayan women. For local women, garments = serious stigma. Acceptable female work: teaching, nursing, NGO, banking, beauty parlor. Hindu minority in old Chittagong — jewelers, shopkeepers.",
            "sylhet": "Sylhet: UK diaspora capital, highest remittance dependency region. Sylheti dialect (closest to Assamese, barely intelligible to Dhaka). Conservative Muslim majority, strong pir/Sufi culture. Remittance families expect women NOT to work — working = shame. Tea gardens employ Adivasi (indigenous/tribal) women. primary_fear for women: husband stops sending money from London, remarries abroad.",
            "rajshahi": "Rajshahi: silk industry, Chapainawabganj mangoes, education hub (Rajshahi University). Hindu minority largest outside Dhaka. Border with India (shares culture with Malda, West Bengal). Historically leftist/secular political tradition. Barind Tract is drought-prone (unlike flood-prone rest of BD). Silk weaving employs women home-based. More moderate gender norms than Sylhet/Chittagong.",
            "barisal": "Barisal/Khulna coastal south: Sundarbans gateway, shrimp farming, extreme climate vulnerability — cyclones (Aila 2009, Amphan 2020), salinity intrusion, river erosion. Hindu fishing communities. Migration SOURCE zone — people LEAVE here. Women work shrimp peeling, fish drying, crab collecting out of necessity — lower stigma. Men go to Gulf or Dhaka.",
            "khulna": "Khulna: industrial pressure, shrimp economy (destroyed rice agriculture through salinization), ship-breaking, climate displacement hub. Women in shrimp peeling, fish processing. Significant climate-driven out-migration to Dhaka/Gazipur.",
            "rangpur": "Rangpur/Kurigram/Dinajpur (north): historically monga (seasonal famine) poverty belt. Char lands of Jamuna/Teesta — extreme flood/erosion. Day laborers. Lowest development indicators. Adivasi Santal community. Women do agricultural day labor, tobacco processing, brick kiln seasonal migration. Children work from age 8-10. Early marriage highest in country.",
            "comilla": "Comilla/Noakhali/Feni: densely populated, strong madrasa belt, high Middle East migration. Conservative at home but paradoxically top source region for female RMG workers — poverty forces migration to Dhaka garments. Island communities (Hatiya, Sandwip) climate-vulnerable.",
            "mixed": "A mixed Bangladesh sample across Dhaka, Chittagong, Sylhet, Rajshahi, Barisal, Khulna, Rangpur, and Comilla — reflecting 84% informal employment, post-July 2024 political upheaval, and declining female labor force participation.",
        },
        "dialects": "Use only Bangladesh-relevant varieties: standard Dhaka Bangla, Sylheti (almost a separate language), Chatgaayan (distinct from Dhaka), Noakhali-influenced Bangla, Barishal speech, Rangpur dialect, or English-Bangla mix for educated urban professionals. Garment workers from Comilla/Noakhali speak differently from Chittagong locals.",
        "country_rules": [
            "84% of employment is INFORMAL. Most agents should have informal, precarious, or self-employed work. Only corporate and some middle_class have formal employment.",
            "Post-July 2024 revolution: trust_government is LOW across ALL segments. Political identity is explosive — agents hide affiliation. Student agents may carry uprising trauma.",
            "Garments workers are 4-5 million people — the single largest formal female employer. But garment work carries stigma in Chittagong, Sylhet, and conservative rural areas.",
            "Female occupation MUST match zone norms: garments normalized in Dhaka slums but stigmatized in Sylhet. Domestic work done by MIGRANTS, never local middle-class women.",
            "Migration-linked households reflect remittance pressure, Gulf labour exposure, family-status obligations, and fraud/exploitation anxiety.",
            "Rural agents should feel food-price shocks, show agricultural or day-wage occupations, and face community reputation pressure.",
            "Climate migration is a MAJOR driver — coastal/northern poor migrate to Dhaka slums, Gazipur garments, or brick kilns.",
            "Inflation above 8%, GDP growth at 3.97% — economic anxiety is universal, not segment-specific.",
        ],
    },
    "India": {
        "segment_weights": {
            "rural": 0.32,
            "urban_working": 0.24,
            "middle_class": 0.17,
            "corporate": 0.08,
            "migration_workers": 0.07,
            "students": 0.07,
            "women": 0.03,
            "elderly": 0.02,
        },
        "regions": {
            "delhi": "Delhi NCR (32+ million metro): national capital, government HQ, corporate (Gurgaon/Noida), most diverse city. MASSIVE migrant labor from UP/Bihar/Jharkhand/Odisha. Domestic workers = largest female migrant occupation. Gurgaon = corporate India. Old Delhi = Muslim artisan/trading. JNU/DU = intellectual activism. Caste: all castes present but Upper-caste/OBC-dominant politics.",
            "mumbai": "Mumbai: financial capital, Bollywood, Dharavi (Asia's largest informal economy — leather, garments, recycling), most economically active city for women. Fish-selling Koli community. Dalit political assertion (Ambedkar's Mahar community). Bhiwandi/Malegaon = Muslim textile hubs. Pune nearby = IT/education hub.",
            "kolkata": "Kolkata: former capital, declining industrial base (jute mills closing), intellectual/literary tradition, 27% Muslim population (second highest), TMC politics (Mamata), post-industrial economy. Bengali identity strong. Murshidabad/Malda = poor Muslim border districts with bidi rolling.",
            "chennai": "Tamil Nadu/Chennai: Dravidian political culture, Self-Respect Movement legacy (anti-Brahmin, rationalist), HIGHEST female labor participation among large states. Women visible in ALL sectors including bus conductors. Tirupur garments. Kanchipuram silk. Sivakasi matchsticks (hazardous). BUT: sumangali system (bonded Dalit girls in textile mills).",
            "bengaluru": "Bangalore/Karnataka: IT capital of India (TCS, Infosys, Wipro, startups), garments hub employing large numbers of young women, significant Dalit population. Silk weaving (Mysore/Ramanagara). Beedi rolling in rural Karnataka. Progressive urban culture coexisting with caste rigidity in rural areas.",
            "hyderabad": "Hyderabad/Telangana: IT hub (Microsoft, Google, Amazon campuses), pharma industry, Nizam legacy, urban Muslim professional class, rural agriculture. Andhra coast: shrimp, tobacco (Guntur). Purdah less strict than North. Pearl trading. Unani medicine tradition.",
            "lucknow": "UP/Bihar heartland: most populous region (240M UP + 130M Bihar), caste MOST rigid, massive out-migration to Delhi/Mumbai/Gujarat, 20% Muslim in UP. Lucknow = Nawabi culture, chikan embroidery. Varanasi = holy city, Banarasi saree weaving (Muslim Ansari weavers). Aligarh = locks. Kanpur = leather (Dalit). Bihar: extreme poverty, remittance-dependent like Bangladesh.",
            "kerala": "Kerala: highest literacy (96.2%), Communist tradition, Gulf remittance economy, nurse export capital, Christians + Hindus + Muslims coexist, matrilineal Nair community. Women MOST educated/empowered. BUT: high local unemployment drives migration. Gulf wives similar to Bangladesh Sylhet pattern.",
            "punjab": "Punjab/Haryana: Green Revolution prosperity, Sikh majority, agricultural mechanization, drug crisis. Haryana: Jat-dominant, extreme patriarchy. Ludhiana: textiles/hosiery. Farm protests legacy (2020-21). Military recruitment dominant. Trucking iconic (Sikh truckers).",
            "rajasthan": "Rajasthan/Gujarat/MP: Rajasthan = feudal Rajput culture, tourism, textiles, MOST restricted women (Rajput ghoonghat, honor killing). Gujarat = business (Jain/Marwari), diamond polishing Surat, dairy (Amul), salt pans (Kutch). MP = large Adivasi population, tendu leaf, NREGA.",
            "northeast": "Northeast India: 8 states, culturally distinct from mainland. Matrilineal Khasi (Meghalaya — women own property, run businesses). Naga/Mizo identity. Assam = tea, Brahmaputra floods. Women MOST economically active in India. Tribal Christian majority in several states.",
            "mixed": "A mixed India sample reflecting 81% informal employment, caste as invisible-but-dominant variable, 12M+ gig workers, 600M+ internal migrants, massive ASHA/Anganwadi female workforce, and enormous regional variation in women's economic participation.",
        },
        "dialects": "Use India-relevant speech: Hindi-English mix (Delhi/UP/Bihar), Bambaiya Hindi (Mumbai), Bengali (Kolkata), Tamil-English mix (Chennai), Kannada-English (Bangalore), Telugu-English (Hyderabad), Hinglish corporate-speak (Gurgaon), Bhojpuri-influenced Hindi (Bihar migrants), Punjabi-Hindi mix, Malayalam (Kerala), or regional colloquial. Match dialect to state/region. IT workers use English-heavy mix.",
        "country_rules": [
            "81% of employment is INFORMAL. 58.4% self-employed. Only corporate and some middle_class have formal salaried work.",
            "Caste shapes occupation more than income/education/geography. Infer caste from name, occupation, location — NEVER state it explicitly.",
            "ASHA workers (1M+) and Anganwadi workers (2.5M+) are a MASSIVE female occupation. They are educated, politically aware, economically precarious despite essential role.",
            "Bidi rolling employs 5+ million workers (majority women — Dalit and Muslim). Major home-based occupation across states.",
            "Domestic work is done by MIGRANT women from poor states (UP, Bihar, Jharkhand, Odisha) to cities. NOT local middle-class women.",
            "A woman's occupation MUST match her state and caste norms: Rajput women in Rajasthan face extreme ghoonghat restrictions. Kerala women are most empowered.",
            "12M+ gig workers (Swiggy, Zomato, Ola, Uber). Muslim riders face documented communal discrimination from customers.",
            "600M+ internal migrants. UP+Bihar = half of all out-migration. COVID trauma still shapes migrant anxiety. Trust in employer/contractor: LOW.",
            "Political identity varies by caste: upper-caste Hindus lean BJP, Muslims very LOW trust in BJP government, Dalits politically aware (Ambedkarite tradition), OBCs variable.",
        ],
    },
    "Pakistan": {
        "segment_weights": {
            "rural": 0.33,
            "urban_working": 0.23,
            "middle_class": 0.16,
            "corporate": 0.06,
            "migration_workers": 0.09,
            "students": 0.07,
            "women": 0.04,
            "elderly": 0.02,
        },
        "regions": {
            "karachi": "Karachi (20+ million): Pakistan's economic engine, most diverse city (Mohajir, Pashtun, Sindhi, Baloch, Punjabi, Bengali). Financial hub. Media hub. Port city. LOWEST restriction on women. Mohajir women most educated/economically active. Pashtun community maintains KP-level restrictions. Industry (SITE, Korangi). Dharavi-equivalent slums alongside corporate towers.",
            "lahore": "Lahore: cultural capital (LUMS, GCU, Punjab University, food, arts, Mughal heritage). Professional women accepted. Textile hub (Faisalabad nearby). Real estate boom (DHA, Bahria Town). IT sector growing (Arfa Karim Technology Park). Class paradox: poor women work, middle-class MOST restricted, elite above judgment. Sialkot (sports goods, surgical instruments) and Gujranwala (cutlery, fans) nearby industrial towns.",
            "islamabad": "Islamabad-Rawalpindi: federal capital + military cantonment. Government and diplomatic zone. CSS officer posting. Army HQ (GHQ Rawalpindi). Most formal discourse. Professional women in government/NGO/corporate. Security state presence palpable. Potohari Punjabi dialect.",
            "peshawar": "KP/Peshawar: Pashtun majority. PTI stronghold. Post-conflict (FATA merger 2018). TTP attacks continue. Afghan refugees (3+ million). MOST restricted women — bazaars male-only, full burqa, women work ONLY as female doctor/teacher/LHW/home-based. Pashtunwali honor code. PTM human rights movement. Conservative Islamic culture.",
            "quetta": "Balochistan/Quetta: tribal sardari system. Mining (coal, copper — hazardous). CPEC/Gwadar. Baloch separatist insurgency. Hazara Shia community under siege (targeted killings). EXTREME women's restriction (tribal honor). Most underdeveloped province. Enforced disappearances.",
            "multan": "South Punjab/Seraiki belt: Multan, Bahawalpur, DG Khan. Feudal. Extreme poverty. Cotton agriculture (women + children pick). Brick kilns (bonded labor — Christian/Hindu families). Sufi shrine culture (Data Darbar). Seraiki language. Very different from Lahore/Islamabad.",
            "interior_sindh": "Interior Sindh: feudal heartland. PPP dynasty. Sindhi language. Sufi shrines. Hindu minority (Tharparkar — some areas Hindu majority). Extreme poverty. 2022 floods devastated this region. Women = property under feudal system. Karo-kari (honor killing). Forced conversion of Hindu/Christian girls.",
            "mixed": "A mixed Pakistan sample reflecting 72.1% informal employment, $38.3B remittances (record), post-2022 political crisis (PTI crackdown, IMF bailout, 35%+ inflation), 77% of women in unpaid care work, massive brain drain, and enormous provincial variation in women's participation.",
        },
        "dialects": "Use Pakistan-relevant: Karachi Urdu (urban, Mohajir — closest to standard), Punjabi-influenced Urdu (Lahore), formal Islamabad Urdu-English mix, Pashto-influenced speech (Peshawar/KP), Seraiki (south Punjab — Multan), Sindhi (interior Sindh), Balochi (Balochistan), Roman Urdu (social media — de facto digital language), English-Urdu corporate code-switching (elite). Match dialect to province and class.",
        "country_rules": [
            "72.1% of non-agricultural employment is informal. 77% of women do unpaid domestic/care work counted as NOT working.",
            "Political crisis since 2022: PTI supporters face arrest/disappearance. Political identity is HIDDEN by most. trust_government: VERY LOW for PTI supporters (majority youth/urban). EVERYONE has an opinion on Imran Khan.",
            "Factory work for women is STIGMATIZED — unlike Bangladesh. Home-based work (stitching, embroidery, food business) is universally acceptable.",
            "A woman's occupation MUST match province/ethnicity: KP = doctor/teacher/LHW only. Karachi Mohajir = professional work normalized. South Punjab/Sindh = feudal control. Balochistan = virtually invisible.",
            "Remittances = $38.3B record. Gulf workers (50%+ to Saudi). UK diaspora (Mirpuri/Kashmiri). Brain drain massive — educated professionals leaving.",
            "Sectarian identity shapes life: Shia face targeted killings. Ahmadis face constitutional persecution (declared non-Muslim, criminalized for Islamic practices). Christians face blasphemy weapon and brick kiln bonded labor. Hindus face forced conversion.",
            "Biradari (clan/caste) system in Punjab shapes marriage, politics, occupation access. Names signal biradari — Khan, Butt, Chaudhry, Sheikh, Rajput, Arain, Gujjar.",
            "Inflation peaked 35%+ (2023). Electricity prices doubled. Gas shortages. Economic anxiety is UNIVERSAL.",
        ],
    },
    "Nepal": {
        "segment_weights": {
            "rural": 0.35,
            "urban_working": 0.20,
            "middle_class": 0.15,
            "corporate": 0.05,
            "migration_workers": 0.13,
            "students": 0.06,
            "women": 0.04,
            "elderly": 0.02,
        },
        "regions": {
            "kathmandu": "Kathmandu Valley: capital + Lalitpur + Bhaktapur. Government, tourism gateway, IT growing, Newar cultural heritage (UNESCO). Most cosmopolitan. RSP/Balen Shah powerbase post-March 2026. Professional women normalized. Domestic workers from rural (Tamang, Dalit, Terai). 2015 earthquake damage partially rebuilt.",
            "pokhara": "Pokhara/Gandaki: tourism hub (Annapurna views, paragliding, trekking gateway). Gurkha retirement community — British/Indian Army pensions. Gurung, Magar communities. Lake tourism economy. Relatively prosperous from military pensions + tourism.",
            "terai": "Terai/Madhesh Province: southern plains, Indian border. Madhesi population (culturally closer to Bihar/UP). Tharu indigenous. Full Indian-style caste system. MOST restricted women. Open border with India = massive circular migration. Industrial (Birgunj, Biratnagar). Kamaiya (bonded labor) legacy in west. Muslim community concentrated here. Cross-border trade.",
            "eastern_hills": "Eastern hills (Koshi Province): Rai, Limbu, Kirant communities. Gurkha recruitment tradition. Terraced farming. ENORMOUS male out-migration — villages of women, children, elderly. Major source for Gulf/Malaysia workers. 2015 earthquake damage. Left-behind women manage everything.",
            "western_hills": "Western hills (Lumbini, Karnali, Sudurpashchim): Brahmin-Chhetri + Magar + Tharu. Karnali = most remote, poorest province. Food insecurity. Limited road access. Extreme out-migration. FCHV (health volunteers) are significant female occupation. Maoist insurgency history (1996-2006).",
            "mountain": "Mountain zone (Solukhumbu/Everest, Mustang, Dolpo, Manang): Sherpa, Tibetan Buddhist. Tourism/trekking economy. Lodge owners (women manage while husbands guide). Extreme altitude — limited agriculture. Yak herding. Most isolated communities. Climate change anxiety (glaciers melting).",
            "mixed": "A mixed Nepal sample reflecting 25% GDP from remittances (world's highest ratio), 3.5M workers abroad (14% of population), post-Sep 2025 Gen Z uprising, RSP/Balen March 2026 landslide, caste-ethnicity-geography nexus (Brahmin-Chhetri 29% dominating politics, Janajati 36%, Madhesi 32%, Dalit 13.6%), and MASSIVE left-behind women economy.",
        },
        "dialects": "Use Nepal-relevant: Kathmandu Nepali (urban, English-mixing), Nepali (standard hill — most agents), Maithili (Terai Madhesh — second most spoken), Bhojpuri (western Terai), Newari/Nepal Bhasa (Newar — Kathmandu Valley), Tamang (hills near KTM), Sherpa (Tibetan-related — mountain), Tharu (Terai indigenous). Match dialect to caste/ethnicity and geography.",
        "country_rules": [
            "Remittance IS the economy — 25% of GDP, 55.8% of households receive it. Most young men ABSENT. Generate many 'left-behind women' who manage everything but are not counted as employed.",
            "Caste + ethnicity + geography = the person. Brahmin Kathmandu ≠ Tamang hills ≠ Tharu Terai ≠ Sherpa mountains ≠ Musahar Madhesh — same country, completely different lives.",
            "Post-September 2025 Gen Z uprising: 76 killed. RSP/Balen March 2026 landslide. KEY DIVIDE IS GENERATIONAL. Every agent under 30 shaped by uprising.",
            "Gurkha military (British/Indian Army) = DISTINCT pathway for Gurung, Magar, Rai, Limbu. Pensions → relative prosperity. Different from Gulf labor migration.",
            "Madhesi (Terai) women = MOST restricted — similar to Bihar/UP India. Purdah/ghunghat. Tharu women relatively more active. Muslim Madhesi most restricted.",
            "Dalit: 42% below poverty line. Untouchability STILL practiced. Caste-locked occupations persist. Musahar (Terai Dalit) among most destitute in South Asia.",
            "Kamaiya (bonded labor): Tharu Terai — formally abolished 2000 but legacy of landlessness, poverty, trauma persists. First-generation post-Kamaiya now adults.",
            "FCHV (Female Community Health Volunteer) = significant female occupation. Rs 3,000/month. Vaccination, maternal health. Often most educated woman in village.",
            "2015 earthquake: 9,000 killed, 800,000 homes destroyed. Agents from Sindhupalchok, Gorkha, Dhading: displacement history, reconstruction debt.",
        ],
    },
    "Sri Lanka": {
        "segment_weights": {
            "rural": 0.28,
            "urban_working": 0.25,
            "middle_class": 0.18,
            "corporate": 0.08,
            "migration_workers": 0.09,
            "students": 0.06,
            "women": 0.04,
            "elderly": 0.02,
        },
        "regions": {
            "colombo": "Colombo/Western Province: economic hub, most cosmopolitan, corporate HQ, port, tourism gateway. Pettah = Muslim trading district. Colombo 7 = elite. Negombo = Catholic fishing. Garments FTZ (Katunayake, Biyagama). LOWEST restriction on women. Most ethnically integrated. IT sector (WSO2, Virtusa, 99X). 2022 crisis epicenter — aragalaya protests centered here.",
            "kandy": "Kandy/Central/Hill Country: sacred Buddhist city (Temple of Tooth). Tea estates = Malaiyaha Tamil community (MOST marginalized — line rooms, Rs 1,350/day, 90% landless, 200 years exploitation). Nuwara Eliya = 'Little England'. Kandyan Sinhala = conservative aristocratic. Plantation economy dominates hill country. Two COMPLETELY different worlds coexist.",
            "galle": "Southern Province: Galle (colonial Dutch fort — UNESCO, boutique hotels, surfing). Tourism BOOMING (Mirissa whale watching, Weligama surfing). Hambantota = Rajapaksa heartland (white elephant port/airport with Chinese loans). Fishing communities. Cinnamon cultivation. Overwhelmingly Sinhala Buddhist. Conservative.",
            "jaffna": "Northern Province/Jaffna/Vanni: Tamil heartland. Jaffna = educated professional class tradition. Vanni (Kilinochchi, Mullaitivu) = final war battlefield — most destroyed area. 89,000 war widows. Military still occupies land. Missing persons. Diaspora in Canada/UK/Australia. trust_government: VERY LOW. Palmyra economy. Hindu temples. Catholic minority.",
            "batticaloa": "Eastern Province: most ethnically mixed (Tamil Batticaloa, Muslim Ampara, Sinhala). Post-war + post-tsunami + post-Easter-2019 Muslim backlash. Fishing dominant. Lagoon farming. Muslim community (Tamil-speaking) faced severe backlash after Easter bombings despite NO connection to bombers.",
            "nuwara_eliya": "Hill Country Estates: Malaiyaha (plantation) Tamil world. Tea plucking (100,000+ women). Line rooms (10x12 feet, 5-10 people). Rs 1,350/day minimum. 90% landless. Distinct from Jaffna Tamil — different dialect, caste, history. Young women escape to Colombo FTZ. Young men to Gulf. Education = only exit.",
            "ratnapura": "Sabaragamuwa/Gem Country: gem mining (sapphires, rubies — Ratnapura = 'City of Gems'). Hand-dug pits — dangerous. Miners poor despite valuable finds. Dealers profit. Also tea/rubber estates. Uva: vegetable farming for Colombo market.",
            "mixed": "A mixed Sri Lanka sample reflecting 2022 crisis shared trauma (69.8% inflation, 13-hour power cuts, aragalaya), 74.9% Sinhala + 11.2% Tamil + 4.1% Malaiyaha + 9.3% Muslim composition, NPP/AKD political transformation, 24.5% poverty rate (twice 2019), and $1.9B garment sector at tariff risk.",
        },
        "dialects": "Use Sri Lanka-relevant: Sinhala urban (Colombo — code-switching with English), formal Sinhala (Kandy — more traditional), Tamil Jaffna style (educated, 'pure' Tamil), Malaiyaha estate Tamil (South Indian dialect mixing — distinct from Jaffna), Tamil-English mix (professional), Sinhala-English mix (Colombo corporate), Muslim Tamil (Eastern Province), English only (Burgher, elite).",
        "country_rules": [
            "2022 economic crisis is SHARED NATIONAL TRAUMA. 69.8% inflation, 13-hour power cuts, fuel queues, empty pharmacies. baseline_anxiety elevated for ALL agents. Middle-class savings destroyed. Working-class skipped meals.",
            "Ethnicity is the PRIMARY variable — more than class. Sinhala, Sri Lankan Tamil, Malaiyaha Tamil, and Muslim of same income = COMPLETELY different lives.",
            "Malaiyaha (plantation) Tamil is DISTINCT from Jaffna Tamil. Different community, dialect, caste, history. 90% landless, line rooms, tea plucking. DO NOT conflate.",
            "For Tamil agents (north/east): war trauma is PRESENT. Missing family. Military surveillance. 89,000 war widows. Memorial suppression. trust_government: VERY LOW regardless of who governs.",
            "Post-Easter 2019: Muslim community faced severe backlash. Shops boycotted. Women targeted for hijab. Muslim agents: minority anxiety, low trust.",
            "Garments FTZ ($1.9B, 300,000 workers — primarily young SINHALA women) at risk from Trump 44% tariff threat.",
            "NPP/AKD won Sep 2024 — first genuinely new political force. But JVP insurrection history (1971, 1987-89) frightens older voters.",
            "Brain drain post-2022: over 300,000 left. Doctors, IT, nurses emigrating. Remittances became critical lifeline.",
        ],
    },
}

COUNTRY_SEGMENT_PRIORS: Dict[str, Dict[str, str]] = {
    "Bangladesh": {
        "rural": "Occupations: paddy farmer, sharecropper (bargadar), agricultural day laborer (hari), fish farmer, shrimp farm worker, jute farmer, char land subsistence farmer, livestock rearer, poultry farmer, vegetable cultivator, Sundarbans resource collector. Women: homestead poultry, vegetable garden, unpaid family agricultural labor, rice husking, shrimp peeling (coastal), tea garden plucker (Sylhet Adivasi only). Bias: food-price sensitivity, community reputation pressure, farm/day-wage uncertainty, climate vulnerability. 84% informal.",
        "urban_working": "Occupations: garments sewing operator/helper/QC (female), garments cutter/ironer/supervisor (male), rickshaw puller, CNG driver, Pathao/foodpanda rider, construction mason/helper, security guard, domestic helper (migrant women only), beauty parlor worker, tea stall owner, hotel/restaurant worker, office peon, delivery rider, market porter. Bias: wage/rent/utility pressure, dense peer influence, informal employment, post-revolution distrust.",
        "middle_class": "Occupations: government school teacher, college lecturer, nurse, NGO program officer, microfinance branch manager, bank clerk, government office clerk, journalist, pharmacist, private tutor, coaching center teacher, upazila health officer. Bias: balancing dignity and cost pressure, salaried stability anxiety, education spending, post-revolution institutional distrust.",
        "corporate": "Occupations: doctor (MBBS/specialist), university professor, software engineer (bKash/Grameenphone/Pathao), banker (officer+), corporate manager (HR/marketing/supply chain), lawyer (high court), architect, engineer (BUET), NGO senior management, development consultant (WB/ADB/UNDP), media professional. Bias: polished English-mixed posting, career caution, lower shame sensitivity, professional network anxiety.",
        "migration_workers": "Occupations: construction laborer (Saudi/Qatar/UAE — LARGEST), domestic driver (Gulf), security guard abroad, factory worker (Malaysia/Singapore), cleaning worker (UAE/Qatar), restaurant worker (Gulf/Italy/Greece), agricultural worker (Saudi/Jordan). Female: domestic worker (Saudi Arabia — largest female category), garments worker (Jordan EPZ), factory worker (Malaysia). Bias: Gulf remittance duty, family absence, migration fraud anxiety, kafala system vulnerability, 67% go to Saudi Arabia.",
        "students": "Occupations: university student, college student, private university student, coaching student, madrasa student, Pathao rider (37% of riders are students), freelancer (graphic design, data entry), F-commerce seller, social media content creator. Bias: high Facebook intensity, peer amplification, family-budget fear, post-July 2024 uprising trauma — many participated and saw peers killed/blinded. Politically radicalized by experience.",
        "women": "Occupation MUST match zone norms. Dhaka slum: anything available (garments, domestic, waste picking, hawking). Dhaka middle: teacher, nurse, NGO, bank. Chittagong local: teaching, nursing, beauty parlor (NOT garments — stigma). Sylhet: mostly not working (remittance family) or teaching/NGO only. Coastal/north: agricultural labor, shrimp peeling, brick kiln. Bias: gendered safety, household management, social scrutiny, zone-specific occupation constraints.",
        "elderly": "Occupations: retired government employee (pensioned), retired teacher, retired trader/shopkeeper, elder family caretaker, pensioner, village elder/matbar, retired imam. Bias: lower posting, memory of 1974 famine and past price shocks, dependence on family networks, medical expense anxiety, slower but durable opinion change.",
    },
    "India": {
        "rural": "Occupations: farmer (marginal/small/medium), agricultural day laborer, NREGA worker, tea plucker (Adivasi — Assam/WB/TN), sugarcane cutter (MH/KA migrant couples), cotton picker, toddy tapper (Kerala), fisherman, dairy farmer, tendu leaf collector (tribal — MP/CG/JH). Women: unpaid family farm worker (LARGEST invisible category), NREGA worker (55% female), ASHA health worker, anganwadi worker, bidi roller (Dalit/Muslim women), salt pan worker. Bias: caste shapes occupation, food/fuel prices, NREGA dependency, climate vulnerability, 81% informal.",
        "urban_working": "Occupations: domestic worker (female — LARGEST urban category — migrant from UP/Bihar), construction laborer (migrant), garments factory worker (Tirupur/Bangalore/Noida), auto-rickshaw driver, delivery rider (Swiggy/Zomato/Blinkit — 12M gig workers), security guard, beauty parlor worker, ASHA/anganwadi worker, rag picker (Dalit), street vendor, call center agent. Bias: rent/commute/utility pressure, gig economy precarity, caste-based occupational clustering, communal discrimination (Muslim riders).",
        "middle_class": "Occupations: government school teacher (competitive exam — stable, pensioned), nurse (Kerala nurses globally famous), bank officer (SBI/PNB/IBPS exam), government clerk (SSC/state PSC), NGO program officer, microfinance officer (Bandhan/Ujjivan), journalist (regional media), police sub-inspector, LIC officer, railway clerk. Bias: status maintenance, education spending, EMI stress, government exam anxiety, reservation politics (OBC/SC/ST quotas shape career access).",
        "corporate": "Occupations: software engineer (TCS/Infosys/Wipro/startups/MNCs — Bangalore/Hyderabad/Pune/Chennai/NCR), doctor (AIIMS/Apollo/Fortis), corporate manager (HR/marketing/finance), CA, lawyer (high court), IAS/IPS (UPSC — most prestigious), university professor, startup founder, investment banker. Bias: LinkedIn-style professional self-presentation, career caution, English-heavy posting, Hinglish corporate-speak, IT layoff anxiety.",
        "migration_workers": "Occupations: construction laborer (Gulf — Saudi/UAE/Qatar — largest), construction migrant (interstate — Delhi/Mumbai/Gujarat from UP/Bihar), domestic driver (Gulf), factory worker (Malaysia/Singapore — skilled), IT professional (USA/UK — H1B), nurse abroad (Kerala — Gulf/UK/USA), seafarer/merchant navy. Internal: 600M+ migrants, UP+Bihar = half. Bias: contractor/broker exploitation, COVID reverse-migration trauma, wage theft, kafala (Gulf), family separation, communal discrimination at destination.",
        "students": "Occupations: university student, IIT/NIT/medical aspirant (Kota coaching — extreme pressure), government exam aspirant (UPSC/SSC/banking — millions competing), engineering student, medical student, gig worker (Swiggy/Zomato rider while studying), freelancer. Bias: exam competition anxiety (millions for few seats), paper leak rage, Agniveer controversy, unemployment after degree, student loan pressure, meme fluency, peer amplification.",
        "women": "Occupation MUST match state/caste norms. UP/Bihar: agricultural labor (poor), ASHA/anganwadi, chikan embroidery (Muslim — Lucknow), bidi rolling (Dalit/Muslim), domestic helper (migration). Rajasthan: extreme Rajput ghoonghat — very restricted. Kerala: nurse, teacher, professional — most empowered. TN: garments, all sectors including bus conductor. Mumbai: domestic worker (migrant) to corporate professional. NE: most economically active women — Khasi matrilineal. Bias: state-specific gender norms, caste-specific restrictions, triple discrimination for Dalit women.",
        "elderly": "Occupations: retired government employee (pensioned), retired teacher, retired army, retired shopkeeper/trader, village elder (sarpanch/mukhiya), retired priest/pandit, pensioner (IGNOAPS — Rs 200-500/month — barely subsistence). Bias: pension insufficiency, medicine costs, joint family erosion, memory of Emergency/communal violence/partition (oldest), slower but durable opinion change, religious observance increasing.",
    },
    "Pakistan": {
        "rural": "Occupations: wheat/cotton/rice/sugarcane farmer, agricultural day laborer (mazoor/hari — often bonded in Sindh), livestock herder, dairy farmer, fisherman (Sindh coast), date farmer (Balochistan). Women: cotton picker (seasonal — women+children), livestock management at home, home-based embroidery, lady health worker. Bias: inflation (35%+), electricity price doubled, fertilizer cost, feudal exploitation (Sindh/south Punjab), honor culture, 72% informal.",
        "urban_working": "Occupations: truck driver (legendary decorated trucks), auto-rickshaw driver, Careem/inDriver rider, foodpanda/Bykea delivery rider, construction mason/laborer, textile factory worker (Faisalabad), sports goods worker (Sialkot), security guard, shopkeeper (kiryana), hotel restaurant worker, municipal worker. Women: domestic helper (poorest — often Christian), beauty parlor, private school teacher (Rs 8,000-25,000/month), factory worker (stigmatized). Bias: electricity/fuel/food costs, gig economy precarity, political crisis anxiety.",
        "middle_class": "Occupations: CSS officer (most prestigious), government teacher (through NTS), bank officer (commercial banks), police officer, doctor (government hospital), engineer (government), university lecturer (HEC), lawyer, NGO program officer. Women: government teacher, nurse, bank officer, call center agent, corporate professional, IT freelancer, lawyer. Bias: salaried stress, school fees, institutional distrust, CSS exam competition, professional class brain drain anxiety.",
        "corporate": "Occupations: software developer/IT (10Pearls, Systems Ltd, Netsol), corporate executive (Unilever, Engro, Lucky Group, Nestle, Telenor/Jazz), chartered accountant (ICAP), lawyer (Supreme Court), doctor (Aga Khan, Shifa — private), media professional (TV anchor — Geo, ARY, Hum), startup founder. Bias: polished Urdu-English code-switching, politically careful, IT export pride ($3.8B record), brain drain temptation, LinkedIn-style self-presentation.",
        "migration_workers": "Occupations: construction worker (Saudi/UAE/Qatar/Kuwait — LARGEST), driver (Gulf household/taxi), factory worker (Saudi/Malaysia), restaurant/hotel (Gulf/UK), taxi driver (UK London — Mirpuri community), IT professional (UK/USA/Canada — skilled migration), doctor (UK NHS), student-worker (Canada/Australia/UK). Bias: Gulf remittance ($38.3B record), kafala exploitation, UK diaspora connections, brain drain wave post-2022 crisis.",
        "students": "Occupations: university student, CSS aspirant, medical student (MDCAT exam), engineering student (NUST, GIKI, UET), madrasa student (qawmi/alia system — millions), O/A levels student (elite — English-medium), freelancer (IT — Pakistan 4th globally). Bias: political activism (PTI supporters dominant among youth), digital-first presence, exam competition, unemployment anxiety after degree, brain drain aspiration — half of post-secondary educated want to leave Pakistan.",
        "women": "Occupation MUST match province/ethnicity. Lahore/Islamabad: doctor, teacher, banker, IT freelancer, NGO worker (with family permission). Karachi Mohajir: most active — corporate, media, banking, teaching. KP: ONLY doctor (female ward), teacher (girls school), LHW, home-based embroidery. South Punjab/Interior Sindh: cotton picking (feudal), livestock, home-based stitching. Balochistan: virtually invisible except Hazara Shia. Universal: home-based food business, stitching, beauty parlor.",
        "elderly": "Occupations: retired government officer (CSS/PCS — pensioned), retired military (army — pension + cantonment privileges), retired teacher, retired shopkeeper/trader, village elder/numberdar, retired imam, pensioner. Bias: conservative speech, inflation devastating fixed-income pensioners, memory of Zia era/1971/prior crises, slower but durable opinion, religious observance increasing.",
    },
    "Nepal": {
        "rural": "Occupations: subsistence farmer (terraced — rice, maize, millet), livestock keeper (goats, buffalo), FCHV health volunteer (Rs 3,000/month), remittance household manager (manages everything while husband abroad), tea house/lodge worker (trekking), porter (female — doko baskets), carpet/dhaka weaver, agricultural laborer (Terai — paddy, wheat), brick kiln worker (Terai — bonded). Men: farmer, Gulf/Malaysia construction worker (PRIMARY for young men), trekking guide/porter, Gurkha soldier, seasonal labor to India. Bias: remittance dependency, left-behind women economy, 2015 earthquake scars.",
        "urban_working": "Occupations: taxi/Pathao driver (Kathmandu — ex-Gulf returnee common), construction worker, shopkeeper, restaurant worker, hotel/tourism, motorcycle taxi, domestic worker (from rural — Tamang/Dalit/Terai women), beauty parlor, market vendor, small trader, handicraft seller (Thamel tourist market). Bias: Kathmandu cost pressure, migration aspiration, Gen Z political engagement, RSP/Balen hope.",
        "middle_class": "Occupations: government officer (Lok Sewa Aayog exam — Brahmin-Chhetri dominated), teacher (government school — significant female), nurse, bank clerk (Nabil, NIC Asia, Sanima), NGO program officer, police officer, Nepal Army officer, FCHV coordinator, journalist, lawyer. Bias: government exam competition, Brahmin-Chhetri institutional dominance, brain drain anxiety, post-uprising institutional distrust.",
        "corporate": "Occupations: IT professional (Kathmandu — growing), corporate executive (Chaudhary Group, Ncell, banking), hotel/tourism manager, doctor (government + private), lawyer, startup founder (small ecosystem), journalist. Bias: English-mixed, brain drain temptation (Australia/Canada), post-uprising optimism, professional aspiration vs Nepal's limited opportunities.",
        "migration_workers": "Occupations: construction worker Gulf (Saudi/Qatar/UAE/Kuwait — kafala — LARGEST), factory worker Malaysia, factory worker South Korea (EPS — well-paid, legal, competitive), factory/warehouse Romania/Croatia/Poland (emerging — 368x increase), seasonal labor India (open border — construction, security, agriculture), Gurkha British/Indian Army (distinct — Gurung/Magar/Rai/Limbu — pensions), student-worker Australia/UK/Canada. Women: domestic worker Gulf (Saudi/Kuwait — abuse documented). Bias: recruitment fraud ($100-500K in fees), debt bondage, worker deaths abroad, kafala, remittance obligation, 14% of population absent.",
        "students": "Occupations: university student (TU, KU, Pokhara), IT student, medical student, Pathao delivery rider (student), freelancer (IT — growing), government exam aspirant (Lok Sewa). Bias: Gen Z — shaped by Sep 2025 uprising (friends killed by police), RSP/Balen supporters, anti-corruption digital activism, migration to Japan/Korea/Australia aspiration, unemployment anxiety.",
        "women": "Occupation MUST match caste/ethnicity/geography. Hill: subsistence farmer + livestock + FCHV + remittance manager (left-behind while husband abroad). Kathmandu: teacher, nurse, IT, NGO, bank, beauty parlor. Terai Madhesi: MOST restricted — agricultural labor if poor, home if middle-class, purdah in upper castes. Sherpa/mountain: lodge management. Tharu: Kamaiya-legacy landlessness. Dalit: domestic work, brick kiln, caste-locked occupations. Bias: 55.8% of households = remittance-dependent — women ARE the domestic economy but invisible.",
        "elderly": "Occupations: retired government teacher, retired Nepal Army, retired Gurkha (British/Indian — pension), retired farmer, village elder, retired shopkeeper. Bias: Maoist insurgency memory (1996-2006), 2015 earthquake loss, Gen Z uprising shock (September 2025), children emigrated — alone, pension/remittance dependency.",
    },
    "Sri Lanka": {
        "rural": "Occupations: paddy farmer, tea estate worker (Malaiyaha Tamil — Rs 1,350/day — most marginalized), rubber tapper, cinnamon peeler (Galle/Matara — women), fisherman (all coasts — post-tsunami rebuilt), coconut farmer, vegetable farmer (hill country), palmyra product maker (Jaffna — women). Women: tea plucker (100,000+ Malaiyaha women), paddy laborer, fish processor/seller, cinnamon peeler. Bias: 2022 crisis trauma (food prices doubled), 24.5% poverty, plantation exploitation, climate vulnerability.",
        "urban_working": "Occupations: tuk-tuk driver (ICONIC — Rs 1,500-5,000/day), garments FTZ worker (Katunayake/Biyagama — young Sinhala women — at tariff risk), construction worker, domestic worker (rural→urban migration), bus driver/conductor, delivery rider (PickMe/Uber Eats), beauty parlor worker, small shopkeeper, market vendor, hotel/tourism worker. Bias: 2022 crisis wage erosion (real wages still below 2019), cost-of-living pressure, tariff threat to garments, gig economy growth.",
        "middle_class": "Occupations: government school teacher (pensioned — Sinhala/Tamil/English medium), nurse (many migrating abroad for better pay), bank officer (BOC, People's Bank, Commercial, HNB), government SLAS officer, midwife (PHM), NGO worker (post-war/post-crisis), journalist, accountant (CIMA/ACCA). Bias: 2022 savings destroyed, brain drain pressure (colleagues leaving), NPP hope vs JVP fear, status loss anxiety, IMF austerity (VAT 18%, income tax 30%).",
        "corporate": "Occupations: IT professional (WSO2, Virtusa, 99X, IFS — many emigrating post-2022), corporate executive (John Keells, MAS, Dialog, Hayleys), doctor (government + private), lawyer, accountant (CIMA/ACCA), hotel/tourism manager, architect. Bias: brain drain (Australia/Canada/Singapore offers), polished Sinhala/English code-switching, corporate resilience vs crisis exhaustion, tariff threat to export sectors.",
        "migration_workers": "Occupations: domestic worker in Gulf — Saudi/Kuwait/UAE (LARGEST female category — abuse documented), construction worker Gulf (male — largest), IT professional abroad (Australia/Canada/UK/Singapore — brain drain post-2022), nurse abroad (Gulf/UK/Australia), doctor abroad (UK NHS/Maldives), merchant navy seafarer, hotel worker (Maldives — close/well-paying), factory worker Korea (EPS — competitive). Bias: post-2022 brain drain wave (300,000+ left), Gulf domestic worker abuse/kafala, remittances as family lifeline, guilt about leaving.",
        "students": "Occupations: university student (Colombo/Peradeniya/Jaffna/Kelaniya/Moratuwa), A/L student (GCE Advanced Level — make-or-break exam), IT student, medical student. Bias: 19.8% youth unemployment (one in five), educated unemployment paradox (25.7% for young women), 2022 crisis disrupted education (schools closed — no paper for exams), brain drain aspiration, NPP political engagement, aragalaya participation memory.",
        "women": "Occupation MUST match ethnicity. Sinhala: garments FTZ (young, boarding house), teacher, nurse, corporate professional, cinnamon peeler, fish seller. Malaiyaha Tamil: tea plucker (PRIMARY), estate domestic, FTZ migration. Jaffna Tamil: war widow running multiple informal jobs, teacher, NGO, palmyra, fish processing. Muslim: trading family (behind scenes), some professional in Colombo. Bias: 30.3% female LFPR (among lowest), 2022 crisis = skipped meals, ethnic-specific constraints.",
        "elderly": "Occupations: retired government teacher (pensioned), retired military (large standing army), retired bank officer, retired plantation worker (no adequate pension), temple/church community elder, retired fisherman. Bias: 2022 crisis devastated fixed-income pensioners, medicine costs, children emigrated (brain drain), JVP insurrection memory (1971/1987-89 — fear), war memory, aragalaya observation.",
    },
}

DIASPORA_REGION_SETTINGS = {
    "gulf": "Gulf migrant and family-remittance networks across Saudi Arabia, UAE, Qatar, Kuwait, Oman, and Bahrain.",
    "uk": "United Kingdom diaspora communities with intergenerational identity tension and political discussion tied back home.",
    "eu": "European diaspora communities with mixed labor and professional migration patterns.",
    "us": "United States diaspora communities with class-diverse, education-heavy, and transnational identity patterns.",
    "north america": "North American diaspora communities across the United States and Canada.",
    "southeast asia": "Diaspora communities across Malaysia, Singapore, and nearby labor corridors.",
    "mixed": "A mixed diaspora sample across Gulf, UK, EU, and US communities.",
}

MIXED_SOUTH_ASIA_WEIGHTS = {
    "Bangladesh": 0.22,
    "India": 0.42,
    "Pakistan": 0.20,
    "Nepal": 0.08,
    "Sri Lanka": 0.05,
    "Diaspora": 0.03,
}

OPS_SEGMENT_ENTITY_TYPES = {
    "rural": "RuralHousehold",
    "urban_working": "UrbanWorkingFamily",
    "middle_class": "MiddleClassFamily",
    "corporate": "CorporateProfessional",
    "migration_workers": "MigrationWorker",
    "students": "Student",
    "women": "WomenHouseholdVoice",
    "elderly": "ElderlyCitizen",
}

INSTITUTIONAL_SEED_TYPES = {
    "governmentagency": "GovernmentAgency",
    "mediaoutlet": "MediaOutlet",
    "organization": "Organization",
    "expert": "Expert",
}

COUNTRY_INSTITUTIONAL_PRIORS: Dict[str, Dict[str, Any]] = {
    "Bangladesh": {
        "GovernmentAgency": ["Trading Corporation of Bangladesh", "DSCC Consumer Protection Cell", "Directorate of National Consumer Rights Protection", "Bangladesh Food Safety Authority", "BGMEA Labour Relations Desk", "Department of Labour (DIFE)"],
        "MediaOutlet": ["Prothom Alo Public Desk", "The Daily Star Price Watch", "Somoy TV Consumer Bureau", "Channel 24 Market Tracker", "Bangla Tribune Cost of Living Desk", "bdnews24.com Public Affairs"],
        "Organization": ["BRAC Community Resilience Forum", "Consumers Association of Bangladesh (CAB)", "Garment Workers Solidarity Forum", "Bangladesh Nari Progati Sangha", "Transparency International Bangladesh", "Ain o Salish Kendra (ASK)"],
        "Expert": ["Dr. Atiur Rahman (former BB governor)", "Prof. Rehman Sobhan", "Dr. Nazneen Ahmed (BIDS)", "Prof. Mustafizur Rahman (CPD)", "Dr. Fahmida Khatun (CPD)", "Shafiqul Alam (AFP bureau chief)"],
    },
    "India": {
        "GovernmentAgency": ["Department of Consumer Affairs", "Food Corporation of India (FCI) Public Desk", "NITI Aayog Policy Monitor", "Ministry of Labour and Employment", "National Commission for Women", "EPFO (Employees' Provident Fund Organisation)"],
        "MediaOutlet": ["NDTV Public Affairs Desk", "The Hindu Data Desk", "India Today Economy Bureau", "The Wire Investigative", "Scroll.in Labour Watch", "The Indian Express Consumer Desk"],
        "Organization": ["Self Employed Women's Association (SEWA)", "National Campaign on Dalit Human Rights (NCDHR)", "Aajeevika Bureau (migration rights)", "People's Union for Civil Liberties (PUCL)", "All India Trade Union Congress (AITUC)", "Indian Federation of App-based Transport Workers (IFAT)"],
        "Expert": ["Prof. Jean Dreze", "Prof. Jayati Ghosh", "Dr. Surjit Bhalla", "Prof. Ashwini Deshpande (caste-economics)", "Dr. Reetika Khera (NREGA/welfare)", "Prof. Kaushik Basu (former chief economist World Bank)"],
    },
    "Pakistan": {
        "GovernmentAgency": ["National Price Monitoring Committee (NPMC)", "Pakistan Bureau of Statistics Price Desk", "Ministry of Commerce Consumer Wing", "NEPRA (electricity regulator) Public Affairs", "State Bank of Pakistan Monetary Policy Desk", "Utility Stores Corporation"],
        "MediaOutlet": ["Dawn News Investigative Desk", "Geo TV Economy Bureau", "The News International Consumer Watch", "Express Tribune Data Desk", "Samaa TV Public Affairs", "The Friday Times Analysis"],
        "Organization": ["Human Rights Commission of Pakistan (HRCP)", "Pakistan Institute of Development Economics (PIDE)", "Aurat Foundation", "Pakistan Workers Federation (PWF)", "Home Based Women Workers Federation", "Edhi Foundation"],
        "Expert": ["Dr. Hafiz Pasha (economist — UNDP)", "Dr. Ishrat Husain (former SBP governor)", "Dr. Ayesha Siddiqa (military analyst)", "Prof. Kaiser Bengali (economist)", "Dr. Farzana Bari (gender studies — QAU)", "Mosharraf Zaidi (policy analyst — Tabadlab)"],
    },
    "Nepal": {
        "GovernmentAgency": ["Nepal Rastra Bank Public Affairs", "Department of Foreign Employment (DoFE)", "Ministry of Labour Employment Desk", "National Planning Commission", "Election Commission Nepal", "Consumer Protection Desk"],
        "MediaOutlet": ["Kathmandu Post Analysis Desk", "Republica Economy Bureau", "Online Khabar Consumer Watch", "Setopati Data Desk", "The Record Nepal", "Nepal Times Investigative"],
        "Organization": ["CESLAM (Centre for Study of Labour and Mobility)", "Nepal Institute for Social and Environmental Research (NISER)", "FEDO (Feminist Dalit Organisation)", "Pravasi Nepali Coordination Committee (PNCC)", "National Indigenous Women Forum (NIWF)", "Kamaiya Liberation Forum"],
        "Expert": ["Dr. Bishwambher Pyakuryal (economist)", "Prof. Chaitanya Mishra (sociologist)", "Dr. Ganesh Gurung (migration expert — CESLAM)", "Dr. Meena Acharya (gender economist)", "Jhalak Subedi (journalist — Record Nepal)", "Dr. Mahesh Maskey (development — TU)"],
    },
    "Sri Lanka": {
        "GovernmentAgency": ["Consumer Affairs Authority", "Department of Census and Statistics Price Division", "Central Bank of Sri Lanka Public Affairs", "Ministry of Labour Public Desk", "Samurdhi Authority (welfare)", "Board of Investment (BOI) FTZ Affairs"],
        "MediaOutlet": ["Daily Mirror Sri Lanka", "The Sunday Times Economy Desk", "Daily FT (Financial Times Sri Lanka)", "Hiru TV Consumer Bureau", "Tamil Mirror Public Affairs", "Colombo Gazette Analysis"],
        "Organization": ["Centre for Policy Alternatives (CPA)", "Verite Research", "Institute of Policy Studies (IPS)", "Women's Development Centre (WDC)", "Lanka Jathika Estate Workers Union", "National Fisheries Solidarity Movement (NAFSO)"],
        "Expert": ["Dr. Nishan de Mel (Verite Research)", "Prof. Sirimal Abeyratne (Colombo economics)", "Dr. Paikiasothy Saravanamuttu (CPA)", "Dr. Nisha Arunatilake (IPS)", "Ahilan Kadirgamar (political economist — Jaffna)", "Dr. Howard Nicholas (ISS — Sri Lanka development)"],
    },
}

INSTITUTIONAL_ROLE_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "GovernmentAgency": {
        "gender": "other",
        "age": 30,
        "trust_government": 8,
        "shame_sensitivity": 2,
        "influence_radius": 80000,
        "fb_intensity": 5,
        "income_stability": "institutionally stable",
        "rumour_amplifier": False,
        "baseline_anxiety": 2.5,
    },
    "MediaOutlet": {
        "gender": "other",
        "age": 30,
        "trust_government": 5,
        "shame_sensitivity": 3,
        "influence_radius": 120000,
        "fb_intensity": 8,
        "income_stability": "commercial but visible",
        "rumour_amplifier": False,
        "baseline_anxiety": 3.0,
    },
    "Organization": {
        "gender": "other",
        "age": 30,
        "trust_government": 4,
        "shame_sensitivity": 4,
        "influence_radius": 25000,
        "fb_intensity": 6,
        "income_stability": "grant- or donation-dependent",
        "rumour_amplifier": False,
        "baseline_anxiety": 3.5,
    },
    "Expert": {
        "gender": "other",
        "age": 42,
        "trust_government": 5,
        "shame_sensitivity": 3,
        "influence_radius": 18000,
        "fb_intensity": 5,
        "income_stability": "professionally stable",
        "rumour_amplifier": False,
        "baseline_anxiety": 3.2,
    },
}


# =============================================================================
# BANGLADESH OCCUPATIONAL REALITY SYSTEM
# Source: BBS Labour Force Survey 2024, ILO, BMET 2025, World Bank, field data
# =============================================================================

BANGLADESH_OCCUPATIONAL_REALITY: Dict[str, Any] = {

    # =========================================================================
    # SECTION 1: MACRO LABOR FACTS
    # =========================================================================

    "macro_labor_facts": {
        "total_labor_force": "71.71 million (LFS 2024)",
        "male_labor_force": "48.02 million",
        "female_labor_force": "23.69 million",
        "employed_population": "69.09 million",
        "unemployment_rate": "3.66% (2024)",
        "informal_employment": "84% of employed population — 58 million",
        "youth_labor_force_15_29": "24.83 million",
        "sector_agriculture": "44.67% — 31.83 million — LARGEST sector",
        "sector_services": "37.96% — 26.58 million",
        "sector_industry": "17.37% — 12.75 million",
        "female_lfpr": "34% of total labor force — declined from 36.5% in 2022",
        "women_informal_share": "89.5%+ of working women in informal sector",
        "women_rmg_dependency": "42% of rural female full-time jobholders work in RMG or its value chains",
    },

    "rmg_garments_facts": {
        "total_workers": "4-5 million",
        "female_share_current": "53-56% (declining from 80%+ in 1990s-2000s)",
        "export_value": "approximately $55 billion (2023)",
        "export_share_gdp": "84% of total exports",
        "minimum_wage_rmg": "BDT 12,500",
        "automation_threat": "ILO estimates 25% reduction in unskilled textile labor demand by 2030",
        "male_roles": "Cutting section, ironing/finishing, store/fabric handling, compliance, mid-management, buying house agents",
        "female_roles": "Sewing machine operators (largest), helpers, quality checkers, line leaders, washing/finishing, sample makers",
        "post_august_2024": "Many pro-AL garment factory owners fled. Factories shut. Workers lost entitlements. BGMEA reconstituted.",
        "ldc_graduation_risk": "Bangladesh faces LDC graduation 2026 — may lose preferential EU tariff access",
    },

    "migration_remittance_facts": {
        "overseas_workers_2025": "1.125 million deployed",
        "total_bangladeshis_abroad": "Over 13 million",
        "remittance_fy2025": "$30.04 billion — all-time record",
        "saudi_arabia_share": "67% of deployed workers in 2025",
        "gulf_gcc_share": "81% of all overseas workers",
        "female_migration_2025": "61,997 women — only ~5-6% of total",
        "key_destinations_male": ["Saudi Arabia", "UAE", "Qatar", "Kuwait", "Bahrain", "Oman", "Malaysia", "Singapore", "Italy", "Greece", "Libya", "South Korea", "Japan"],
        "key_destinations_female": ["Saudi Arabia", "UAE", "Kuwait", "Oman", "Lebanon", "Jordan", "Malaysia"],
        "fraud_problem": "BMET received 5,000+ complaints in 2024 — fake job offers, illegal visa trading",
    },

    "gig_economy_facts": {
        "total_gig_workers": "Over 1 million (estimated 2025)",
        "ride_sharing_drivers": "approximately 200,000",
        "delivery_riders": "approximately 400,000",
        "online_freelancers": "500,000-700,000 — second highest in South Asia",
        "key_platforms": ["Pathao", "Shohoz", "foodpanda", "HungryNaki", "Chaldal", "Daraz", "RedX", "eCourier", "bKash", "Nagad"],
        "student_gig_workers": "37% of Pathao supply-side providers are students",
    },

    "climate_migration_facts": {
        "annual_dhaka_influx": "Over 400,000 low-income individuals migrate to Dhaka annually (IOM)",
        "dhaka_slum_residents": "880,000 (Dhaka), 1.8 million nationally in slums (BBS Census 2022)",
        "brick_kilns": "8,000+ brick kilns — approximately 1 million workers including children",
        "source_zones": ["Satkhira", "Khulna coastal", "Barisal", "Bhola", "Noakhali islands", "Patuakhali", "Char lands of Jamuna and Padma", "Kurigram", "Gaibandha"],
        "destination_zones": ["Dhaka", "Narayanganj", "Gazipur", "Chittagong EPZ", "Khulna city"],
    },

    "political_context_2024_2026": {
        "july_revolution_2024": "Student-led uprising July 2024 over job quota system. PM Hasina fled to India on 5 August 2024.",
        "death_toll": "At least 1,400 killed. 20,000+ injured. 11,000+ arrested.",
        "interim_government": "Nobel laureate Muhammad Yunus became Chief Adviser. Advisory council includes student leaders.",
        "awami_league_banned": "Awami League banned from political activity under anti-terrorism laws (May 2025).",
        "election_timeline": "General election and referendum scheduled February 2026.",
        "law_and_order": "Sharp rise in mob violence post-revolution. Police discredited. Military patrols.",
        "economic_impact": "GDP growth slipped to 3.97%. Inflation above 8%. Food prices rising.",
        "agent_generation_note": "Political identity is EXPLOSIVE. Most agents will hide affiliation. trust_government is LOW across all segments. Generate political_lean as behavioral inference, never explicit label.",
    },

    # =========================================================================
    # SECTION 2: ZONE SOCIAL DYNAMICS
    # =========================================================================

    "zone_social_dynamics": {

        "dhaka": {
            "character": "Capital. 22+ million metro. Most diverse labor market. Garments hub (Gazipur, Savar, Ashulia). NGO sector global HQ. Corporate sector. Climate migrant destination. Highest income disparity.",
            "women_work_norms": "VARIABLE BY CLASS. Garments work normalized for working-class women. Professional work fully accepted. Upper-middle class paradoxical pressure to NOT work. Slum women work anything available.",
            "sub_zones": {
                "mirpur_mohammadpur": "Working class. Garments dominant. Conservative Muslim neighborhoods. Women work out of necessity. Political activism high.",
                "gulshan_banani_baridhara": "Elite. Corporate offices. Diplomatic zone. Women professionals normalized. Liberal social attitudes.",
                "dhanmondi": "Upper-middle class. University area. Intellectual tradition. Mixed conservative and progressive.",
                "uttara_bashundhara": "New middle class. Corporate. IT sector. Apartment living. Nuclear families.",
                "old_dhaka": "Trading families. Conservative artisan communities. Bihari community in Geneva Camp. Women rarely work outside.",
                "slums_korail_bauniabandh": "Climate migrants. Women work ANYTHING — domestic, garments, waste picking, brick carrying, hawking. No occupation stigma.",
                "gazipur_savar_ashulia": "EPZ and garment factory corridor. Workers are MIGRANTS from rural districts. Dormitory culture. Labour unrest history.",
                "keraniganj_narayanganj": "Industrial. Jute, textiles, garments. Working-class pragmatism.",
            },
        },

        "chittagong": {
            "character": "Port city. Second largest urban economy. Strong Chatgaayan identity. Trading tradition. Conservative Muslim majority. Significant Hindu minority. Ship-breaking (Sitakunda). EPZ garment factories.",
            "women_work_norms": "SIGNIFICANT STIGMA. Local Chatgaayan women discouraged from garments — associated with lower class. Acceptable: teaching, nursing, NGO, banking, own beauty parlor. Domestic work COMPLETELY taboo for local women.",
            "critical_note": "GARMENT WORKERS IN CHITTAGONG EPZ ARE MIGRANTS from Noakhali, Comilla, Feni, Lakshmipur — NOT local Chatgaayan women.",
        },

        "sylhet": {
            "character": "UK diaspora capital. Highest remittance dependency. Tea gardens. Sufi shrine culture. Sylheti dialect barely intelligible to Dhaka. Conservative Muslim majority. Strong pir culture.",
            "women_work_norms": "HIGH STIGMA. Remittance families expect women NOT to work — working = family cannot afford her = shame. Exception: teaching, NGO, health. Garments COMPLETELY unacceptable for local women.",
            "remittance_paradox": "Economic security but extreme gender enforcement. Women whose husbands are abroad manage everything but are not formally employed. primary_fear: husband stops sending money, remarries in UK.",
        },

        "rajshahi": {
            "character": "Silk industry. Mangoes (Chapainawabganj). Education hub (Rajshahi University). Hindu minority largest outside Dhaka. Border with India. Historically leftist/secular. Barind Tract drought-prone.",
            "women_work_norms": "MODERATE. Less remittance-driven than Sylhet. University presence creates secular atmosphere. Hindu women more likely to work. Silk weaving employs women home-based.",
        },

        "khulna_barisal_coastal": {
            "character": "Sundarbans gateway. Shrimp farming. Extreme climate vulnerability — cyclones, salinity, river erosion. Significant Hindu fishing communities. Migration SOURCE zone — people leave here.",
            "women_work_norms": "LOWER STIGMA — poverty overrides social pressure. Women in shrimp peeling, fish drying, crab collecting, agriculture. Climate displacement forces work regardless.",
            "migration_pattern": "Coastal displacement → Dhaka/Gazipur garments OR brick kilns OR domestic work. Men go to Gulf. Women to brick kilns or Dhaka.",
        },

        "rangpur_kurigram_north": {
            "character": "Historically monga (seasonal famine) poverty belt. Char lands of Jamuna/Teesta — extreme flood vulnerability. Day laborers. Lowest development indicators. Adivasi Santal community.",
            "women_work_norms": "LOW STIGMA — survival necessity. Women do agricultural day labor, tobacco processing, brick kiln (seasonal migration), domestic work. Education levels lowest. Early marriage highest.",
            "char_lands": "Char dwellers — extreme poverty. Seasonal displacement. Government services almost absent. Children work from age 8-10.",
        },

        "comilla_noakhali_feni": {
            "character": "Densely populated. Strong madrasa belt. High migration to Middle East. Noakhali history of communal violence. Island communities (Hatiya, Sandwip) climate-vulnerable.",
            "women_work_norms": "HIGH STIGMA in rural areas due to conservative religious influence. But MANY women migrate to Dhaka garments — top source region for female RMG workers. Paradox: conservative at home but pragmatic when poverty forces migration.",
        },

        "mymensingh_tangail": {
            "character": "Agricultural heartland. Jute (Tangail). Handloom weaving (Tangail saree). Haor wetland economy in Kishoreganj. Major internal migration source.",
            "women_work_norms": "MODERATE. Tangail handloom weaving employs women. Agricultural work common. Less extreme than Sylhet or Chittagong.",
        },
    },

    # =========================================================================
    # SECTION 3: FEMALE OCCUPATIONS — EXHAUSTIVE BY SEGMENT CONTEXT
    # =========================================================================

    "female_occupations": {

        "agricultural_rural": [
            "subsistence paddy farmer (own small plot)",
            "sharecropper (female-headed household — widowed/divorced/abandoned)",
            "agricultural day laborer (transplanting, weeding, harvesting)",
            "shrimp farm worker (coastal — peeling, sorting, cleaning)",
            "shrimp peeling shed worker (Khulna, Satkhira — piece rate)",
            "fish drying worker (coastal — sun-drying process)",
            "crab and shrimp collector (coastal mangroves)",
            "vegetable cultivator (homestead garden — sells surplus at local market)",
            "homestead poultry farmer (eggs and broilers — NGO-supported)",
            "goat and cattle rearing (livestock — often microcredit-linked)",
            "dairy milk production (home-based — sell to middlemen)",
            "sericulture worker — silk cocoon cultivation (Rajshahi)",
            "jute processing (retting, sorting, grading — seasonal)",
            "tobacco leaf drying and sorting worker (Rangpur, Kushtia)",
            "tea garden plucker (Sylhet, Moulvibazar — Adivasi women primarily)",
            "rice husking and processing (manual and small mill)",
            "betel leaf (paan) cultivation and preparation",
            "unpaid family agricultural labor — MOST COMMON, invisible in statistics",
        ],

        "home_based_informal": [
            "nakshi kantha embroidery (Rajshahi, Faridpur, Jessore — traditional quilt art)",
            "hand loom weaving (Tangail, Sirajganj, Narsingdi — sarees, gamchha, lungi)",
            "tailoring from home — stitching neighbor's clothes",
            "block printing on fabric (Narayanganj, Narsingdi)",
            "mat weaving from hogla/shital pati (Sylhet, Sunamganj)",
            "bamboo and cane craft (CHT, Sylhet, Mymensingh)",
            "jute craft — bags, dolls, decorative items (BRAC-promoted)",
            "incense stick (agarbatti) rolling (piece-rate home work)",
            "food preparation — tiffin service for offices and schools",
            "pickle, achaar, chanachur production (home-based small business)",
            "pitha (traditional cakes) making for sale at local markets",
            "F-commerce (Facebook commerce) — selling clothes, cosmetics, food online",
            "online freelancing — data entry, graphic design, digital marketing",
        ],

        "climate_migrant_survival": [
            "brick field worker — molding and carrying (seasonal 6 months)",
            "domestic helper — full-time live-in (from rural areas, NOT local urban women)",
            "domestic helper — part-time in multiple households",
            "fish and vegetable vendor — bazaar hawker",
            "street food hawker — pitha, tea, singara, fuchka, chotpoti",
            "waste picker and recycler (Dhaka slums — sorting plastics, metals)",
            "construction helper — carrying bricks, sand, water on head",
            "hospital ward cleaner and patient attendant (ayah)",
            "hotel and restaurant kitchen helper",
            "garments worker (if migrated to Dhaka/Gazipur and meets threshold)",
            "rice processing mill worker",
            "small market stall keeper — vegetables, fish, daily necessities",
        ],

        "urban_working_class": [
            "garments worker — sewing machine operator (LARGEST single female urban occupation)",
            "garments worker — helper (entry-level, lowest pay, youngest workers)",
            "garments quality checker (QC)",
            "garments line leader / supervisor (experienced — 5+ years)",
            "beauty parlor worker — assistant (shampoo, threading, henna)",
            "beauty parlor owner — small neighborhood parlor (female-only space)",
            "private school teacher — primary level (BDT 3,000-8,000/month)",
            "madrasa teacher — girls section",
            "diagnostic center and pathology lab receptionist",
            "NGO field worker — community level (BRAC shasthya shebika, ASA, Grameen)",
            "microfinance loan collection officer — field level",
            "community health worker — shasthya kormi (government community clinics)",
            "family planning field worker (house-to-house visits)",
            "data entry operator — small office, NGO, government project",
            "call center agent (Dhaka — customer service, telemarketing)",
            "supermarket and retail store sales staff (Shwapno, Agora, Meena Bazar)",
            "e-commerce packaging and dispatch worker (Daraz, Chaldal warehouse)",
            "childcare center (day care) worker",
        ],

        "middle_class_professional": [
            "government primary school teacher (NCTB curriculum — stable, pensioned)",
            "government secondary school teacher",
            "college lecturer (government and MPO)",
            "nurse — government hospital (diploma or BSc nursing)",
            "nurse — private hospital/clinic",
            "trained midwife (community skilled birth attendant — CSBA)",
            "NGO program officer — district or national level (BRAC, Oxfam, ActionAid)",
            "microfinance branch manager (BRAC, ASA, Grameen)",
            "bank clerk / teller (Sonali, Janata, BRAC Bank, Dutch-Bangla)",
            "government office clerk — entry level (non-cadre)",
            "journalist — regional newspaper, online news portal",
            "pharmacist — registered",
            "private tutor — secondary and higher secondary level",
            "coaching center teacher (after-school tutoring industry)",
        ],

        "corporate_elite_professional": [
            "doctor — MBBS (government hospital, private hospital, own chamber)",
            "specialist doctor — gynecology, pediatrics, dermatology",
            "university lecturer / assistant professor / professor",
            "software developer / IT professional (bKash, Pathao, Grameenphone)",
            "banker — officer grade and above (BRAC Bank, EBL, City Bank, SCB)",
            "corporate manager — HR, marketing, administration, supply chain",
            "lawyer / advocate — district court, high court",
            "NGO senior management — country director, program director",
            "development sector consultant (World Bank, ADB, UNDP projects)",
            "entrepreneur — SME owner (garments buying house, food, fashion)",
            "architect (BUET, BRAC University graduates)",
            "engineer — civil, electrical, software (rare but growing)",
            "diplomat — BCS foreign affairs cadre",
        ],

        "migrant_abroad": [
            "domestic worker — Saudi Arabia (LARGEST category for female migrants)",
            "domestic worker — UAE, Kuwait, Oman, Qatar, Lebanon, Jordan",
            "garments factory worker — Jordan EPZ",
            "factory worker — Malaysia (electronics, manufacturing)",
            "hotel and hospitality worker — UAE, Maldives",
            "nurse — Gulf countries and UK (professional migration)",
        ],
    },

    # =========================================================================
    # SECTION 4: MALE OCCUPATIONS — EXHAUSTIVE BY SEGMENT CONTEXT
    # =========================================================================

    "male_occupations": {

        "agricultural": [
            "paddy farmer — own land (boro, aman, aus seasons)",
            "sharecropper — bargadar (cultivates another's land for share)",
            "agricultural day laborer — hari (hired per day during planting/harvest)",
            "irrigation pump operator and mechanic",
            "fish farmer — pond aquaculture (pangasius, tilapia, carp — commercial)",
            "river fisherman (hilsa, other species — seasonal)",
            "deep sea fisherman (Cox's Bazar, Chittagong — dangerous, seasonal)",
            "shrimp farmer — gher owner or manager (Khulna, Satkhira)",
            "livestock and dairy farmer (cow fattening for Eid-ul-Adha — major seasonal business)",
            "commercial poultry farm worker and owner",
            "jute farmer (declining — Mymensingh, Faridpur, Jessore)",
            "vegetable farmer — commercial (Jessore, Bogura — tomato, potato, brinjal)",
            "char land farmer — subsistence (extreme poverty, flood-prone Jamuna/Padma)",
            "Sundarbans resource collector — honey, golpata, fish, crab (dangerous — tiger attacks)",
            "tea garden worker (Sylhet, Moulvibazar — Adivasi community)",
        ],

        "transport_logistics": [
            "pedal rickshaw puller — urban (declining as battery rickshaws grow)",
            "battery-powered rickshaw / easy bike driver (towns and rural — rapidly growing)",
            "van rickshaw driver — rural (goods and passengers on three-wheeled platforms)",
            "CNG auto-rickshaw driver (urban — Dhaka, Chittagong, Sylhet)",
            "ride-app motorcycle rider — Pathao, Shohoz (young urban males — student and full-time)",
            "bus driver — BRTC (government) and private",
            "bus helper / conductor (shouting routes, collecting fares)",
            "human hauler / leguna / tempo driver (shared micro-transport — peri-urban)",
            "truck driver — local and long-haul (inter-district goods transport)",
            "truck helper (assists driver, loads/unloads, sleeps under truck)",
            "cargo loader and unloader — dock worker, market porter (coolie)",
            "launch / ferry crew (river transport — Barisal, Dhaka, Chandpur routes)",
            "e-commerce delivery rider — Pathao Courier, RedX, eCourier, Paperfly",
            "food delivery rider — foodpanda, HungryNaki, Pathao Food",
        ],

        "construction_labor": [
            "construction mason — rajmistri (skilled bricklayer and plasterer)",
            "assistant mason — jogali (learning trade, mixing cement, carrying)",
            "construction day laborer — helper (carrying bricks, sand — lowest rung)",
            "rod binder / steel fixer (rebar tying — semi-skilled)",
            "shuttering carpenter (formwork for concrete)",
            "house painter (interior and exterior)",
            "tile and marble fitter",
            "brick field worker — furnace side (loading, firing kiln — hazardous)",
            "brick field worker — molding side (forming raw bricks from clay)",
            "sand and stone dredger / quarry worker (river bed extraction — dangerous)",
            "road construction worker",
        ],

        "skilled_trades": [
            "welder and fabricator — steel, aluminum, iron gate",
            "electrician — house wiring, industrial (certified and uncertified)",
            "plumber and pipe fitter (sanitary, water supply)",
            "AC technician and installer (growing with urbanization and climate heat)",
            "mobile phone repair technician (massive informal sector)",
            "motorcycle mechanic (Hero, Bajaj, Honda, Yamaha)",
            "car and microbus mechanic (auto workshop — garage)",
            "CNG auto-rickshaw mechanic",
            "carpenter and furniture maker",
            "tailor — men's clothing (shalwar kameez, panjabi, shirt, pant)",
            "goldsmith and jewelry maker (traditionally Hindu Swarnakar community)",
            "solar panel installer and technician (growing — rural electrification)",
        ],

        "trade_commerce": [
            "village grocery shop owner — modir dokan",
            "tea stall owner — cha er dokan (social hub — male gathering point)",
            "roadside food stall — biryani, khichuri, dal-bhat, tea and snacks",
            "wholesale trader — rice, grain, fish, vegetable (aratdar — commission agent)",
            "retail fish seller — bazaar (kacha bazar)",
            "cloth and textile merchant (Islampur, New Market, local bazaars)",
            "hardware shop owner (tools, cement, paint)",
            "mobile phone and accessory shop",
            "pharmacy / medicine shop (often without pharmacist qualification)",
            "fertilizer and agricultural input dealer (rural — seasonal)",
            "rice mill and flour mill operator",
            "scrap metal and recycling dealer (bhangari)",
            "pharmaceutical sales representative — MR (medical representative)",
            "real estate broker — dalal (land and property)",
        ],

        "urban_working_class_services": [
            "hotel and restaurant worker — cook, kitchen assistant, cleaner",
            "waiter and food server (male — almost all BD restaurants are male-staffed for service)",
            "security guard — building, office, factory, shopping mall",
            "night watchman — chowkidar",
            "office peon and cleaner — government and private",
            "municipal sweeper (stigmatized — often Dalit/harijan community)",
            "hospital ward boy and orderly",
            "building caretaker — darwan (apartment building manager/security)",
            "salesperson — shop floor (electronics, clothing, furniture)",
            "garments cutting master and cutter (cutting section — skilled, predominantly male)",
            "garments ironing and pressing (male-dominated — steam press, finishing)",
            "garments production supervisor and floor manager",
            "marriage event and catering worker — baburchi (cook for mass events)",
        ],

        "middle_professional": [
            "government officer — BCS cadre (administration, police, foreign affairs — highest prestige)",
            "police sub-inspector, inspector, ASP",
            "army non-commissioned officer — soldier, havildar, subedar",
            "teacher — government school, college, university (permanent, pensioned)",
            "bank officer — junior to senior",
            "NGO program officer and district coordinator",
            "journalist and reporter — print, TV, online",
            "court lawyer — junior to mid-level advocate",
            "doctor — upazila health complex (rural posting)",
            "engineer — government (PWD, LGED, BWDB)",
            "pharmaceutical sales manager — area manager",
        ],

        "corporate_elite": [
            "doctor — senior consultant, department head (Square, Apollo, United, Labaid)",
            "engineer — BUET-trained civil, mechanical, EEE, CSE",
            "software engineer (bKash, Grameenphone, Pathao, international remote)",
            "corporate executive — manager to VP to director",
            "commercial banker — senior officer, VP, SVP, EVP",
            "lawyer — high court and supreme court advocate",
            "university professor / vice-chancellor",
            "garments factory owner (RMG industry)",
            "real estate developer (Dhaka, Chittagong — apartment market)",
            "tech startup founder (Dhaka ecosystem — emerging)",
        ],

        "migrant_abroad": [
            "construction laborer — Saudi Arabia, Qatar, UAE, Oman (LARGEST category)",
            "construction project worker — roads, buildings, stadiums (Gulf)",
            "domestic driver — Saudi Arabia, UAE (private household)",
            "security guard abroad — UAE, Saudi Arabia, Qatar, Bahrain, Malaysia",
            "factory worker — Malaysia, Singapore (manufacturing, electronics)",
            "cleaning and janitorial worker — UAE, Qatar, Bahrain (malls, offices)",
            "restaurant and hotel worker — Gulf, Malaysia, Maldives, Italy, Greece",
            "agricultural worker abroad — Saudi Arabia, Jordan (greenhouse farming)",
            "ship crew — ocean-going cargo (lascar tradition — declining)",
            "manpower agent — dalal (migration broker — often exploitative)",
        ],

        "religious_community": [
            "imam — mosque (weekly Friday sermon, daily prayers, community disputes)",
            "muezzin — mosque (call to prayer, maintenance)",
            "madrasa teacher — maulvi, maulana (qawmi and alia system)",
            "Quranic teacher — huzur (teaching children Quran recitation)",
            "village doctor — palli chikitshak / quack (without formal degree — common)",
            "traditional healer — kabiraj (herbal medicine — declining)",
            "union parishad chairman and member (elected local government)",
            "NGO field staff — community mobilizer, credit officer",
        ],
    },

    # =========================================================================
    # SECTION 5: GENDER-OCCUPATION CONSTRAINTS BY ZONE
    # =========================================================================

    "gender_occupation_rules": {
        "universal": [
            "A woman's occupation MUST be plausible for her zone, class, religion, and family situation.",
            "Garment work for women is NORMALIZED in Dhaka/Gazipur but STIGMATIZED in Chittagong/Sylhet for local women.",
            "Garment workers in Chittagong EPZ are MIGRANTS from Comilla/Noakhali/Feni — NOT local Chatgaayan women.",
            "Domestic work is done by MIGRANT women — local middle-class women do NOT do domestic work.",
            "Brick kiln workers are seasonal MIGRANTS from climate-affected coastal/northern districts.",
            "Slum women have NO occupation stigma — they do anything available for survival.",
            "Upper-middle class women face paradoxical pressure to NOT work — husband's income as status symbol.",
            "Tea garden workers are Adivasi women (Sylhet/Moulvibazar) — ethnically distinct from Bangali Muslims.",
            "F-commerce (Facebook selling) is growing rapidly among urban women — socially acceptable home-based work.",
        ],
        "male_only_occupations": [
            "rickshaw puller", "CNG driver", "truck driver", "ship-breaking worker",
            "construction mason", "rod binder", "brick kiln furnace worker",
            "imam", "muezzin", "madrasa teacher (boys section)",
            "waiter/food server (almost all BD restaurants)", "night watchman",
        ],
        "female_dominated_occupations": [
            "garments sewing machine operator", "domestic helper",
            "beauty parlor worker", "shrimp peeling shed worker",
            "tea garden plucker", "nakshi kantha embroidery",
            "family planning field worker", "community health worker",
        ],
    },

    # =========================================================================
    # SECTION 6: FALLBACK NAME POOLS — AUTHENTIC BY RELIGION AND REGION
    # =========================================================================

    "name_pools": {
        "muslim_male": [
            "Rahim Hasan", "Sajjad Hossain", "Imran Kabir", "Masud Rana",
            "Kamal Uddin", "Shahin Mia", "Rashed Khan", "Jamal Ahmed",
            "Firoz Alam", "Milon Sheikh", "Babul Haque", "Sohel Rana",
            "Rafiqul Islam", "Mizanur Rahman", "Abdur Rahim", "Zahirul Haque",
            "Shamsul Alam", "Anwar Hossain", "Harun-or-Rashid", "Nurul Islam",
            "Abul Kalam", "Monir Hossain", "Selim Reza", "Tariqul Islam",
        ],
        "muslim_female": [
            "Ayesha Akter", "Ruma Khatun", "Farzana Rahman", "Sharmin Sultana",
            "Halima Begum", "Nasreen Akter", "Shirin Jahan", "Kulsum Bibi",
            "Marium Khatun", "Taslima Begum", "Shahida Akter", "Fatema Khatun",
            "Rehana Parvin", "Nazma Begum", "Bilkis Akter", "Rowshan Ara",
            "Amena Khatun", "Monowara Begum", "Hasina Akter", "Rashida Khatun",
        ],
        "hindu_male": [
            "Ratan Das", "Sunil Chandra", "Bikash Sarkar", "Dipak Saha",
            "Rajesh Barua", "Gopal Dey", "Arun Kumar", "Mrinal Chakraborty",
            "Ashok Mandal", "Tapan Ghosh",
        ],
        "hindu_female": [
            "Rina Rani Das", "Shilpi Sarkar", "Moushumi Saha", "Anjali Dey",
            "Purnima Barua", "Kakoli Mandal", "Shikha Chakraborty", "Mithu Rani",
        ],
        "adivasi_male": [
            "Suman Chakma", "Ratan Marma", "Bikash Tripura", "Dipak Tanchangya",
            "Sunil Santal", "Mohan Oraon",
        ],
        "adivasi_female": [
            "Sunita Chakma", "Renu Marma", "Mala Tripura", "Phulmoni Santal",
        ],
    },
}


# =============================================================================
# INDIA OCCUPATIONAL REALITY SYSTEM
# Source: PLFS 2023-24/2024, ILO India Employment Report, NITI Aayog,
#         IDSN caste-occupation research, Fairwork India, World Bank
# =============================================================================

INDIA_OCCUPATIONAL_REALITY: Dict[str, Any] = {

    # =========================================================================
    # SECTION 1: MACRO LABOR FACTS
    # =========================================================================

    "macro_labor_facts": {
        "population": "approximately 1.44 billion (2024)",
        "total_lfpr": "59.6% (2024 usual status)",
        "male_lfpr": "78.8% (2023-24)",
        "female_lfpr": "41.7% (2023-24) — UP from 23.3% in 2017-18 — but quality of work is concern",
        "unemployment_rate": "4.9% national (2024). Urban: 6.7%. Rural: 4.2%",
        "self_employed": "58.4% of workforce — LARGEST category",
        "regular_wage_salaried": "21.7%",
        "casual_labor": "19.8%",
        "informal_sector": "81% of employed in informal sector. Over 95% of working women informal.",
        "agriculture_share": "approximately 45% of workforce",
        "no_written_contract": "58% of regular salaried employees have NO written job contract",
        "flfpr_increase_driver": "Almost all 20-point FLFP increase since 2017 driven by rural self-employment in agriculture — NOT formal job creation. Many unpaid family workers.",
        "gender_earnings_gap": "Women earn 76% of men's earnings among salaried workers",
        "remittances": "$137 billion in 2024 — world's LARGEST remittance recipient",
    },

    "asha_anganwadi_frontline": {
        "asha_workers": "approximately 1.04 million ASHA workers",
        "anganwadi_workers_helpers": "approximately 2.5 million Anganwadi Workers and Helpers",
        "total_frontline_women": "approximately 3.5 million women designated as 'volunteers' — NOT workers",
        "asha_honorarium": "Rs 2,000-3,500 fixed monthly + performance incentives. Total Rs 7,000-8,000.",
        "worker_status_denied": "Classified as 'honorary volunteers' — denied minimum wages, EPF, pension, paid leave.",
        "protests": "Persistent strikes across India. Kerala ASHA strike 2025 crossed 100 days.",
        "agent_note": "ASHA/Anganwadi is a MASSIVE occupation for rural/semi-urban women. They are educated, trained in health, politically aware (they organize and strike), economically precarious despite essential role.",
    },

    "gig_economy_facts": {
        "total_gig_workers": "approximately 12 million by FY 2024-25",
        "projected_2030": "23.5 million by 2029-30 (NITI Aayog)",
        "key_platforms": ["Ola", "Uber", "Swiggy", "Zomato", "Urban Company", "Dunzo", "BigBasket", "Flipkart", "Amazon", "Blinkit", "Zepto", "Rapido", "Porter", "BluSmart"],
        "worker_earnings": "Delivery riders Rs 500-600/day. Ola/Uber drivers Rs 15,000-25,000/month before expenses.",
        "no_social_security": "No ESI, EPF, minimum wage, maternity benefits",
        "worker_protests": "Nationwide gig worker strikes 2025-26. Protests at Swiggy, Zomato, Ola, Uber.",
        "communal_discrimination": "Documented incidents of customers refusing delivery based on rider's Muslim name.",
    },

    "internal_migration_facts": {
        "total_internal_migrants": "Over 600 million. Migration rate 28.9% (PLFS 2022).",
        "top_source_states": ["Uttar Pradesh", "Bihar", "Rajasthan", "Madhya Pradesh", "Jharkhand", "Odisha", "Chhattisgarh", "West Bengal"],
        "top_destination_states": ["Maharashtra (Mumbai)", "Delhi NCR", "Gujarat (Surat, Ahmedabad)", "Tamil Nadu (Chennai)", "Karnataka (Bangalore)", "Kerala", "Punjab", "Haryana"],
        "bihar_up_dominance": "UP and Bihar together = HALF of all inter-state out-migration",
        "construction_workers_migrant": "15 million migrants in construction sector",
        "covid_trauma": "140 million migrants affected by COVID lockdowns. Mass reverse migration. Shramik trains.",
        "domestic_workers_delhi": "Largest category of female migrant workers in Delhi — from UP, Bihar, Jharkhand, Odisha",
    },

    "political_context": {
        "bjp_governance": "BJP under PM Modi since 2014. Hindu nationalist governance. Strong mandate 2024 elections (NDA coalition).",
        "caste_politics": "Caste is CENTRAL to Indian politics. OBC reservation (Mandal). SC/ST reservation. EWS reservation. Every election is a caste calculation.",
        "communal_tensions": "CAA-NRC fears for Muslims. Bulldozer politics — selective demolitions. Delhi 2020 riots. Muzaffarnagar 2013. Muslim agents: primary_fear often includes communal violence.",
        "farm_protests": "2020-21 farmer protests against farm laws — repealed. Punjab/Haryana farmer identity strong.",
        "unemployment_crisis": "Youth unemployment crisis. Agniveer (short-term military) protests. Government exam paper leaks.",
        "agent_generation_note": "Caste shapes occupation more than income/education/geography. Hindu upper caste: higher trust_government under BJP. Muslims/Dalits: LOW trust. OBC: variable. Never make caste EXPLICIT in bio — it shows through occupation, location, name, behavior. Political lean is inferred, never stated.",
    },

    # =========================================================================
    # SECTION 2: CASTE-OCCUPATION RULES (for agent generation)
    # =========================================================================

    "caste_occupation_rules": {
        "overview": "Caste determines what work a person does more than income, education, or geography. The system operates through thousands of jatis (sub-castes) with specific traditional occupations.",
        "brahmin_upper": "Modern: IAS/IPS, doctors, lawyers, academics, IT, corporate, media, judiciary. Women: doctors, teachers, lawyers, IT. Names: Sharma, Mishra, Tripathi, Dubey, Pandey (UP/Bihar), Iyer, Iyengar (Tamil), Bhat, Kaul (Kashmir), Mukherjee, Banerjee, Chatterjee (Bengali).",
        "kshatriya_rajput_jat": "Army officers, police, farming (large), real estate, transport. Rajput women VERY restricted (ghoonghat, honor culture). Names: Singh, Chauhan, Rathore, Rajput, Thakur.",
        "vaishya_bania_marwari": "Business empires. Retail, wholesale, gems, commodity trading, fintech. Women traditionally behind-scenes, now educated professionals. Names: Agarwal, Gupta, Mittal, Jain, Shah, Goenka, Bansal.",
        "obc_artisan_farming": "Weavers, potters, blacksmiths, barbers, farmers. Government jobs through 27% OBC quota. Names: Yadav, Kurmi, Koeri, Kumhar, Lohar, Nai, Teli, Ansari (Muslim OBC), Julaha.",
        "dalit_sc": "Manual scavenging (legally abolished but continues), leather work, sweeping, sanitation, cremation, bonded agricultural labor, brick kiln, construction. Government jobs through 15% SC quota. Names: varies by region — Chamar, Jatav, Valmiki, Paswan, Ram (surname in many Dalit communities), Ambedkar (adopted).",
        "adivasi_st": "Forest-dependent: shifting cultivation, tendu leaf, honey, forest produce. Mining displacement. Tea garden labor. Government through 7.5% ST quota. Names: Munda, Oraon, Santal, Gond, Bhil, Meena, Chakma.",
        "muslim": "VARIES by class. Ashraf (upper): doctors, lawyers, business. Pasmanda (backward): weavers (Ansari/Julaha), butchers (Qureshi), barbers (Nai), bidi rolling, chikan embroidery. Names: Khan, Ahmed, Sheikh, Ansari, Qureshi, Hussain, Siddiqui.",
        "sikh": "Farming, military, trucking, business. Names: Singh (male), Kaur (female) — universal Sikh surnames.",
        "christian": "Kerala: nurses, teachers, plantation, IT. Goa: tourism, hospitality. NE: government, military, education. Dalit Christian: face double discrimination. Names: Mathew, Thomas, George (Kerala), D'Souza, Fernandes (Goa), Lyngdoh, Jamir (NE).",
    },

    # =========================================================================
    # SECTION 3: STATE ZONE DYNAMICS
    # =========================================================================

    "state_zone_dynamics": {

        "uttar_pradesh": {
            "character": "Most populous state (240M). Caste most rigid. BJP strong (Yogi Adityanath). High poverty. Massive out-migration. 20% Muslim. Hindi heartland.",
            "women_work_norms": "VERY HIGH restriction. Ghoonghat (veil) among Hindu upper/middle castes. Purdah among Muslims. Poor Dalit women work from necessity. Chikan embroidery (Lucknow) acceptable home-based Muslim women's work.",
            "key_economies": "Agriculture, weaving (Varanasi Banarasi sarees), chikan (Lucknow), locks (Aligarh), brass (Moradabad), leather (Kanpur/Agra — Dalit), IT (Noida/Greater Noida), government.",
        },

        "bihar_jharkhand": {
            "character": "Bihar: among poorest states. Caste extremely rigid. Massive out-migration (11.7M post-COVID). Jharkhand: mineral-rich, underdeveloped, Adivasi, mining displacement, Naxal.",
            "women_work_norms": "VERY HIGH in Bihar. Purdah/ghunghat strong. Poor women: agricultural labor. Jharkhand: Adivasi women more active.",
            "key_economies": "Bihar: agriculture, migration-dependent remittance economy. Jharkhand: coal mining (Dhanbad/Bokaro), iron ore, mica (illegal — children/women).",
        },

        "maharashtra_mumbai": {
            "character": "Financial capital. Mumbai most diverse, most economically active for women. Bollywood. Dharavi — largest informal economy hub. Dalit political assertion (Ambedkar). Pune — IT.",
            "women_work_norms": "LOW TO MODERATE. Mumbai most permissive. Dalit women empowerment strong. Muslim women (Bhiwandi/Malegaon) in textiles.",
            "key_economies": "Finance, media, IT, Bollywood, Dharavi (leather, garments, recycling), Pune (IT, auto), Bhiwandi/Malegaon (textiles).",
        },

        "tamil_nadu_karnataka": {
            "character": "Dravidian political culture. Strong female labor participation (TN highest). IT hubs: Bangalore, Chennai. Self-Respect Movement legacy. Garments industry (Tirupur, Bangalore).",
            "women_work_norms": "LOWER THAN NORTH. Women visible in ALL sectors including transport. Garments employ large numbers of young women. BUT: sumangali system (bonded young Dalit women in textile mills — exploitative).",
            "key_economies": "IT (Bangalore, Chennai), garments (Tirupur, Bangalore), silk weaving (Kanchipuram), matchsticks (Sivakasi — hazardous), beedi rolling, auto manufacturing.",
        },

        "andhra_telangana": {
            "character": "Telangana: Hyderabad IT hub + rural agriculture. Andhra: coastal agriculture, shrimp, tobacco. Significant Dalit population.",
            "women_work_norms": "MODERATE. Hyderabad IT has significant female workforce. Rural: agriculture, tobacco processing, shrimp peeling.",
            "key_economies": "IT (Hyderabad), pharma (Hyderabad), rice, shrimp, tobacco (Guntur), chili, cotton.",
        },

        "kerala": {
            "character": "Highest literacy (96.2%). Communist tradition. Gulf remittance economy. Christians + Hindus + Muslims coexist. Matrilineal Nair community. Nurse export capital.",
            "women_work_norms": "LOWEST RESTRICTION IN INDIA. Women most educated. Kerala nurses globally famous. Muslim women MORE active than North Indian Muslim women. BUT: high local unemployment.",
            "key_economies": "Gulf remittances, healthcare (nurse export), tourism, IT (Technopark, Infopark), coir, cashew, rubber, spices.",
        },

        "punjab_haryana_delhi": {
            "character": "Punjab: Green Revolution, Sikh majority, agricultural mechanization, drug crisis. Haryana: Jat-dominant, manufacturing (Gurgaon), extreme patriarchy. Delhi NCR: most diverse, corporate, government, massive migrant destination.",
            "women_work_norms": "MODERATE TO HIGH. Jat community: extreme honor restrictions. Sikh women more active. Delhi: enormous range from elite professional to slum domestic worker.",
            "key_economies": "Delhi: government, corporate, services. Gurgaon: IT, consulting, finance. Noida: manufacturing, IT. Punjab: agriculture, dairy. Ludhiana: textiles, hosiery.",
        },

        "west_bengal_northeast": {
            "character": "Bengal: intellectual tradition, Kolkata declining industrial base, 27% Muslim. Northeast: 8 states, culturally distinct, matrilineal Khasi (Meghalaya), tribal identity movements.",
            "women_work_norms": "MODERATE in Bengal. NORTHEAST: women MOST economically active in India — Khasi women own property and run businesses.",
            "key_economies": "Kolkata: services, jute (declining), IT (growing). Tea (North Bengal, Assam). NE: agriculture, handloom, government, military.",
        },

        "rajasthan_gujarat": {
            "character": "Rajasthan: feudal Rajput culture, tourism, textiles, EXTREMELY restricted women (Rajput). Gujarat: business-focused, Jain/Marwari trading castes, diamond polishing (Surat).",
            "women_work_norms": "HIGHEST restriction in Rajasthan (Rajput ghoonghat, honor killing). Gujarat: moderate but conservative despite prosperity.",
            "key_economies": "Rajasthan: tourism, block printing, marble mining, agriculture. Gujarat: diamonds (Surat), textiles, petrochemical, dairy (Amul), salt pans (Kutch).",
        },

        "mp_chhattisgarh_odisha": {
            "character": "Large Adivasi populations. Underdeveloped. Mineral-rich. Naxal-affected (Chhattisgarh). MP: agriculture. Odisha: mining (Vedanta controversy), cyclone-vulnerable coast.",
            "women_work_norms": "Adivasi women less restricted. But poverty drives all work. Tendu leaf collection (tribal women, seasonal). NREGA major employer.",
            "key_economies": "Mining (coal, iron, bauxite, manganese), agriculture, forest produce, tendu leaf, NREGA.",
        },
    },

    # =========================================================================
    # SECTION 4: FEMALE OCCUPATIONS BY CATEGORY
    # =========================================================================

    "female_occupations": {

        "agricultural_rural": [
            "subsistence farmer — own small plot (most common invisible female occupation)",
            "unpaid family farm worker — LARGEST actual category but undercounted",
            "agricultural day wage laborer — transplanting, weeding, harvesting (Rs 150-300/day)",
            "NREGA worker (55% female participation — 100 days guaranteed — Rs 200-300/day)",
            "tea garden plucker (Assam, West Bengal, Kerala, Tamil Nadu — Adivasi women)",
            "sugarcane cutter (Maharashtra, Karnataka — migrant couples — extreme seasonal labor)",
            "cotton picker (Gujarat, Maharashtra, Rajasthan, Telangana — seasonal)",
            "tobacco leaf sorter and processor (Andhra — Guntur)",
            "sericulture — silk cocoon rearing (Karnataka — Ramanagara)",
            "salt pan worker (Gujarat Rann — Agariya community — extreme conditions)",
            "tendu leaf collector (MP, Chhattisgarh, Jharkhand — tribal women — seasonal)",
            "forest produce collector — honey, herbs, mahua (tribal women — central India)",
        ],

        "home_based_informal": [
            "bidi roller — hand-rolling tobacco (5+ million, majority women — Dalit and Muslim — Rs 80-150/1000 bidis)",
            "agarbatti (incense) roller — piece rate (Karnataka, Gujarat, Assam)",
            "papad maker — SHG production (Lijjat model — women's cooperative)",
            "chikan embroidery (Lucknow — Muslim women — very low piece rate)",
            "zari and sequin work (Bareilly, Varanasi — Muslim women)",
            "handloom saree weaver (Varanasi, Kanchipuram, Pochampally, Chanderi)",
            "block printing on fabric (Jaipur, Sanganer — women in stamping/dyeing)",
            "bandhani tie-dye (Gujarat, Rajasthan — home-based women's work)",
            "garments piece work — stitching, finishing (Delhi, Mumbai subcontracting chains)",
            "bangle making (Firozabad — glass — extremely hazardous — women and children)",
            "matchstick and firework making (Sivakasi, TN — hazardous — women and children)",
            "food processing — pickle, papad, masala grinding (SHG-supported enterprises)",
        ],

        "urban_working_class": [
            "domestic worker — maid, cook, nanny (LARGEST urban female occupation — 50+ million estimated)",
            "construction laborer — carrying head loads of bricks, cement, sand (migrant women)",
            "rag picker / waste sorter (Dalit women — informal recycling — health hazard)",
            "garments factory worker (Tirupur, Bangalore, Noida, Ludhiana — significant female workforce)",
            "ASHA health worker (community — Rs 2,000-8,000/month honorarium)",
            "anganwadi worker (ICDS — Rs 4,500-12,000/month)",
            "private school teacher (low pay — Rs 3,000-10,000/month — massive sector)",
            "call center agent / BPO worker (Delhi, Bangalore, Hyderabad — young women)",
            "beauty parlor worker and owner (female-only space)",
            "retail sales staff (malls, supermarkets — Big Bazaar, Reliance, D-Mart)",
            "vegetable and fruit vendor — street hawker",
            "flower seller — temple garlands, roadside",
        ],

        "middle_class_professional": [
            "government school teacher (stable, pensioned — high status)",
            "nurse — government hospital (GNM/BSc Nursing — Kerala nurses globally famous)",
            "staff nurse — private hospital (AIIMS, Fortis, Apollo, Max)",
            "bank clerk / officer (SBI, PNB, IBPS recruitment — competitive exam)",
            "LIC / insurance officer",
            "government administrative staff (through SSC, state PSC exams)",
            "NGO program officer",
            "microfinance field officer (Bandhan, Ujjivan, SKS)",
            "self help group federation leader (NRLM)",
            "journalist — regional media",
            "police sub-inspector / constable (growing female intake)",
            "railway clerk / ticket collector (Indian Railways — massive employer)",
        ],

        "corporate_elite_professional": [
            "doctor — MBBS, MD, specialist",
            "software engineer / IT professional (TCS, Infosys, Wipro, HCL, startups, MNCs)",
            "corporate manager — HR, marketing, finance, consulting",
            "chartered accountant (CA)",
            "lawyer / advocate (district courts, high courts, Supreme Court)",
            "IAS / IPS / IFS officer (UPSC — most prestigious)",
            "university professor (UGC-NET + PhD)",
            "media professional — TV anchor, senior editor",
            "architect", "fashion designer (NIFT graduates)",
            "startup founder (Bangalore, Delhi ecosystem)",
            "airline pilot / flight attendant",
        ],

        "migrant_abroad": [
            "nurse (Gulf, UK, USA, Australia, Canada — Kerala dominant — professional migration)",
            "domestic worker (Gulf — Saudi, UAE, Kuwait — lower-class women)",
            "IT professional (USA, UK, Canada — H1B/H4)",
            "doctor (UK NHS, USA — skilled migration)",
            "care worker (elderly care — Israel program — Kerala women)",
        ],
    },

    # =========================================================================
    # SECTION 5: MALE OCCUPATIONS BY CATEGORY
    # =========================================================================

    "male_occupations": {

        "agricultural": [
            "farmer — own land (marginal <1ha, small 1-2ha, medium/large >2ha — size determines everything)",
            "agricultural day laborer",
            "NREGA worker (45% male)",
            "cattle and dairy farmer (commercial — milk cooperative)",
            "fisherman — freshwater and marine",
            "tea garden worker (Assam, North Bengal — Adivasi)",
            "sugarcane cutter (Maharashtra, Karnataka — seasonal migrant — extreme labor)",
            "toddy tapper (Kerala, TN — Ezhava/Nadar community — climbing palms)",
        ],

        "transport_logistics": [
            "auto-rickshaw driver (every Indian city)",
            "e-rickshaw / battery rickshaw driver (rapidly growing)",
            "taxi driver — Ola, Uber, Rapido (gig platform)",
            "bus driver — state transport and private",
            "truck driver — long haul interstate (millions — Sikh truckers dominant in North)",
            "delivery rider — Swiggy, Zomato, Blinkit, Zepto, Amazon (gig — millions)",
            "porter — railway station (red uniformed — declining)",
            "tempo / Tata Ace driver (small goods transport)",
        ],

        "construction_labor": [
            "construction mason — mistri (skilled — bricklayer, plasterer)",
            "construction helper — unskilled carrying work (migrant labor — lowest rung)",
            "rod binder / steel fixer (rebar — semi-skilled)",
            "plumber (growing demand with urbanization)",
            "painter (interior/exterior — seasonal)",
            "electrician — house wiring, industrial",
            "brick kiln worker (Dalit and Adivasi — seasonal — bonded labor documented)",
            "stone quarry worker (hazardous — silicosis risk)",
        ],

        "skilled_trades": [
            "welder and fabricator — steel, iron, aluminum",
            "carpenter and furniture maker (traditional caste: Vishwakarma/Sutar)",
            "goldsmith and jewelry maker (traditional caste: Sonar/Swarnakar)",
            "tailor — men's clothing",
            "mobile phone repair (massive informal sector)",
            "motorcycle and scooter mechanic",
            "AC technician and installer (growing with urbanization)",
            "diamond polisher (Surat — primarily Patel community men)",
            "handloom weaver (Varanasi, Pochampally — traditional caste: Julaha/Ansari/Padmashali)",
            "barber / hair stylist (traditional caste: Nai)",
        ],

        "trade_commerce": [
            "kirana (grocery) shop owner (every neighborhood — typically Bania/Marwari/local trading caste)",
            "chai (tea) stall owner (ubiquitous — male social hub)",
            "street food vendor — samosa, chaat, pani puri, vada pav, dosa",
            "wholesale trader — grains, vegetables, fruits (mandi system)",
            "cloth and textile merchant (traditional trading caste)",
            "mobile phone and accessories shop",
            "medical store / pharmacy (often without pharmacist qualification)",
            "scrap dealer — kabadiwala (recycling — informal economy)",
            "real estate broker — dalal",
        ],

        "urban_services": [
            "security guard — building, mall, office, factory (often retired military or poor rural men)",
            "hotel and restaurant cook, kitchen staff, waiter",
            "office peon / attender",
            "municipal sweeper (stigmatized — Dalit community — sanitation work)",
            "hospital ward boy / orderly",
            "dhaba (roadside restaurant) owner and cook",
            "barber shop owner (traditional Nai caste — modernizing to 'salon')",
            "salesperson — retail (electronics, clothing, hardware)",
            "watchman / chowkidar (night security)",
        ],

        "middle_professional": [
            "government officer — IAS/IPS/IFS (UPSC — highest prestige. Through competitive exam.)",
            "government officer — state civil service (state PSC exam)",
            "police sub-inspector, inspector",
            "army officer and jawan (large recruitment from UP, Bihar, Punjab, Rajasthan, Haryana)",
            "teacher — government school/college (competitive exam — stable, pensioned)",
            "bank officer (SBI, PNB, IBPS — competitive exam entry)",
            "journalist and reporter (regional media — Hindi, Tamil, Telugu, Bengali, Marathi)",
            "court lawyer — junior to mid-level advocate",
            "doctor — community health center / primary health center",
            "engineer — government (PWD, railways, irrigation)",
            "railway employee (Indian Railways — largest civilian employer — 1.2 million)",
        ],

        "corporate_elite": [
            "software engineer — IT (TCS, Infosys, Wipro, HCL, startups, MNCs, FAANG)",
            "corporate executive — manager to VP to director",
            "doctor — senior consultant, department head (AIIMS, Apollo, Fortis, Max)",
            "investment banker (Mumbai — Dalal Street)",
            "chartered accountant (CA) — Big Four, industry",
            "lawyer — high court and supreme court advocate",
            "university professor / IIT-IIM faculty",
            "startup founder (Bangalore, Delhi, Mumbai ecosystem)",
            "real estate developer",
        ],

        "migrant_abroad": [
            "construction laborer — Gulf (Saudi, UAE, Qatar, Kuwait — largest category)",
            "domestic driver — Gulf",
            "IT professional (USA, UK, Canada, Australia — H1B)",
            "doctor (UK NHS, USA, Australia — skilled migration)",
            "truck driver — Gulf",
            "restaurant/hotel worker — Gulf, Europe",
            "nurse — male (growing — Gulf, UK)",
            "seafarer / merchant navy (Goa, Kerala, Mumbai tradition)",
        ],
    },

    # =========================================================================
    # SECTION 6: GENDER-OCCUPATION CONSTRAINTS
    # =========================================================================

    "gender_occupation_rules": {
        "universal": [
            "A woman's occupation MUST be plausible for her state, caste, religion, and family situation.",
            "Domestic work is done by MIGRANT women from poorer states (UP, Bihar, Jharkhand, Odisha) — NOT local middle-class women.",
            "ASHA and Anganwadi workers are a MASSIVE legitimate female occupation — generate them for rural/semi-urban women.",
            "Bidi rolling employs 5+ million workers (majority women — Dalit and Muslim). Major home-based occupation.",
            "Rajput/Jat women in Rajasthan/Haryana face extreme honor-based restrictions. DO NOT assign them garments/factory work.",
            "Dalit women face triple discrimination (caste+class+gender). They do manual scavenging, brick kiln, construction carrying.",
            "Kerala women are MOST educated and empowered — nurses, teachers, professionals. Muslim women in Kerala MORE active than North Indian Muslim women.",
            "Garments work is acceptable for women in Tamil Nadu, Karnataka, but carries some stigma in conservative North India.",
            "Caste should be inferred from name, occupation, location — NEVER stated explicitly in bio or persona.",
        ],
        "male_only_occupations": [
            "truck driver", "auto-rickshaw driver", "bus driver", "rickshaw puller",
            "construction mason", "toddy tapper", "diamond polisher (Surat)",
            "imam", "temple priest (pujari)", "cremation ground worker (Dom)",
            "waiter in most restaurants (South India has more female servers than North)",
        ],
        "female_dominated_occupations": [
            "domestic worker", "ASHA health worker", "anganwadi worker",
            "tea garden plucker", "bidi roller", "garments sewing operator",
            "beauty parlor worker", "nurse", "chikan embroidery worker",
        ],
    },

    # =========================================================================
    # SECTION 7: FALLBACK NAME POOLS — AUTHENTIC BY COMMUNITY
    # =========================================================================

    "name_pools": {
        "hindu_upper_caste_male": [
            "Rajesh Sharma", "Amit Mishra", "Sunil Pandey", "Vivek Tripathi",
            "Manish Tiwari", "Arun Dubey", "Pradeep Shukla", "Sanjay Joshi",
            "Deepak Bhat", "Rohit Kaul", "Anand Iyer", "Suresh Rao",
        ],
        "hindu_upper_caste_female": [
            "Priya Sharma", "Anita Mishra", "Neha Pandey", "Sunita Tripathi",
            "Pooja Shukla", "Kavita Joshi", "Swati Iyer", "Meera Rao",
        ],
        "obc_male": [
            "Rajesh Yadav", "Ramesh Kurmi", "Vinod Kumhar", "Suresh Lohar",
            "Ashok Teli", "Dinesh Nai", "Manoj Koeri", "Pankaj Gujar",
            "Raju Vishwakarma", "Pramod Gadaria",
        ],
        "obc_female": [
            "Sunita Yadav", "Meena Kumhar", "Lata Kurmi", "Geeta Teli",
            "Pushpa Nai", "Radha Koeri", "Suman Vishwakarma", "Asha Gujar",
        ],
        "dalit_male": [
            "Ramesh Jatav", "Sunil Paswan", "Ashok Valmiki", "Raju Ram",
            "Deepak Chamar", "Mohan Dhobi", "Santosh Musahar", "Ajay Mahar",
            "Ganesh Mala", "Suresh Paraiyar",
        ],
        "dalit_female": [
            "Laxmi Jatav", "Sushila Paswan", "Kamla Valmiki", "Phoolmati Ram",
            "Rani Devi", "Savitri Mahar", "Anita Chamar", "Guddi Musahar",
        ],
        "adivasi_male": [
            "Suman Munda", "Birsa Oraon", "Lakhan Santal", "Mangal Gond",
            "Raju Bhil", "Kishore Meena", "Deepak Ho", "Sunil Baiga",
        ],
        "adivasi_female": [
            "Phulmoni Munda", "Sunita Oraon", "Malti Santal", "Kamla Gond",
            "Radha Bhil", "Lata Meena", "Savitri Baiga",
        ],
        "muslim_male": [
            "Mohammed Ansari", "Salim Sheikh", "Irfan Khan", "Rashid Ahmed",
            "Asif Qureshi", "Zaheer Hussain", "Shakeel Siddiqui", "Nadeem Malik",
            "Imran Pathan", "Wasim Akram", "Farhan Mirza", "Aamir Javed",
        ],
        "muslim_female": [
            "Fatima Ansari", "Nazia Sheikh", "Shabana Khan", "Rukhsar Ahmed",
            "Nasreen Begum", "Sakina Bibi", "Zeenat Parveen", "Ayesha Qureshi",
            "Rehana Khatoon", "Mumtaz Jahan",
        ],
        "sikh_male": [
            "Gurpreet Singh", "Harjinder Singh", "Manpreet Singh", "Balwinder Singh",
            "Jaswant Singh", "Kuldeep Singh", "Amarjeet Singh", "Sukhwinder Singh",
        ],
        "sikh_female": [
            "Harpreet Kaur", "Manpreet Kaur", "Jaspreet Kaur", "Gurleen Kaur",
            "Amandeep Kaur", "Rajwinder Kaur",
        ],
        "christian_male": [
            "Mathew Thomas", "George Kurian", "Joseph Varghese", "Anthony D'Souza",
            "David Fernandes", "Samuel Tirkey", "John Lyngdoh",
        ],
        "christian_female": [
            "Mary Thomas", "Susan Kurian", "Elizabeth Varghese", "Priscilla D'Souza",
            "Grace Fernandes", "Ruth Tirkey", "Martha Lyngdoh",
        ],
    },
}


# =============================================================================
# PAKISTAN OCCUPATIONAL REALITY SYSTEM
# Source: PBS LFS 2024-25 (19th ICLS), SBP remittance data, BEOE,
#         IOM Pakistan, HRCP, CSJ, International Crisis Group
# =============================================================================

PAKISTAN_OCCUPATIONAL_REALITY: Dict[str, Any] = {

    # =========================================================================
    # SECTION 1: MACRO LABOR FACTS
    # =========================================================================

    "macro_labor_facts": {
        "population": "approximately 240-252 million (Census 2023 — contested)",
        "working_age_population": "179.6 million (LFS 2024-25)",
        "lfpr": "47.7% (2024-25) — NOTE: shifted to 19th ICLS framework excluding subsistence agriculture",
        "male_lfpr": "69.8%",
        "female_lfpr": "24.4% — among LOWEST globally but slowly rising",
        "unemployment_rate": "6.9% (up from 6.3%)",
        "informal_sector": "72.1% of non-agricultural employment is informal. Rural: 75.5%. Urban: 68.3%.",
        "unpaid_domestic_care": "117.4 million engaged in unpaid domestic/care work. 66.7 million female (77.1% of all women).",
        "agriculture_share": "approximately 37-39% of employment",
        "textiles": "Textile sector is manufacturing backbone — but male-dominated factory floors UNLIKE Bangladesh",
        "it_exports": "$3.8 billion in FY2024-25 (record — 18% increase). Lahore, Karachi, Islamabad hubs.",
        "youth_bulge": "Nearly 40% under 15. 18%+ aged 15-24. Massive demographic wave entering labor market.",
    },

    "migration_remittance_facts": {
        "remittance_fy2025": "$38.3 billion — ALL-TIME RECORD (26.6% increase over FY24)",
        "remittance_share_gdp": "approximately 8-10% of GDP — CRITICAL macroeconomic stabilizer",
        "top_source_saudi": "$9.34 billion from Saudi Arabia — single largest",
        "top_source_uae": "$7.83 billion from UAE",
        "top_source_uk": "$5.99 billion from UK — Mirpuri/Kashmiri-origin diaspora",
        "top_source_usa": "$3.72 billion from USA",
        "total_overseas_pakistanis": "approximately 9-11 million",
        "saudi_worker_dominance": "50%+ of registered overseas workers go to Saudi Arabia",
        "brain_drain": "Post-2022 crisis = massive brain drain. Young educated professionals leaving for Canada, UK, Australia, Gulf. Over 2 million sought employment abroad.",
        "uk_diaspora": "Established community — majority from Mirpur (AJK) and Punjab. Restaurant sector. NHS workers. Taxi drivers. Second/third generation now professional class.",
    },

    "political_crisis_2022_2026": {
        "overview": "Pakistan in continuous political crisis since April 2022 — fundamental rupture in civilian-military power balance.",
        "imran_khan": "Imran Khan (PTI) removed via no-confidence motion April 2022. Arrested May 2023. In jail since August 2023. Sentenced to 14+ years. 186+ legal cases. Supporters view ALL cases as politically motivated. 57% approval despite imprisonment.",
        "may_9_2023": "Khan supporters attacked military installations. Military crackdown: thousands arrested. PTI leadership jailed/exiled. Party stripped of election symbol.",
        "february_2024_election": "PTI-backed independents won most seats despite obstruction. Election widely considered rigged. Coalition government (PML-N + PPP) formed despite losing popular vote.",
        "november_2024_protest": "PTI march on Islamabad. Military deployed. Internet shut down. At least 12 killed.",
        "economic_crisis": "IMF bailout ($7 billion). Inflation peaked above 35% (2023). Electricity prices doubled. Gas shortages. GDP growth minimal.",
        "agent_generation_note": "Political identity in Pakistan is EXPLOSIVE and DANGEROUS. PTI supporters face arrest, torture, disappearance. Generate with: political_identity = 'hidden' for MOST agents. PTI supporters: high digital presence, very low trust_government, very low trust_military. PML-N/PPP: pragmatic, older, establishment-aligned. EVERYONE has an opinion on Imran Khan — single most polarizing topic.",
    },

    # =========================================================================
    # SECTION 2: SECTARIAN/ETHNIC IDENTITY (shapes occupation access)
    # =========================================================================

    "sectarian_ethnic_rules": {
        "sunni_majority": "Barelvi (majority — Sufi/shrine, TLP party) and Deobandi (JUI-F, Taliban-linked ideology). Shapes madrasa type, political allegiance.",
        "shia_15_20_percent": "Targeted by sectarian violence. Hazara Shia in Quetta visibly identifiable and confined to Hazara Town for safety. trust_government: NEAR ZERO for Hazara.",
        "ahmadi_persecuted": "Declared non-Muslim by constitution. Criminalized for Islamic practices. 6 murdered for faith in 2024. Cannot reveal identity publicly. trust_government: ZERO. Hidden identity ALWAYS.",
        "christian_2_3_percent": "Associated with sanitation work (caste-linked even post-conversion). Brick kiln bonded labor disproportionate. Forced conversion of girls documented. Jaranwala 2023 — 21 churches burned.",
        "hindu_1_6_percent": "Concentrated in Sindh (Tharparkar). Lower-caste: feudal agricultural bonded labor. Upper-caste Karachi: traders. Forced conversion of girls = primary fear.",
        "pashtun": "Pashtunwali honor code. MOST restricted women (KP/FATA). Bazaars = male-only. Women in full burqa. PTM human rights movement faces military repression.",
        "baloch": "Tribal sardari system. Separatist insurgency. Enforced disappearances. EXTREME institutional distrust. Women virtually invisible in public.",
        "mohajir": "Urdu-speaking partition migrants. Karachi/Hyderabad. Most educated/urban. MQM politics. Women MORE economically active than most communities.",
        "punjabi_biradari": "Biradari (clan) system: Jat (farming — dominant), Rajput, Arain, Gujjar, Butt (Kashmiri), Sheikh (business), Chaudhry, Malik. Occupational castes: Lohar, Tarkhan, Mochi, Mussalli/Chuhra (sanitation — largely Christian).",
        "sindhi_feudal": "Interior Sindh = feudal waderas. Haris (peasants) bonded. Women = property. Karo-kari (honor killing). PPP dynasty politics.",
    },

    # =========================================================================
    # SECTION 3: PROVINCIAL ZONE DYNAMICS
    # =========================================================================

    "provincial_zones": {

        "punjab_north": {
            "character": "Lahore (cultural capital — LUMS, GCU, food, arts), Islamabad (federal capital, military HQ), Rawalpindi (cantonment), Faisalabad (textile hub), Sialkot (sports goods, surgical instruments), Gujranwala (cutlery, fans).",
            "women_work_norms": "MODERATE in cities. Professional women (doctors, teachers, bankers) accepted. Factory work stigmatized. Class paradox: poor women work (necessity > shame), middle-class MOST restricted (status signal), elite women work as professionals (above judgment). Home-based work (stitching, food business) completely acceptable.",
            "key_economies": "Textiles (Faisalabad), sports goods (Sialkot), surgical instruments (Sialkot), agriculture (wheat, rice, sugarcane), IT (Lahore), government/military (Islamabad/Rawalpindi), real estate (DHA, Bahria Town).",
        },

        "punjab_south_seraiki": {
            "character": "Multan, Bahawalpur, DG Khan, Rahim Yar Khan, Rajanpur. Feudal. Extreme poverty. Cotton agriculture. Brick kilns. Seraiki language. Sufi shrines. PPP/independents.",
            "women_work_norms": "EXTREME restriction in feudal areas. Poor women DO work agriculture (cotton picking — seasonal — women and children) but formal work: unthinkable. Brick kiln bonded labor traps entire families including women.",
        },

        "sindh_karachi": {
            "character": "Karachi (20+ million — economic engine, most diverse city: Mohajir, Pashtun, Sindhi, Baloch, Punjabi, Bengali). Financial hub. Media hub. Port city. Different planet from interior Sindh.",
            "women_work_norms": "LOWER restriction than rest of Pakistan. Mohajir women most educated and economically active. Professional work accepted. Largest professional female workforce in Pakistan. BUT: Pashtun community maintains KP-level restrictions.",
        },

        "sindh_interior": {
            "character": "Feudal heartland. PPP dynasty. Sufi shrine culture. Hindu minority (Tharparkar). Extreme poverty. 2022 floods: one-third of Pakistan underwater, Sindh worst hit. Recovery incomplete.",
            "women_work_norms": "EXTREME under feudal system. Women = property. Karo-kari documented. Hindu/Christian women face forced conversion. Agricultural work but under feudal/bonded conditions.",
        },

        "kp_peshawar": {
            "character": "Pashtun majority. PTI stronghold. Post-conflict (FATA merger 2018). TTP attacks continue. Afghan refugees. Conservative Islamic culture. Pashtunwali honor code.",
            "women_work_norms": "VERY HIGH restriction. Acceptable: female doctor (female ward ONLY), female teacher (girls school ONLY), lady health worker. Home-based embroidery acceptable. Bazaars = male-only. Women in full burqa when visible. Merged districts (ex-FATA): women virtually never leave home compound.",
        },

        "balochistan": {
            "character": "Largest province, smallest population. Quetta. Tribal sardari system. Mining (coal, copper). CPEC/Gwadar. Baloch separatist insurgency. Hazara Shia under siege. Most underdeveloped.",
            "women_work_norms": "EXTREME. Tribal honor culture. Women almost invisible in public. Exception: Hazara Shia women in Quetta more educated. Some Baloch women in education (growing from very low base).",
        },

        "gb_ajk": {
            "character": "GB: mountainous, Shia/Ismaili majority. Tourism (Hunza, Skardu). CPEC corridor. AJK: disputed territory. Mirpuri community is UK diaspora source.",
            "women_work_norms": "GB Ismaili women (Hunza): MORE active and educated (Aga Khan network). AJK: remittance family dynamics — husband in UK, wife manages at home.",
        },
    },

    # =========================================================================
    # SECTION 4: FEMALE OCCUPATIONS
    # =========================================================================

    "female_occupations": {

        "universally_acceptable": [
            "home-based embroidery and stitching — phulkari (Punjab), mirror work (Sindh), Balochi embroidery",
            "home-based tailoring — stitching shalwar kameez",
            "home-based food business — catering, baking, cooking for events (social media driven)",
            "livestock management at home — goats, cattle, buffalo, poultry (rural — not counted as 'work')",
            "female doctor — treating female patients (HIGH demand — social necessity)",
            "female teacher — girls-only school (most acceptable formal employment)",
            "lady health worker (LHW — government — 100,000+ women — Rs 15,000-25,000/month)",
            "beauty parlor worker and owner (female-only space)",
        ],

        "acceptable_in_cities": [
            "private school teacher (massive sector — 50,000+ private schools in Punjab alone — Rs 8,000-25,000/month)",
            "nurse (growing — was stigmatized, now more acceptable)",
            "bank teller and officer (HBL, UBL, MCB, Meezan Islamic Bank)",
            "call center agent (Lahore, Karachi)",
            "corporate professional (MNCs, telecom — Telenor, Jazz, Ufone)",
            "government clerk (through NTS/CSS/PMS)",
            "NGO worker (with family permission)",
            "journalist and media (minority but visible — faces threats)",
            "IT freelancer (graphic design, content, web — Pakistan 4th largest freelancer country)",
            "pharmacist (licensed — growing)",
            "university lecturer (through HEC)",
            "lawyer (growing female bar — Karachi, Lahore, Islamabad)",
        ],

        "done_by_poorest_with_stigma": [
            "domestic helper — maid, cook, cleaner (lowest class — rural or Christian community)",
            "brick kiln worker (bonded labor — south Punjab, Sindh — Christian, Hindu families)",
            "agricultural day laborer (cotton picking — women and children — extreme conditions)",
            "factory worker (textiles — Karachi, Faisalabad — stigmatized for women unlike in BD)",
            "waste picker (Karachi — extreme poverty — Christian or Afghan women)",
        ],

        "migrant_abroad": [
            "domestic worker (Saudi Arabia, UAE, Kuwait — growing despite social resistance)",
            "nurse (Gulf countries — professional migration)",
            "doctor (UK NHS — significant Pakistani female doctor representation)",
            "IT professional (UK, Canada, UAE — skilled migration)",
        ],
    },

    # =========================================================================
    # SECTION 5: MALE OCCUPATIONS
    # =========================================================================

    "male_occupations": {

        "agricultural": [
            "wheat farmer (Punjab — rabi crop)", "cotton farmer (Punjab, Sindh — kharif)",
            "rice farmer (Punjab, Sindh — basmati and IRRI)", "sugarcane farmer (linked to sugar mills)",
            "mango and citrus orchardist (Multan, Sargodha)",
            "livestock herder (Balochistan, KP — pastoral)", "dairy farmer (Punjab — buffalo milk)",
            "agricultural day laborer (mazoor/hari — on landlord's land — often bonded in Sindh)",
            "fisherman (Sindh coast, Makran coast)", "date farmer (Balochistan — Turbat, Panjgur)",
        ],

        "transport_logistics": [
            "truck driver (legendary — decorated trucks — Swat, Jhelum origin traditionally — long-haul N-5 highway)",
            "bus and wagon driver (intercity and local)", "auto-rickshaw driver (CNG — every city)",
            "chingchi driver (modified motorcycle-rickshaw)", "ride-hailing driver (Careem, inDriver)",
            "motorcycle delivery rider (foodpanda, Bykea, Cheetay — gig economy)",
            "donkey cart driver (rural — goods transport)", "cargo loader and unloader (Karachi port, mandis)",
        ],

        "construction_trades": [
            "construction mason — mistri (skilled)", "construction laborer — mazdoor (unskilled)",
            "rod binder (rebar — semi-skilled)", "painter", "tile fixer", "marble worker",
            "brick kiln furnace worker (hazardous)", "electrician", "plumber",
            "AC technician (growing — extreme summer heat)", "welder and fabricator",
            "auto mechanic (motorcycle, car, truck)", "mobile phone repair",
        ],

        "commerce_trade": [
            "general store owner — kiryana (most ubiquitous small business)",
            "medical store / pharmacy (often without pharmacist license — 'compounder')",
            "cloth and textile merchant (Lahore Azam Market, Karachi Bolton Market)",
            "wholesale trader — grains, vegetables (mandi system — arhtiya commission agents)",
            "gold and jewelry shop", "mobile phone and accessories shop",
            "property dealer (real estate — DHA, Bahria Town)", "fertilizer and seed dealer (rural)",
            "money changer / hawala operator (sarafa bazaar)", "scrap dealer",
        ],

        "professional_government": [
            "CSS officer (Pakistan Administrative/Police/Foreign Service — most prestigious civilian career)",
            "army officer (PMA Kakul — significant social status and economic security)",
            "army soldier / jawan / NCO (large recruitment — Punjab, KP, Balochistan)",
            "police officer (provincial forces — politically controlled)", "doctor (government hospital)",
            "engineer (government — PWD, NHA, WAPDA)", "university professor (HEC)",
            "government teacher (through NTS)", "bank officer (State Bank, commercial banks)",
        ],

        "corporate_professional": [
            "software developer / IT professional (Lahore, Karachi, Islamabad — 10Pearls, Systems Ltd, Netsol)",
            "corporate executive (Unilever Pakistan, Engro, Lucky Group, Nestle, Telenor, Jazz)",
            "chartered accountant (ICAP)", "lawyer (district court to Supreme Court)",
            "doctor (private hospital — Aga Khan, Shifa, South City)", "media professional (TV anchor — Geo, ARY, Hum)",
            "startup founder (Lahore, Karachi — nascent ecosystem)",
        ],

        "migrant_abroad": [
            "construction worker (Saudi Arabia, UAE, Qatar, Kuwait, Oman — LARGEST category)",
            "driver (Gulf — household, taxi, truck)", "factory worker (Saudi, Malaysia, UAE)",
            "security guard (UAE, Qatar — malls, hotels)", "restaurant/hotel worker (Gulf, UK)",
            "taxi driver (UK — London — Pakistani/Mirpuri community)",
            "IT professional (UK, USA, Canada, Germany, UAE — skilled migration — growing rapidly)",
            "doctor and nurse (UK NHS — significant Pakistani medical community)",
            "student-worker (Canada, Australia, UK — studying + working part-time — massive recent trend)",
        ],

        "religious_sector": [
            "mosque imam (every neighborhood — Friday sermon, daily prayers, community disputes)",
            "madrasa teacher — maulvi, maulana (qawmi/alia systems — millions of students)",
            "Quran teacher — hafiz program (memorization)", "pir / shrine custodian (Sufi tradition — political power)",
        ],
    },

    # =========================================================================
    # SECTION 6: GENDER-OCCUPATION CONSTRAINTS
    # =========================================================================

    "gender_occupation_rules": {
        "universal": [
            "A woman's occupation MUST be plausible for her province, ethnicity, sect, and class.",
            "Factory work for women is STIGMATIZED in Pakistan — unlike Bangladesh where garments are normalized.",
            "Home-based work (stitching, embroidery, food business) is UNIVERSALLY acceptable across all regions.",
            "Domestic work is done by poorest women — often Christian or rural migrant. Extreme stigma.",
            "KP/FATA: women work only as female doctor (female ward), female teacher (girls school), LHW, or home-based.",
            "Karachi Mohajir women: MOST economically active. Professional work normalized.",
            "Balochistan tribal: women virtually invisible in public sphere except Hazara Shia community.",
            "South Punjab/Interior Sindh: feudal control. Poor women work cotton/agriculture but under bonded conditions.",
            "Brick kiln bonded labor traps entire families — Christian and Hindu disproportionately affected.",
        ],
        "male_only_occupations": [
            "truck driver", "bus driver", "auto-rickshaw driver", "chingchi driver",
            "construction mason", "brick kiln furnace worker", "welder",
            "imam", "madrasa teacher", "pir/shrine custodian",
            "waiter (almost all Pakistani restaurants male-staffed)",
            "bazaar shopkeeper (in KP/FATA/Balochistan — bazaars are male-only spaces)",
        ],
        "female_dominated_occupations": [
            "lady health worker (LHW)", "beauty parlor worker",
            "home-based embroidery/stitching", "private school teacher (primary — low pay)",
            "domestic helper", "cotton picker (seasonal — with children)",
        ],
    },

    # =========================================================================
    # SECTION 7: FALLBACK NAME POOLS
    # =========================================================================

    "name_pools": {
        "muslim_punjabi_male": [
            "Muhammad Aslam", "Imran Butt", "Zubair Ahmed", "Kashif Ali",
            "Naveed Iqbal", "Waseem Akram", "Tariq Mehmood", "Shoaib Malik",
            "Aamir Javed", "Shahzad Awan", "Riaz Chaudhry", "Saeed Gujjar",
            "Faisal Rajput", "Umar Farooq", "Bilal Sheikh", "Nadeem Arain",
        ],
        "muslim_punjabi_female": [
            "Ayesha Malik", "Fatima Butt", "Sadia Chaudhry", "Rabia Awan",
            "Nadia Iqbal", "Samina Javed", "Uzma Rajput", "Tahira Begum",
            "Kiran Sheikh", "Bushra Gujjar", "Asma Arain", "Hina Mehmood",
        ],
        "pashtun_male": [
            "Gul Khan", "Noor Muhammad", "Zahir Shah", "Wazir Ali",
            "Bakhtiar Yousafzai", "Fazal Rahman", "Sher Afzal", "Hameed Afridi",
            "Usman Khattak", "Samiullah Wazir", "Khalid Durrani", "Amir Zaman",
        ],
        "pashtun_female": [
            "Gulalai Bibi", "Nazia Khan", "Zarmina Khatoon", "Farida Begum",
            "Samina Yousafzai", "Bibi Hajra", "Reshma Bibi", "Nooria Khattak",
        ],
        "sindhi_male": [
            "Shah Nawaz Jatoi", "Ali Raza Soomro", "Ghulam Mustafa Chandio",
            "Sikandar Brohi", "Dodo Bheel", "Nabi Bux Laghari", "Hafeez Shaikh",
            "Mumtaz Bhutto",
        ],
        "sindhi_female": [
            "Marvi Laghari", "Sassui Chandio", "Zulaikha Soomro", "Noor Bibi Jatoi",
            "Haseena Brohi", "Sakina Bheel",
        ],
        "baloch_male": [
            "Mir Hazar", "Nawab Khan Bugti", "Akbar Mengal", "Wahid Baloch",
            "Dost Muhammad", "Ghulam Qadir", "Sajjad Raisani",
        ],
        "baloch_female": [
            "Bibi Zainab", "Mama Qadeer", "Nargis Baloch", "Sammi Baloch",
        ],
        "mohajir_male": [
            "Farhan Siddiqui", "Aamir Ansari", "Rehan Hashmi",
            "Zafar Ahmed", "Nadeem Rizvi", "Irfan Baig", "Danish Qureshi",
        ],
        "mohajir_female": [
            "Saba Siddiqui", "Nadia Hashmi", "Lubna Rizvi",
            "Huma Ansari", "Farah Baig", "Mehwish Qureshi",
        ],
        "christian_male": [
            "Patras Masih", "Yousaf Gill", "Emmanuel Bhatti",
            "Akash Samuel", "Sunny Masih", "Sadiq Barkat",
        ],
        "christian_female": [
            "Shamim Bibi", "Neelam Masih", "Razia Gill",
            "Sabrina Bhatti", "Mariam Samuel",
        ],
        "hindu_male": [
            "Rana Bheel", "Mohan Meghwar", "Vijay Kolhi",
            "Sanjay Bheel", "Ramesh Menghwar",
        ],
        "hindu_female": [
            "Radha Bheel", "Parvati Kolhi", "Lata Meghwar",
            "Champa Bheel",
        ],
        "hazara_male": [
            "Ali Raza Hazara", "Hassan Changezi", "Qadir Sarwari",
            "Abbas Hussain", "Sajjad Ali",
        ],
        "hazara_female": [
            "Fatima Changezi", "Sakina Hazara", "Zainab Hussain",
        ],
    },
}


# =============================================================================
# SRI LANKA OCCUPATIONAL REALITY SYSTEM
# Source: DCS LFS 2024-25, World Bank Sri Lanka Dev Update 2025,
#         ICG, ILO plantation reports, Progressive International,
#         Thomson Reuters Foundation, field-level ethnic-economic data
# =============================================================================

SRI_LANKA_OCCUPATIONAL_REALITY: Dict[str, Any] = {

    # =========================================================================
    # SECTION 1: MACRO LABOR + CRISIS FACTS
    # =========================================================================

    "macro_labor_facts": {
        "population": "approximately 22 million",
        "economically_active": "8.4 million (LFPR 47.7% Q4 2024)",
        "male_lfpr": "67.6% (Q4 2024)",
        "female_lfpr": "30.3% (Q4 2024) — historically low, barely budging",
        "unemployment_rate": "4.2% (Q4 2024). Youth 15-24: 19.8% — one in five jobless",
        "educated_unemployment": "7.1% among A/L or higher. PARADOX: more education = higher unemployment for women (10% vs 4.7% men)",
        "sector_services": "47.6% of employed (largest)",
        "sector_agriculture": "26.8% (declining)",
        "sector_industry": "25.7% (includes garments)",
        "self_employed": "Approximately 42.7% — dominant employment status",
        "informal": "Contributing family labor 62% in agriculture — markers of informal, vulnerable employment",
        "poverty_rate": "24.5% below $3.65/day — TWICE the 2019 level",
        "food_insecurity": "6.3 million skipping meals. 65,600 experiencing severe food shortages.",
        "real_wages": "Still BELOW 2019 levels despite recovery",
    },

    "economic_crisis_2022": {
        "overview": "Worst crisis since independence 1948. Sovereign default April 2022. GDP contracted 9.5% cumulatively. 13-hour power cuts. Fuel/food/medicine shortages. Inflation peaked 69.8%.",
        "aragalaya": "Mass protests (Aragalaya = 'Struggle') — cross-ethnic unity. Protesters occupied President's house July 2022. Gotabaya Rajapaksa fled. Rajapaksa dynasty weakened.",
        "brain_drain": "Over 300,000 left for foreign employment in 2022 AND 2023. 500 medical officers emigrated Jan-Aug 2022 alone.",
        "trump_tariff_threat": "44% tariff on Sri Lankan exports — garment sector ($1.9B, 300,000 workers) at severe risk.",
        "agent_note": "EVERY Sri Lankan adult lived through this crisis. It is shared trauma. Middle-class: savings destroyed. Working-class: skipped meals. Generate baseline_anxiety = elevated for ALL agents.",
    },

    "political_transformation_2024": {
        "npp_victory": "AKD (Anura Kumara Dissanayake) elected President Sep 2024. NPP/JVP landslide Nov 2024. 150 of 225 MPs are first-termers.",
        "rajapaksa_era_ended": "Rajapaksa family's dominance ended. SLPP collapsed.",
        "jvp_history": "JVP has VIOLENT history — two insurrections (1971, 1987-89). Older Sri Lankans fear it. Modern JVP is democratic, anti-corruption.",
        "agent_note": "NPP/AKD supporters: hopeful but anxious. Former Rajapaksa supporters: resentful. Tamil/Muslim: cautiously optimistic but distrustful — decades of betrayal.",
    },

    "demographics_ethnicity": {
        "sinhalese": "74.9% — Buddhist 70.2%. Some Sinhala Christians (Catholic — Negombo, Chilaw coast).",
        "sri_lankan_tamil": "11.2% — Hindu majority, some Catholic (Jaffna). Northern/Eastern provinces. Post-war community.",
        "malaiyaha_tamil": "4.1% — Plantation/Estate/Hill Country Tamil. Hindu. Tea estates (Nuwara Eliya, Badulla, Kandy). MOST marginalized community. DISTINCT from Jaffna Tamils.",
        "muslim_moor": "9.3% — Arab-descended trading community. Tamil and Sinhala speaking. Eastern Province + Colombo Pettah.",
        "burgher": "Small (<0.5%) — mixed European descent. English-speaking. Urban Colombo. Many emigrated to Australia.",
    },

    "civil_war_legacy": {
        "duration": "26 years (1983-2009). LTTE vs government. 80,000-100,000 killed. Up to 40,000 Tamil civilians in final months.",
        "missing_persons": "Tens of thousands disappeared. Mothers still searching.",
        "military_land": "Army still occupies significant Northern Province land. Gradual return but much remains.",
        "war_widows": "89,000 female-headed households in north/east — women became sole breadwinners.",
        "diaspora": "Large Tamil diaspora — Canada (Toronto), UK (London), Australia. Politically active. Sends remittances.",
        "agent_note": "For Tamil agents: war trauma is PRESENT, not historical. Missing family. Military surveillance. Memorial suppression (recently relaxed under AKD). trust_government: VERY LOW regardless of who is in power.",
    },

    "plantation_tamil_reality": {
        "history": "Brought from South India by British (1830s) as indentured labor. Denied citizenship until 2003. 200 years of marginalization.",
        "living_conditions": "Line rooms — 10x12 feet, 5-10 people. Shared latrines. No running water in many estates. UN documented conditions as near-slavery.",
        "wages": "Rs 1,350/day minimum (Sep 2024). 22 kg daily target often impossible. Many earn Rs 12,000-20,000/month.",
        "landlessness": "90%+ are LANDLESS. Line rooms owned by plantation companies.",
        "escape_routes": "Young women: Colombo garments FTZ or domestic work. Young men: construction or Gulf migration.",
        "distinct_from_jaffna": "DIFFERENT community from Jaffna Tamils. Different dialect, history, caste, relationship to state. DO NOT conflate.",
    },

    # =========================================================================
    # SECTION 2: ETHNIC-REGIONAL ZONE DYNAMICS
    # =========================================================================

    "zone_dynamics": {

        "colombo_western": {
            "character": "Economic hub. Colombo: most cosmopolitan. Corporate HQ. Port. Tourism gateway. Pettah = Muslim trading. Colombo 7 = elite. Negombo = Catholic fishing. Gampaha = industrial suburb.",
            "women_work_norms": "LOWEST restriction. Professional women normalized. Garments FTZ (Katunayake, Biyagama). Corporate. Tourism. Domestic worker economy (rural → urban migration).",
        },

        "southern": {
            "character": "Galle (colonial heritage, tourism). Matara (education). Hambantota (Rajapaksa heartland, Chinese port). Fishing. Cinnamon cultivation. Overwhelmingly Sinhala Buddhist.",
            "women_work_norms": "Moderate. Tourism creating new employment. Garments FTZ (Koggala). Cinnamon peeling — women. Fish processing and selling.",
        },

        "central_hill_country": {
            "character": "Kandy (sacred Buddhist city — Temple of Tooth). Hill country tea estates. Nuwara Eliya ('Little England'). Malaiyaha Tamil = most marginalized. Plantation economy dominates.",
            "women_work_norms": "VARIABLE. Kandyan Sinhala: conservative traditional. Plantation Tamil women: work from necessity (tea plucking is women's work). Some upward mobility through education and FTZ migration.",
        },

        "northern_jaffna_vanni": {
            "character": "Tamil heartland. Jaffna = educated professional class. Vanni (Kilinochchi, Mullaitivu) = final war battlefield — devastated. Heavy military presence. 89,000 war widows. Diaspora connections.",
            "women_work_norms": "MODERATE. Post-war necessity drove massive female economic participation. Teaching, nursing, government, small trade, agriculture, NGO work. War widows must work. Fishing processing — women. Palmyra products — women.",
        },

        "eastern": {
            "character": "Most ethnically mixed: Tamil (Batticaloa), Muslim (Ampara), Sinhala. Post-war + post-tsunami recovery. Fishing dominant. Lagoon farming. Post-Easter-2019 Muslim backlash zone.",
            "women_work_norms": "Variable by ethnicity. Tamil women: moderate participation. Muslim women: more restricted (trading family tradition — women behind scenes). Some NGO work. Fish processing.",
        },
    },

    # =========================================================================
    # SECTION 3: OCCUPATIONS
    # =========================================================================

    "female_occupations": {

        "plantation_estate": [
            "tea plucker (Malaiyaha Tamil — PRIMARY occupation — Rs 1,350/day — 100,000+ women — backbone of $1B+ tea export)",
            "rubber tapper (early morning — Sabaragamuwa, Kalutara)",
            "estate domestic worker (superintendent's bungalow)",
            "estate creche worker",
        ],

        "garments_ftz": [
            "garments FTZ worker — sewing machine operator (Katunayake, Biyagama, Koggala — young Sinhala women — $1.9B industry — at risk from tariffs)",
            "garments quality checker", "garments line supervisor",
            "garments packing and finishing worker",
        ],

        "agricultural_rural": [
            "paddy transplanting and harvesting laborer (seasonal — women)",
            "cinnamon peeler (Galle, Matara — skilled traditional — paid by weight)",
            "palmyra product maker (Jaffna — toddy, jaggery, fiber — women traditional)",
            "fish processor (dried fish, smoked fish — coastal women — east and north)",
            "fish seller (market women — Negombo, Jaffna, east coast)",
            "vegetable farmer (hill country — leeks, carrots — commercial)",
            "coconut processing worker (copra, desiccated coconut — NW Province)",
            "spice garden worker (Matale — cinnamon, cardamom, pepper)",
        ],

        "urban_working_class": [
            "domestic worker (rural women working in Colombo/Kandy homes — Sinhala AND Tamil women)",
            "beauty parlor worker and owner", "small shop keeper", "market vendor",
            "home-based sewing and tailoring (garment subcontracting + neighborhood)",
            "home-based food preparation (catering, short eats — wadai, rolls, cutlets)",
        ],

        "middle_professional": [
            "government school teacher (Sinhala/Tamil/English medium — pensioned)",
            "nurse (government hospital — many migrating abroad for better pay)",
            "midwife (public health midwife — PHM — community — respected)",
            "bank clerk and officer (BOC, People's Bank, Commercial Bank, HNB, Sampath)",
            "government administrative officer (SLAS — competitive exam)",
            "NGO worker (post-war areas and post-crisis recovery)",
            "journalist (Sinhala, Tamil, English media)",
        ],

        "corporate_professional": [
            "IT professional (Colombo — WSO2, Virtusa, 99X, IFS)",
            "corporate manager (MAS Holdings, Brandix, Dialog, John Keells)",
            "doctor (government and private)", "lawyer (growing female bar)",
            "accountant (CIMA, ACCA)", "architect",
        ],

        "overseas_migrant": [
            "domestic worker in Gulf (Saudi, Kuwait, UAE — LARGEST female category — significant abuse documented)",
            "nurse abroad (Gulf, UK, Australia, Canada)", "IT professional abroad",
            "care worker (elderly care — Israel, Italy, Japan)",
        ],
    },

    "male_occupations": {

        "transport": [
            "tuk-tuk (three-wheeler) driver — ICONIC Sri Lankan occupation. Rs 1,500-5,000/day depending on area.",
            "bus driver (SLTB government and private)", "bus conductor",
            "lorry/truck driver", "delivery rider (PickMe Food, Uber Eats — gig)",
            "PickMe/Uber car driver (ride-hailing — Colombo)",
            "fisherman — boat captain (mechanized trawler)", "fisherman — traditional outrigger canoe",
        ],

        "agriculture_fishing": [
            "paddy farmer (own land — varying sizes)", "tea estate worker — male (pruning, factory processing)",
            "rubber tapper", "coconut toddy tapper (climbing palms — dangerous)",
            "cinnamon plantation worker", "vegetable farmer (commercial — upcountry)",
            "fisherman — all coasts (significant employer — post-tsunami rebuilt fleet)",
            "prawn/shrimp farmer (lagoons — east coast, NW Province)",
        ],

        "construction_trades": [
            "construction mason (well-paid skilled)", "construction laborer",
            "carpenter", "plumber", "electrician", "painter", "tile and granite worker",
        ],

        "gem_industry": [
            "gem miner (Ratnapura — hand-dug pits — dangerous — poor despite working valuable stones)",
            "gem cutter and polisher (skilled)", "gem dealer and broker",
        ],

        "professional_government": [
            "government administrative officer (SLAS)", "police officer",
            "military officer and soldier (large standing army — significant employer for Sinhala rural men)",
            "teacher (government school)", "university lecturer",
            "doctor (government hospital — rural service required)", "lawyer",
            "accountant (CIMA, ACCA — significant profession)",
        ],

        "corporate_professional": [
            "IT professional (WSO2, Virtusa, 99X, IFS — many emigrating)",
            "corporate executive (John Keells, MAS, Dialog, Hayleys, Cargills)",
            "hotel and tourism manager", "tour guide (multi-lingual — English essential)",
        ],

        "overseas_migrant": [
            "construction worker in Gulf (Saudi, UAE, Qatar, Kuwait — largest)",
            "IT professional abroad (Australia, Canada, UK, Singapore — brain drain post-2022)",
            "doctor abroad (UK NHS, Australia, Maldives)", "merchant navy seafarer",
            "hotel worker (Maldives — major destination — close, well-paying)",
            "factory worker in South Korea (EPS program — competitive)",
        ],
    },

    # =========================================================================
    # SECTION 4: GENDER-OCCUPATION CONSTRAINTS
    # =========================================================================

    "gender_occupation_rules": {
        "universal": [
            "Ethnicity is the PRIMARY variable — more than class. A Sinhala, Tamil, Malaiyaha, and Muslim woman of same income live COMPLETELY different lives.",
            "Tea plucking is overwhelmingly Malaiyaha Tamil women's work. Do NOT assign Sinhala or Jaffna Tamil women to tea estates.",
            "Garments FTZ workers are primarily young SINHALA BUDDHIST women (18-35). FTZ living = boarding house — some family stigma about young women away from home.",
            "Domestic work in Colombo = internal migration (rural Sinhala AND Tamil women). Not local Colombo women.",
            "Gulf domestic work = poverty-driven (plantation Tamil, rural Sinhala, some Tamil from north). Significant abuse documented.",
            "Malaiyaha (plantation) Tamil: 90% landless, line room housing, distinct from Jaffna Tamil — DO NOT conflate.",
            "Muslim Moor women: trading family tradition — manage finances behind scenes but less public economic role.",
            "War widows in north/east (89,000): work from NECESSITY — multiple informal occupations simultaneously.",
            "2022 crisis trauma is UNIVERSAL — every agent's baseline_anxiety should be elevated.",
        ],
        "male_only_occupations": [
            "tuk-tuk driver (rare female exceptions but effectively male-only)",
            "bus driver and conductor", "fisherman (sea-going)", "toddy tapper",
            "gem miner (pit mining)", "construction mason",
            "Buddhist monk (bhikkhu)", "military combat roles",
        ],
        "female_dominated_occupations": [
            "tea plucker (Malaiyaha Tamil)", "garments FTZ sewing operator (Sinhala)",
            "domestic worker (internal and Gulf)", "nurse",
            "cinnamon peeler", "fish processor/seller", "beauty parlor worker",
            "palmyra product maker (Jaffna Tamil)",
        ],
    },

    # =========================================================================
    # SECTION 5: FALLBACK NAME POOLS
    # =========================================================================

    "name_pools": {
        "sinhala_buddhist_male": [
            "Chaminda Jayawardena", "Nuwan Bandara", "Pradeep Kumara", "Lakmal Wijesinghe",
            "Saman Dissanayake", "Asanka Rajapaksa", "Rohan Senanayake", "Mahesh Karunaratne",
            "Dinesh Gunawardena", "Kasun Wickremasinghe", "Tharanga Herath", "Ruwan Kularatne",
        ],
        "sinhala_buddhist_female": [
            "Nimalka Jayawardena", "Dilani Bandara", "Kumari Wijesinghe", "Sandamali Kumara",
            "Champa Senanayake", "Nimali Dissanayake", "Rashmi Karunaratne", "Anusha Herath",
            "Gayathri Rajapaksa", "Thilini Wickremasinghe",
        ],
        "sinhala_catholic_male": [
            "Angelo Perera", "Sanjeewa Fernando", "Dinesh Silva", "Roshan de Mel",
            "Ajith Corea", "Chaminda Perera",
        ],
        "sinhala_catholic_female": [
            "Mary Fernando", "Sharmalee Silva", "Renuka Perera", "Imalka de Mel",
        ],
        "sri_lankan_tamil_male": [
            "Sivaganesh Nadarajah", "Thamilselvan Pillai", "Karthikeyan Rajaratnam",
            "Jeyaratnam Sellaiah", "Suthaharan Karunanidhi", "Prasanth Yogeswaran",
            "Vithurshan Sivananthan", "Raveendran Pararajasingham",
        ],
        "sri_lankan_tamil_female": [
            "Thamilselvi Nadarajah", "Kavitha Rajaratnam", "Priya Sellaiah",
            "Meenakshi Yogeswaran", "Shanthini Sivananthan", "Kalpana Karunanidhi",
            "Vasuki Thambipillai", "Nirmala Pararajasingham",
        ],
        "malaiyaha_tamil_male": [
            "Mahalingam Suppiah", "Sivakumar Periyasamy", "Rajan Muthuthevarkittan",
            "Subramaniam Kandasamy", "Velayutham Arumugam", "Krishnasamy Nagalingam",
        ],
        "malaiyaha_tamil_female": [
            "Selvamani Suppiah", "Manohari Periyasamy", "Kamala Kandasamy",
            "Pushpavathi Arumugam", "Lakshmi Nagalingam", "Saraswathi Velayutham",
        ],
        "muslim_moor_male": [
            "Mohamed Rizwan", "Abdul Cader Farook", "Shafraz Maharoof",
            "Ashroff Salley", "Imtiaz Bakeer Markar", "Rauff Hakeem",
            "Faizer Mustapha", "Hisham Mohamed",
        ],
        "muslim_moor_female": [
            "Fathima Rizwana", "Zainab Salley", "Nazia Hakeem",
            "Rehana Farook", "Shafika Mohamed", "Amina Maharoof",
        ],
        "burgher_male": [
            "Derek Jansz", "Noel van Dort", "Rohan Brohier", "Cedric Ondaatje",
        ],
        "burgher_female": [
            "Cheryl Jansz", "Lavinia van Dort", "Sandra Brohier",
        ],
    },
}


# =============================================================================
# NEPAL OCCUPATIONAL REALITY SYSTEM
# Source: Nepal Labour Migration Report 2024, NRB remittance data, DoFE,
#         Census 2021, ILO Nepal, Amnesty Dalit report 2024, CESLAM, IDSN
# =============================================================================

NEPAL_OCCUPATIONAL_REALITY: Dict[str, Any] = {

    "macro_labor_facts": {
        "population": "approximately 30 million (Census 2021: 29.16 million)",
        "lfpr": "39.7% (2024) — LOW and declining",
        "absent_population": "2.1 million absent from country (7% of population) — 77% for work",
        "remittance_share_gdp": "23-28% of GDP — among HIGHEST in world",
        "remittance_fy2024": "NPR 1,445 billion (~$11 billion)",
        "household_dependency": "55.8% of households receive remittances. Remittance = 62% of income for recipients.",
        "agriculture_share": "Largest sector but remittance economy means many 'employed' are managing remittance-funded households",
        "youth_bulge": "Huge youth population — domestic economy CANNOT absorb them — drives migration",
        "total_abroad": "Approximately 3.5 million working abroad (14% of population)",
        "federalism": "7 provinces since 2015: Koshi, Madhesh, Bagmati, Gandaki, Lumbini, Karnali, Sudurpashchim",
    },

    "migration_facts": {
        "new_approvals_2024": "358,000+ new labor approvals",
        "gulf_malaysia_share": "81.3% of new approvals go to Gulf + Malaysia",
        "european_explosion": "European destinations: 368x increase in 5 years (Romania 12,700, Croatia 14,240 permits in 2024)",
        "india_open_border": "Nepal-India open border = massive circular migration. No passport needed. Construction, security, domestic, agriculture in Delhi/Mumbai/Punjab.",
        "female_migration": "12.9% of total (2024) — up from <7% in 2008. Domestic worker in Gulf = primary female category.",
        "worker_deaths": "Hundreds die abroad annually — construction accidents, heat stroke, suicide from debt pressure",
        "recruitment_fraud": "580+ manpower companies suspended July 2024. Workers take high-interest loans (Rs 100,000-500,000) for fees.",
        "gurkha_distinct": "British/Indian Army Gurkha = distinct stream. Gurung, Magar, Rai, Limbu communities. Pensions → prosperity. UK settlement (Aldershot, Folkestone).",
        "destinations_emerging": ["Romania", "Croatia", "Poland", "Japan", "South Korea (EPS)", "Cyprus", "Malta", "Turkey"],
    },

    "political_context": {
        "gen_z_september_2025": "PM Oli imposed social media ban → Gen Z uprising Sep 8-9 2025. At least 76 killed. Singha Durbar set on fire. Oli resigned. Parallel to Bangladesh July 2024.",
        "march_2026_election": "RSP (Rastriya Swatantra Party) led by Balen Shah won LANDSLIDE. Oli lost own seat (68,348 vs 18,734). CPN-UML got 25 seats (from 78). Entire post-1990 political class rejected.",
        "balen_shah": "Gen Z icon. Former Kathmandu mayor. Anti-corruption. Social media savvy. TOTAL rejection of old political class.",
        "agent_note": "Post-March 2026: RSP/Balen supporters HOPEFUL, young, digitally active. Old-guard (UML, Congress, Maoist): devastated. Gen Z carry trauma (friends killed Sep 2025) but also empowerment. KEY DIVIDE IS GENERATIONAL — not just caste/ethnicity. Every agent under 30 shaped by September 2025.",
    },

    "caste_ethnicity_rules": {
        "brahmin_chhetri": "~29% but dominate 91.2% of political/bureaucratic positions. Surnames: Sharma, Poudel, Aryal (Brahmin). Thapa, KC, Khadka, Bista (Chhetri). Modern: government, military officers, teaching, law, IT.",
        "newar": "~5% — controlled Kathmandu Valley. Trading, artisan, restaurant tradition. Own caste hierarchy within Newar. Surnames: Shrestha, Bajracharya, Shakya, Maharjan, Manandhar.",
        "janajati_36_percent": "Gurung/Magar (Gurkha military), Rai/Limbu (eastern hills, Kirant religion), Tamang (hills near KTM — poorest hill group), Sherpa (Everest tourism), Tharu (Terai — Kamaiya bonded labor legacy), Chepang (most marginalized — forest-dwelling).",
        "madhesi_32_percent": "Terai plains. Culturally closer to Bihar/UP India. Hindi/Maithili/Bhojpuri. Full Indian-style caste system within. Women MOST restricted in Nepal. Open border with India.",
        "dalit_13_6_percent": "Hill: Biswakarma/BK (blacksmith), Pariyar (tailor/musician), Sarki (leather). Terai: Chamar, Musahar (most destitute — rat-catching), Dom (cremation). 42% below poverty line vs 25.2% national. Untouchability still practiced.",
        "muslim_4_4_percent": "Terai concentrated. Lowest per capita income. Women most restricted. Culturally close to UP/Bihar Indian Muslims.",
    },

    "geography_zones": {

        "kathmandu_valley": {
            "character": "Capital + Lalitpur + Bhaktapur. Government, tourism, IT, Newar heritage. Most cosmopolitan. RSP/Balen powerbase.",
            "women_work_norms": "LOWEST restriction. Professional women normalized. Teacher, nurse, IT, NGO, bank, corporate, beauty parlor. Domestic workers from rural areas (Tamang, Dalit, Terai women).",
        },

        "hill_regions": {
            "character": "Terraced agriculture. Brahmin-Chhetri + Janajati. Trekking routes. ENORMOUS male out-migration — villages of women, children, elderly. Maoist insurgency history (1996-2006). 2015 earthquake devastation.",
            "women_work_norms": "Women manage EVERYTHING while men abroad. Farming, livestock, children, community. FCHV (health volunteer) is significant occupation. NOT counted as 'employed' despite doing all work.",
            "left_behind": "With most working-age men absent, women are the de facto economy but invisible in statistics.",
        },

        "terai_madhesh": {
            "character": "Southern plains. Fertile agriculture. Indian border. Madhesi + Tharu + hill migrant settlers. Industrial corridor (Birgunj, Biratnagar). Cross-border trade. Madhesh Movement legacy.",
            "women_work_norms": "MOST restricted in Nepal — similar to Bihar/UP India. Purdah/ghunghat in upper Madhesi castes. Poor women work agricultural labor. Muslim women most restricted. Tharu women relatively more active.",
        },

        "mountain_high_altitude": {
            "character": "Sherpa, Tibetan Buddhist. Solukhumbu (Everest), Mustang, Dolpo, Manang. Tourism/trekking economy. Extreme altitude. Yak herding. Monastery culture.",
            "women_work_norms": "Sherpa/mountain women run lodges, manage households during trekking season. Relatively more active than Madhesi or conservative hill women.",
        },
    },

    # =========================================================================
    # OCCUPATIONS
    # =========================================================================

    "female_occupations": {

        "agricultural_rural": [
            "subsistence farmer — terraced rice, maize, millet (de facto head of household while husband abroad)",
            "livestock keeper — goats, buffalo, cattle (rural — women manage)",
            "FCHV — Female Community Health Volunteer (vaccination, maternal health — Rs 3,000/month — significant occupation)",
            "remittance household manager (manages farm, children, elderly, finances — NOT counted as employed)",
            "tea house/lodge worker on trekking routes (cooking, hosting — Sherpa/Tamang women)",
            "porter — female (carrying doko baskets on trekking routes — poorly paid)",
            "carpet weaver (Tibetan-style — some areas)", "dhaka weaver (Palpa — traditional cloth)",
            "agricultural day laborer (Terai — paddy, wheat — Madhesi/Tharu women)",
            "brick kiln worker (Terai — bonded/semi-bonded — Tharu, Dalit families)",
        ],

        "urban_working_class": [
            "domestic worker in Kathmandu (from rural areas — Tamang, Dalit, Terai women)",
            "beauty parlor worker and owner (growing sector — Kathmandu, towns)",
            "restaurant worker", "hotel housekeeping (tourism sector)",
            "garment factory worker (small sector compared to Bangladesh)",
            "small shopkeeper", "market vendor (vegetables, household goods)",
            "home-based tailoring and embroidery", "Madhubani art painter (Terai — traditional)",
        ],

        "middle_professional": [
            "government school teacher (through Lok Sewa exam — significant female occupation — often most educated person in village)",
            "nurse (government hospital — many migrating abroad for better pay)",
            "FCHV coordinator (district level)", "NGO program officer (development sector — large in Nepal)",
            "bank clerk (Nepal Rastra Bank, Nabil, NIC Asia, Sanima — growing)",
            "government officer (through Lok Sewa Aayog — competitive)",
        ],

        "corporate_professional": [
            "IT professional (Kathmandu — growing sector — some emigrating)",
            "corporate professional (Chaudhary Group, Ncell, NTC — some women)",
            "doctor (government and private)", "lawyer (growing female bar)",
            "journalist (independent media)", "hotel/tourism management",
        ],

        "overseas_migrant": [
            "domestic worker in Gulf — Saudi/Kuwait/UAE (LARGEST female category — abuse documented)",
            "factory worker abroad (Malaysia, some)",
            "nurse abroad (Gulf, UK, Australia — professional migration)",
            "care worker abroad (Israel, Japan — emerging)",
        ],
    },

    "male_occupations": {

        "agricultural": [
            "subsistence farmer — terraced (rice, maize, millet — hill)", "paddy farmer (Terai — larger holdings)",
            "wheat and sugarcane farmer (Terai)", "livestock herder (yak — mountain, goat/buffalo — hills)",
            "agricultural day laborer (Terai — hari)",
        ],

        "transport_services": [
            "taxi/ride-app driver (Kathmandu — Pathao, inDrive)", "bus/jeep driver (mountain roads — dangerous)",
            "rickshaw puller (Terai towns)", "truck driver", "motorcycle taxi driver",
            "trekking guide (Annapurna, Everest — Sherpa/Tamang/Rai — seasonal but well-paid for guides)",
            "porter (trekking routes — carrying 30kg+ — poorly paid vs guides — Tamang often)",
            "high-altitude mountaineering support (expedition cook, camp manager — dangerous)",
        ],

        "construction_trades": [
            "construction worker (Kathmandu — building boom)", "stonemason (traditional hill skill)",
            "carpenter", "electrician", "plumber", "welder",
        ],

        "commerce": [
            "shopkeeper (general store — every town)", "restaurant owner (Newar food tradition)",
            "cross-border trader (India — Terai)", "handicraft seller (tourist market — Thamel)",
            "gem/jewelry dealer", "mobile phone shop",
        ],

        "professional_government": [
            "government officer (Lok Sewa Aayog exam — competitive — Brahmin-Chhetri dominated)",
            "teacher (government school)", "police officer", "Nepal Army soldier/officer",
            "Gurkha — British Army (Gurung, Magar, Rai, Limbu — pension → prosperity)",
            "Gurkha — Indian Army (similar communities — Indian pension)",
            "doctor (government hospital)", "lawyer", "journalist",
        ],

        "corporate_professional": [
            "IT professional (Kathmandu — growing)", "corporate executive (Chaudhary Group, Ncell, banking)",
            "hotel/tourism manager", "startup founder (small ecosystem)",
        ],

        "overseas_migrant": [
            "construction worker — Gulf (Saudi/Qatar/UAE/Kuwait — LARGEST category — kafala system)",
            "construction worker — Malaysia (significant destination)",
            "factory worker — South Korea (EPS program — well-paid, competitive, legal)",
            "factory/warehouse worker — Romania/Croatia/Poland (emerging — 368x increase)",
            "seasonal labor in India (open border — construction, security, agriculture, restaurant)",
            "student-worker — Australia/UK/Canada (studying + part-time — many plan to stay)",
        ],
    },

    # =========================================================================
    # GENDER-OCCUPATION CONSTRAINTS
    # =========================================================================

    "gender_occupation_rules": {
        "universal": [
            "Caste + ethnicity + geography = the person. Brahmin Kathmandu ≠ Tamang hills ≠ Tharu Terai ≠ Sherpa mountains ≠ Musahar Madhesh.",
            "Remittance shapes EVERYTHING. Most young men ABSENT. Women manage households, farms, children — de facto economy but not 'employed.'",
            "Left-behind women (remittance household managers) is a MASSIVE category — generate many.",
            "FCHV (Female Community Health Volunteer) is significant occupation for rural/semi-urban women.",
            "Kamaiya (bonded labor) legacy: Tharu Terai — first generation post-abolition adults. Extreme poverty, landlessness.",
            "Gurkha military = distinct pathway for Gurung, Magar, Rai, Limbu — pension prosperity. Different from Gulf labor.",
            "Madhesi women (Terai) = MOST restricted in Nepal — similar to Bihar/UP India. Purdah/ghunghat.",
            "Dalit: 42% below poverty line. Untouchability still practiced. Caste-locked occupations persist (blacksmithing, tailoring, sweeping).",
            "2015 earthquake: permanent scars for agents from Sindhupalchok, Gorkha, Dhading, Nuwakot.",
        ],
        "male_only_occupations": [
            "trekking guide (Sherpa/Tamang — effectively male)", "mountaineering support",
            "bus/jeep driver", "rickshaw puller", "construction mason",
            "Gurkha soldier", "yak herder (high altitude)",
        ],
        "female_dominated_occupations": [
            "FCHV health volunteer", "tea plucker (if applicable)",
            "domestic worker (internal — rural → Kathmandu)", "beauty parlor worker",
            "remittance household manager", "carpet/dhaka weaver",
        ],
    },

    # =========================================================================
    # FALLBACK NAME POOLS
    # =========================================================================

    "name_pools": {
        "brahmin_male": [
            "Ram Prasad Sharma", "Krishna Poudel", "Shiva Aryal", "Govinda Bhatta",
            "Bishnu Pant", "Hari Upadhyay", "Ganga Dahal", "Keshav Subedi",
            "Narayan Adhikari", "Surya Gautam",
        ],
        "brahmin_female": [
            "Saraswati Sharma", "Laxmi Poudel", "Sita Aryal", "Gita Bhatta",
            "Parvati Subedi", "Kamala Adhikari", "Radha Gautam", "Durga Dahal",
        ],
        "chhetri_male": [
            "Bir Bahadur Thapa", "Khadga Khadka", "Dil Bahadur KC", "Padam Bista",
            "Man Bahadur Rawat", "Narendra Basnet", "Sher Bahadur Kunwar", "Lokendra Shahi",
        ],
        "chhetri_female": [
            "Pabitra Thapa", "Nirmala KC", "Bimala Khadka", "Kopila Bista",
            "Mina Basnet", "Sarita Rawat",
        ],
        "newar_male": [
            "Rajesh Shrestha", "Sujan Bajracharya", "Bikash Shakya", "Anil Maharjan",
            "Prabin Manandhar", "Suresh Tuladhar", "Kiran Amatya",
        ],
        "newar_female": [
            "Shanti Shrestha", "Sunita Bajracharya", "Nisha Shakya", "Laxmi Maharjan",
            "Mina Manandhar", "Rekha Tuladhar",
        ],
        "gurung_magar_male": [
            "Tek Bahadur Gurung", "Om Bahadur Pun", "Dal Bahadur Ale",
            "Bhim Bahadur Thapa Magar", "Kul Bahadur Rana Magar",
        ],
        "gurung_magar_female": [
            "Sanu Maya Gurung", "Dhan Maya Pun", "Lal Maya Ale",
            "Nani Maya Thapa Magar", "Rita Rana Magar",
        ],
        "rai_limbu_male": [
            "Dhan Bahadur Rai", "Karna Bahadur Limbu", "Padam Rai",
            "Nir Kumar Subba", "Bir Bahadur Yakha",
        ],
        "rai_limbu_female": [
            "Hira Maya Rai", "Suk Maya Limbu", "Devi Subba",
            "Phul Maya Rai",
        ],
        "tamang_male": [
            "Pasang Tamang", "Dawa Lama", "Phurba Moktan",
            "Mingma Waiba", "Karma Ghising",
        ],
        "tamang_female": [
            "Kalpana Tamang", "Phul Maya Lama", "Sanu Moktan",
            "Dawa Dolma Tamang",
        ],
        "sherpa_male": [
            "Ang Tshering Sherpa", "Tenzing Sherpa", "Mingma Sherpa",
            "Pemba Sherpa", "Lakpa Sherpa",
        ],
        "sherpa_female": [
            "Dawa Yangzum Sherpa", "Phuti Sherpa", "Lhamu Sherpa",
            "Yangjee Sherpa",
        ],
        "tharu_male": [
            "Ram Chaudhary", "Shyam Tharu", "Birendra Mahato",
            "Raj Kumar Chaudhary", "Gopal Tharu",
        ],
        "tharu_female": [
            "Sita Chaudhary", "Mina Tharu", "Laxmi Mahato",
            "Kamala Chaudhary",
        ],
        "dalit_hill_male": [
            "Hari Biswakarma", "Ram Pariyar", "Gopal Sarki",
            "Dil BK", "Bishnu Nepali", "Shyam Sunar",
        ],
        "dalit_hill_female": [
            "Laxmi Biswakarma", "Sita Pariyar", "Kamala Sarki",
            "Mina BK", "Gita Nepali",
        ],
        "madhesi_male": [
            "Rajesh Yadav", "Suresh Mandal", "Manoj Singh",
            "Ashok Jha", "Ram Kumar Gupta", "Birendra Shah",
        ],
        "madhesi_female": [
            "Sunita Yadav", "Geeta Mandal", "Lata Singh",
            "Asha Jha", "Meena Gupta",
        ],
        "dalit_terai_male": [
            "Ram Chamar", "Sunil Musahar", "Mohan Dom",
            "Rajesh Paswan", "Dinesh Ram",
        ],
        "dalit_terai_female": [
            "Phoolmati Chamar", "Guddi Musahar", "Laxmi Dom",
            "Sushila Paswan",
        ],
        "muslim_male": [
            "Imran Khan", "Salim Ansari", "Rashid Sheikh",
            "Farhan Miya", "Zaheer Siddiqui",
        ],
        "muslim_female": [
            "Fatima Ansari", "Nazia Khan", "Rukhsar Sheikh",
            "Shabana Miya",
        ],
    },
}


def _slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")
    return value or "ops_agent"


def _coerce_int(value: Any, default: int) -> int:
    try:
        parsed = int(float(value))
        return parsed if parsed > 0 else default
    except (TypeError, ValueError):
        return default


def normalize_ops_population_params(params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Normalize structured OPS population params from the frontend into backend-safe values."""
    if not isinstance(params, dict) or not params:
        return None

    raw_run_type = str(params.get("run_type") or params.get("runType") or "Domestic").strip()
    run_type = RUN_TYPE_ALIASES.get(raw_run_type.lower(), raw_run_type if raw_run_type in RUN_TYPE_ALIASES.values() else "Domestic")

    origin_country_raw = str(params.get("origin_country") or params.get("originCountry") or params.get("country") or "Bangladesh").strip()
    origin_country = COUNTRY_ALIASES.get(origin_country_raw.lower(), origin_country_raw if origin_country_raw in COUNTRY_SETTINGS else "Bangladesh")

    origin_countries_raw = params.get("origin_countries") or params.get("originCountries") or params.get("countries") or []
    origin_countries = []
    for item in origin_countries_raw if isinstance(origin_countries_raw, list) else []:
        normalized = COUNTRY_ALIASES.get(str(item).strip().lower())
        if normalized and normalized not in origin_countries:
            origin_countries.append(normalized)

    raw_segments = params.get("segments") or []
    segments = []
    if isinstance(raw_segments, list):
        for item in raw_segments:
            normalized = SEGMENT_ALIASES.get(str(item).strip().lower())
            if normalized and normalized not in segments:
                segments.append(normalized)

    requested_outputs = []
    raw_outputs = params.get("requested_outputs") or params.get("requestedOutputs") or []
    if isinstance(raw_outputs, list):
        requested_outputs = [str(item).strip() for item in raw_outputs if str(item).strip()]

    audience_region = str(params.get("audience_region") or params.get("audienceRegion") or "").strip()
    corridor = str(params.get("corridor") or "").strip()
    region = str(params.get("region") or "mixed").strip() or "mixed"

    normalized = {
        "run_type": run_type,
        "origin_country": origin_country,
        "origin_countries": origin_countries,
        "audience_region": audience_region,
        "corridor": corridor,
        "segments": segments,
        "n_agents": _coerce_int(params.get("n_agents") or params.get("nAgents") or params.get("target_agents") or params.get("targetAgents"), 100),
        "requested_outputs": requested_outputs,
        "region": region,
    }

    if not normalized["segments"]:
        return None

    if run_type == "Regional multi-country" and len(origin_countries) < 2:
        return None
    if run_type == "Diaspora" and not audience_region:
        normalized["audience_region"] = "Gulf"
    if run_type == "Corridor-based" and not corridor:
        normalized["corridor"] = f"{origin_country} corridor"

    return normalized


class OPSPopulationGenerator:
    """Generate OPS-native populations directly from population parameters."""

    MAX_WORKERS = 10

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model_name = model_name or Config.LLM_MODEL_NAME
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.profile_helper = OasisProfileGenerator(
            api_key=self.api_key,
            base_url=self.base_url,
            model_name=self.model_name,
        )

    def generate_population(
        self,
        params: Dict[str, Any],
        scenario_context: str,
        use_llm: bool = True,
    ) -> List[OasisAgentProfile]:
        """Dispatch OPS-native population generation by run type and geography."""
        normalized = normalize_ops_population_params(params)
        if not normalized:
            raise ValueError("OPS population params are missing required fields")

        run_type = normalized["run_type"]
        n_agents = normalized["n_agents"]
        segments = normalized["segments"]

        if run_type == "Domestic":
            return self._dispatch_country_population(
                country=normalized["origin_country"],
                n_agents=n_agents,
                segments=segments,
                scenario_context=scenario_context,
                region=normalized["region"],
                use_llm=use_llm,
            )

        if run_type == "Diaspora":
            return self.generate_diaspora_population(
                n_agents=n_agents,
                segments=segments,
                scenario_context=scenario_context,
                audience_region=normalized["audience_region"],
                origin_country=normalized["origin_country"],
                use_llm=use_llm,
            )

        if run_type == "Corridor-based":
            return self.generate_diaspora_population(
                n_agents=n_agents,
                segments=segments,
                scenario_context=f"{scenario_context}\nCorridor: {normalized['corridor']}",
                audience_region=normalized["audience_region"] or "mixed",
                origin_country=normalized["origin_country"],
                use_llm=use_llm,
            )

        return self.generate_mixed_south_asia_population(
            n_agents=n_agents,
            segments=segments,
            scenario_context=scenario_context,
            countries=normalized["origin_countries"],
            use_llm=use_llm,
        )

    def generate_bangladesh_population(
        self,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        region: str = "mixed",
        use_llm: bool = True,
    ) -> List[OasisAgentProfile]:
        return self._generate_country_population("Bangladesh", n_agents, segments, scenario_context, region, use_llm)

    def generate_india_population(
        self,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        region: str = "mixed",
        use_llm: bool = True,
    ) -> List[OasisAgentProfile]:
        return self._generate_country_population("India", n_agents, segments, scenario_context, region, use_llm)

    def generate_pakistan_population(
        self,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        region: str = "mixed",
        use_llm: bool = True,
    ) -> List[OasisAgentProfile]:
        return self._generate_country_population("Pakistan", n_agents, segments, scenario_context, region, use_llm)

    def generate_nepal_population(
        self,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        region: str = "mixed",
        use_llm: bool = True,
    ) -> List[OasisAgentProfile]:
        return self._generate_country_population("Nepal", n_agents, segments, scenario_context, region, use_llm)

    def generate_srilanka_population(
        self,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        region: str = "mixed",
        use_llm: bool = True,
    ) -> List[OasisAgentProfile]:
        return self._generate_country_population("Sri Lanka", n_agents, segments, scenario_context, region, use_llm)

    def generate_diaspora_population(
        self,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        audience_region: str = "Gulf",
        origin_country: str = "Bangladesh",
        use_llm: bool = True,
    ) -> List[OasisAgentProfile]:
        normalized_country = COUNTRY_ALIASES.get(str(origin_country).strip().lower(), origin_country if origin_country in COUNTRY_SETTINGS else "Bangladesh")
        normalized_region = str(audience_region or "mixed").strip() or "mixed"
        settings = COUNTRY_SETTINGS.get(normalized_country, COUNTRY_SETTINGS["Bangladesh"])
        institutional_roles = self._select_institutional_seed_roles(n_agents)
        public_agent_count = max(1, n_agents - len(institutional_roles))
        assignments = self._build_segment_assignments(public_agent_count, segments, settings["segment_weights"])
        diaspora_context = DIASPORA_REGION_SETTINGS.get(normalized_region.lower(), DIASPORA_REGION_SETTINGS["mixed"])

        profiles: List[OasisAgentProfile] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(self.MAX_WORKERS, max(1, len(assignments)))) as executor:
            futures = [
                executor.submit(
                    self._generate_ops_agent_from_demographics,
                    country=normalized_country,
                    segment=segment,
                    region=normalized_region,
                    agent_index=idx,
                    scenario_context=scenario_context,
                    use_llm=use_llm,
                    diaspora_region=normalized_region,
                    diaspora_context=diaspora_context,
                )
                for idx, segment in enumerate(assignments)
            ]
            for future in concurrent.futures.as_completed(futures):
                profiles.append(future.result())

        for role in institutional_roles:
            profiles.append(
                self._generate_institutional_seed_profile(
                    country=normalized_country,
                    role_type=role,
                    region=normalized_region,
                    agent_index=len(profiles),
                    scenario_context=scenario_context,
                    diaspora_region=normalized_region,
                    diaspora_context=diaspora_context,
                    use_llm=use_llm,
                )
            )

        profiles.sort(key=lambda profile: profile.user_id)
        return self._reindex_profiles(profiles)

    def generate_mixed_south_asia_population(
        self,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        countries: Optional[List[str]] = None,
        use_llm: bool = True,
    ) -> List[OasisAgentProfile]:
        included = [COUNTRY_ALIASES.get(str(country).strip().lower(), str(country).strip()) for country in (countries or [])]
        included = [country for country in included if country in COUNTRY_SETTINGS]
        include_diaspora = not included
        if not included:
            included = ["Bangladesh", "India", "Pakistan", "Nepal", "Sri Lanka"]

        weights = {country: MIXED_SOUTH_ASIA_WEIGHTS.get(country, 0.0) for country in included}
        if include_diaspora:
            weights["Diaspora"] = MIXED_SOUTH_ASIA_WEIGHTS["Diaspora"]
        weights = self._normalize_weight_subset(weights)

        allocations = self._allocate_weighted_counts(n_agents, weights)
        combined: List[OasisAgentProfile] = []

        for country, count in allocations.items():
            if count <= 0:
                continue
            if country == "Diaspora":
                combined.extend(
                    self.generate_diaspora_population(
                        n_agents=count,
                        segments=segments,
                        scenario_context=scenario_context,
                        audience_region="mixed",
                        origin_country=random.choice(included),
                        use_llm=use_llm,
                    )
                )
                continue

            combined.extend(
                self._dispatch_country_population(
                    country=country,
                    n_agents=count,
                    segments=segments,
                    scenario_context=scenario_context,
                    region="mixed",
                    use_llm=use_llm,
                )
            )

        return self._reindex_profiles(combined)

    def build_population_entities(
        self,
        profiles: List[OasisAgentProfile],
    ) -> List[EntityNode]:
        """Build synthetic population entities so config generation matches OPS profile scale."""
        entities: List[EntityNode] = []
        for profile in profiles:
            segment = profile.source_entity_type or "person"
            entity_labels = self._segment_to_entity_labels(segment)
            entity_type = next((label for label in entity_labels if label not in {"Entity", "Person", "Node"}), "Person")
            summary = (
                f"{profile.name} is a {profile.profession or 'person'} from {profile.location or profile.country or 'South Asia'}"
                f" speaking as a {entity_type} archetype in the simulation."
                f" Segment={segment},"
                f" with trust_government={profile.current_trust_government if profile.current_trust_government is not None else profile.trust_government},"
                f" shame_sensitivity={profile.current_shame_sensitivity if profile.current_shame_sensitivity is not None else profile.shame_sensitivity},"
                f" primary_fear={profile.primary_fear or 'unclear'}, dialect={profile.dialect or 'unspecified'},"
                f" fb_intensity={profile.fb_intensity if profile.fb_intensity is not None else 'unknown'}."
            )
            entities.append(
                EntityNode(
                    uuid=profile.source_entity_uuid or f"ops_profile_{profile.user_id}",
                    name=profile.name,
                    labels=entity_labels,
                    summary=summary,
                    attributes={
                        "segment": segment,
                        "voice_archetype": entity_type,
                        "profession": profile.profession,
                        "country": profile.country,
                        "location": getattr(profile, "location", None),
                        "dialect": profile.dialect,
                        "primary_fear": profile.primary_fear,
                        "influence_radius": profile.influence_radius,
                    },
                )
            )
        return entities

    def _dispatch_country_population(
        self,
        country: str,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        region: str,
        use_llm: bool,
    ) -> List[OasisAgentProfile]:
        if country == "Bangladesh":
            return self.generate_bangladesh_population(n_agents, segments, scenario_context, region, use_llm)
        if country == "India":
            return self.generate_india_population(n_agents, segments, scenario_context, region, use_llm)
        if country == "Pakistan":
            return self.generate_pakistan_population(n_agents, segments, scenario_context, region, use_llm)
        if country == "Nepal":
            return self.generate_nepal_population(n_agents, segments, scenario_context, region, use_llm)
        return self.generate_srilanka_population(n_agents, segments, scenario_context, region, use_llm)

    def _generate_country_population(
        self,
        country: str,
        n_agents: int,
        segments: List[str],
        scenario_context: str,
        region: str,
        use_llm: bool,
    ) -> List[OasisAgentProfile]:
        settings = COUNTRY_SETTINGS[country]
        institutional_roles = self._select_institutional_seed_roles(n_agents)
        public_agent_count = max(1, n_agents - len(institutional_roles))
        assignments = self._build_segment_assignments(public_agent_count, segments, settings["segment_weights"])
        normalized_region = self._normalize_region(settings["regions"], region)

        profiles: List[OasisAgentProfile] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(self.MAX_WORKERS, max(1, len(assignments)))) as executor:
            futures = [
                executor.submit(
                    self._generate_ops_agent_from_demographics,
                    country=country,
                    segment=segment,
                    region=normalized_region,
                    agent_index=idx,
                    scenario_context=scenario_context,
                    use_llm=use_llm,
                )
                for idx, segment in enumerate(assignments)
            ]
            for future in concurrent.futures.as_completed(futures):
                profiles.append(future.result())

        for role in institutional_roles:
            profiles.append(
                self._generate_institutional_seed_profile(
                    country=country,
                    role_type=role,
                    region=normalized_region,
                    agent_index=len(profiles),
                    scenario_context=scenario_context,
                    diaspora_region=None,
                    diaspora_context=None,
                    use_llm=use_llm,
                )
            )

        profiles.sort(key=lambda profile: profile.user_id)
        return self._reindex_profiles(profiles)

    def _generate_institutional_seed_profile(
        self,
        country: str,
        role_type: str,
        region: str,
        agent_index: int,
        scenario_context: str,
        diaspora_region: Optional[str],
        diaspora_context: Optional[str],
        use_llm: bool = True,
    ) -> OasisAgentProfile:
        if not use_llm:
            profile_data = self._generate_institutional_fallback_profile(
                country=country,
                role_type=role_type,
                region=region,
                diaspora_region=diaspora_region,
            )
        else:
            prompt = self._build_institution_prompt(
                country=country,
                role_type=role_type,
                region=region,
                scenario_context=scenario_context,
                diaspora_region=diaspora_region,
                diaspora_context=diaspora_context,
            )
            system_prompt = (
                "You are an OPS institutional-voice generation expert. Generate one high-influence institutional or expert voice for a South Asian behavioral simulation. "
                "Return one valid JSON object only. String values must not contain unescaped newlines."
            )
            profile_data = None
            last_error = None
            for attempt in range(3):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt},
                        ],
                        response_format={"type": "json_object"},
                        temperature=max(0.2, 0.55 - (attempt * 0.1)),
                    )
                    content = response.choices[0].message.content
                    if response.choices[0].finish_reason == "length":
                        content = self.profile_helper._fix_truncated_json(content)
                    try:
                        profile_data = json.loads(content)
                    except json.JSONDecodeError:
                        repaired = self.profile_helper._try_fix_json(
                            content=content,
                            entity_name=f"{country}_{role_type}_{agent_index}",
                            entity_type=role_type,
                            entity_summary=scenario_context[:200],
                        )
                        if repaired.get("_fixed"):
                            repaired.pop("_fixed", None)
                        profile_data = repaired
                    if profile_data:
                        break
                except Exception as exc:
                    last_error = exc
                    logger.warning(
                        f"OPS institutional seed generation failed for {country}/{role_type} on attempt {attempt + 1}: {exc}"
                    )
            if not profile_data:
                logger.warning(
                    f"Falling back to institutional OPS profile for {country}/{role_type}: {last_error}"
                )
                profile_data = self._generate_institutional_fallback_profile(
                    country=country,
                    role_type=role_type,
                    region=region,
                    diaspora_region=diaspora_region,
                )

        return self._build_profile(
            country=country,
            segment=role_type,
            agent_index=agent_index,
            region=region,
            profile_data=profile_data,
            diaspora_region=diaspora_region,
        )

    def _generate_ops_agent_from_demographics(
        self,
        country: str,
        segment: str,
        region: str,
        agent_index: int,
        scenario_context: str,
        use_llm: bool = True,
        diaspora_region: Optional[str] = None,
        diaspora_context: Optional[str] = None,
    ) -> OasisAgentProfile:
        if not use_llm:
            profile_data = self._generate_fallback_profile(country, segment, region, agent_index, diaspora_region)
        else:
            prompt = self._build_population_prompt(
                country=country,
                segment=segment,
                region=region,
                scenario_context=scenario_context,
                diaspora_region=diaspora_region,
                diaspora_context=diaspora_context,
            )
            system_prompt = (
                "You are an OPS population generation expert. Generate one authentic, specific South Asian person for a behavioral public-opinion simulation. "
                "Return a single valid JSON object only. String values must not contain unescaped newlines. Use English except for names, locations, and dialect labels where appropriate."
            )

            max_attempts = 3
            last_error = None
            profile_data: Optional[Dict[str, Any]] = None

            for attempt in range(max_attempts):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt},
                        ],
                        response_format={"type": "json_object"},
                        temperature=max(0.3, 0.7 - (attempt * 0.1)),
                    )
                    content = response.choices[0].message.content
                    if response.choices[0].finish_reason == "length":
                        content = self.profile_helper._fix_truncated_json(content)

                    try:
                        profile_data = json.loads(content)
                    except json.JSONDecodeError:
                        repaired = self.profile_helper._try_fix_json(
                            content=content,
                            entity_name=f"{country}_{segment}_{agent_index}",
                            entity_type=segment,
                            entity_summary=scenario_context[:200],
                        )
                        if repaired.get("_fixed"):
                            repaired.pop("_fixed", None)
                        profile_data = repaired

                    if profile_data:
                        break
                except Exception as exc:
                    last_error = exc
                    logger.warning(
                        f"OPS population generation failed for {country}/{segment} agent {agent_index} on attempt {attempt + 1}: {exc}"
                    )

            if not profile_data:
                logger.warning(
                    f"Falling back to rule-based OPS profile for {country}/{segment} agent {agent_index}: {last_error}"
                )
                profile_data = self._generate_fallback_profile(country, segment, region, agent_index, diaspora_region)

        return self._build_profile(
            country=country,
            segment=segment,
            agent_index=agent_index,
            region=region,
            profile_data=profile_data,
            diaspora_region=diaspora_region,
        )

    @staticmethod
    def _get_bangladesh_occupation_context(segment: str, region: str, gender: str = "random") -> str:
        """Build Bangladesh-specific occupation and zone context for the LLM prompt."""
        reality = BANGLADESH_OCCUPATIONAL_REALITY

        # Select relevant occupation pool based on segment and gender
        if gender == "female" or (gender == "random" and segment in ("women",)):
            occ_pools = reality["female_occupations"]
        elif gender == "male":
            occ_pools = reality["male_occupations"]
        else:
            # Mixed — provide both
            occ_pools = None

        segment_occ_map = {
            "rural": ("agricultural_rural", "agricultural"),
            "urban_working": ("urban_working_class", "urban_working_class_services"),
            "middle_class": ("middle_class_professional", "middle_professional"),
            "corporate": ("corporate_elite_professional", "corporate_elite"),
            "migration_workers": ("migrant_abroad", "migrant_abroad"),
            "students": ("urban_working_class", "transport_logistics"),
            "women": ("agricultural_rural", "agricultural"),
            "elderly": ("middle_class_professional", "trade_commerce"),
        }
        female_key, male_key = segment_occ_map.get(segment, ("urban_working_class", "urban_working_class_services"))

        occ_lines = []
        if occ_pools:
            key = female_key if gender == "female" or segment == "women" else male_key
            pool = occ_pools.get(key, [])
            if pool:
                sample = pool[:15] if len(pool) > 15 else pool
                occ_lines.append(f"Realistic occupations for this segment ({gender}): {', '.join(sample)}")
        else:
            f_pool = reality["female_occupations"].get(female_key, [])
            m_pool = reality["male_occupations"].get(male_key, [])
            if f_pool:
                occ_lines.append(f"Realistic female occupations: {', '.join(f_pool[:10])}")
            if m_pool:
                occ_lines.append(f"Realistic male occupations: {', '.join(m_pool[:10])}")

        # Zone dynamics
        zone_key = region.lower().replace(" ", "_")
        zone_map = {
            "dhaka": "dhaka", "chittagong": "chittagong", "sylhet": "sylhet",
            "rajshahi": "rajshahi", "barisal": "khulna_barisal_coastal",
            "khulna": "khulna_barisal_coastal", "rangpur": "rangpur_kurigram_north",
            "comilla": "comilla_noakhali_feni", "mymensingh": "mymensingh_tangail",
            "mixed": None,
        }
        zone_data = reality["zone_social_dynamics"].get(zone_map.get(zone_key, zone_key))
        if zone_data:
            occ_lines.append(f"Zone women's work norms: {zone_data.get('women_work_norms', 'Variable by class')}")
            if zone_data.get("critical_note"):
                occ_lines.append(f"CRITICAL: {zone_data['critical_note']}")

        # Gender-occupation constraints
        rules = reality["gender_occupation_rules"]
        occ_lines.append("Gender-occupation constraints:")
        for rule in rules["universal"][:5]:
            occ_lines.append(f"  - {rule}")

        # Political context
        pol = reality["political_context_2024_2026"]
        occ_lines.append(f"Political context: {pol['july_revolution_2024']}")
        occ_lines.append(f"Economic impact: {pol['economic_impact']}")
        occ_lines.append(f"IMPORTANT: {pol['agent_generation_note']}")

        # Key macro facts
        macro = reality["macro_labor_facts"]
        occ_lines.append(f"Labor market: {macro['informal_employment']} informal. {macro['sector_agriculture']} in agriculture.")

        return "\n".join(occ_lines)

    @staticmethod
    def _get_india_occupation_context(segment: str, region: str, gender: str = "random") -> str:
        """Build India-specific occupation, caste, and zone context for the LLM prompt."""
        reality = INDIA_OCCUPATIONAL_REALITY

        # Select relevant occupation pool based on segment and gender
        if gender == "female" or (gender == "random" and segment in ("women",)):
            occ_pools = reality["female_occupations"]
        elif gender == "male":
            occ_pools = reality["male_occupations"]
        else:
            occ_pools = None

        segment_occ_map = {
            "rural": ("agricultural_rural", "agricultural"),
            "urban_working": ("urban_working_class", "urban_services"),
            "middle_class": ("middle_class_professional", "middle_professional"),
            "corporate": ("corporate_elite_professional", "corporate_elite"),
            "migration_workers": ("migrant_abroad", "migrant_abroad"),
            "students": ("urban_working_class", "transport_logistics"),
            "women": ("agricultural_rural", "agricultural"),
            "elderly": ("middle_class_professional", "trade_commerce"),
        }
        female_key, male_key = segment_occ_map.get(segment, ("urban_working_class", "urban_services"))

        occ_lines = []
        if occ_pools:
            key = female_key if gender == "female" or segment == "women" else male_key
            pool = occ_pools.get(key, [])
            if pool:
                sample = pool[:15] if len(pool) > 15 else pool
                occ_lines.append(f"Realistic occupations for this segment ({gender}): {', '.join(sample)}")
        else:
            f_pool = reality["female_occupations"].get(female_key, [])
            m_pool = reality["male_occupations"].get(male_key, [])
            if f_pool:
                occ_lines.append(f"Realistic female occupations: {', '.join(f_pool[:10])}")
            if m_pool:
                occ_lines.append(f"Realistic male occupations: {', '.join(m_pool[:10])}")

        # Zone dynamics
        zone_key = region.lower().replace(" ", "_")
        zone_map = {
            "delhi": "punjab_haryana_delhi", "mumbai": "maharashtra_mumbai",
            "kolkata": "west_bengal_northeast", "chennai": "tamil_nadu_karnataka",
            "bengaluru": "tamil_nadu_karnataka", "hyderabad": "andhra_telangana",
            "lucknow": "uttar_pradesh", "kerala": "kerala",
            "punjab": "punjab_haryana_delhi", "rajasthan": "rajasthan_gujarat",
            "northeast": "west_bengal_northeast", "mixed": None,
        }
        zone_data = reality["state_zone_dynamics"].get(zone_map.get(zone_key, zone_key))
        if zone_data:
            occ_lines.append(f"Zone women's work norms: {zone_data.get('women_work_norms', 'Variable by state and caste')}")

        # Caste-occupation rules
        caste_rules = reality["caste_occupation_rules"]
        occ_lines.append(f"Caste system: {caste_rules['overview']}")
        occ_lines.append("Key caste-occupation mappings (infer from name/occupation — NEVER state explicitly):")
        for key in ["brahmin_upper", "obc_artisan_farming", "dalit_sc", "muslim"]:
            occ_lines.append(f"  - {key}: {caste_rules[key][:150]}...")

        # Gender-occupation constraints
        rules = reality["gender_occupation_rules"]
        occ_lines.append("Gender-occupation constraints:")
        for rule in rules["universal"][:5]:
            occ_lines.append(f"  - {rule}")

        # Political context
        pol = reality["political_context"]
        occ_lines.append(f"Political context: {pol['bjp_governance']}")
        occ_lines.append(f"Caste politics: {pol['caste_politics']}")
        occ_lines.append(f"IMPORTANT: {pol['agent_generation_note']}")

        # ASHA/Anganwadi note for relevant segments
        if segment in ("rural", "urban_working", "women"):
            asha = reality["asha_anganwadi_frontline"]
            occ_lines.append(f"ASHA/Anganwadi: {asha['total_frontline_women']}. {asha['agent_note']}")

        # Key macro facts
        macro = reality["macro_labor_facts"]
        occ_lines.append(f"Labor market: {macro['informal_sector']}. Self-employed: {macro['self_employed']}.")

        return "\n".join(occ_lines)

    @staticmethod
    def _get_pakistan_occupation_context(segment: str, region: str, gender: str = "random") -> str:
        """Build Pakistan-specific occupation and provincial context for the LLM prompt."""
        reality = PAKISTAN_OCCUPATIONAL_REALITY

        # Select relevant occupation pool
        if gender == "female" or (gender == "random" and segment in ("women",)):
            occ_pools = reality["female_occupations"]
        elif gender == "male":
            occ_pools = reality["male_occupations"]
        else:
            occ_pools = None

        segment_occ_map_f = {
            "rural": "universally_acceptable",
            "urban_working": "acceptable_in_cities",
            "middle_class": "acceptable_in_cities",
            "corporate": "acceptable_in_cities",
            "migration_workers": "migrant_abroad",
            "students": "acceptable_in_cities",
            "women": "universally_acceptable",
            "elderly": "universally_acceptable",
        }
        segment_occ_map_m = {
            "rural": "agricultural",
            "urban_working": "construction_trades",
            "middle_class": "professional_government",
            "corporate": "corporate_professional",
            "migration_workers": "migrant_abroad",
            "students": "commerce_trade",
            "women": "agricultural",
            "elderly": "professional_government",
        }

        occ_lines = []
        if occ_pools:
            key = segment_occ_map_f.get(segment, "acceptable_in_cities") if (gender == "female" or segment == "women") else segment_occ_map_m.get(segment, "commerce_trade")
            pool = occ_pools.get(key, [])
            if pool:
                sample = pool[:15] if len(pool) > 15 else pool
                occ_lines.append(f"Realistic occupations for this segment ({gender}): {', '.join(sample)}")
        else:
            f_key = segment_occ_map_f.get(segment, "acceptable_in_cities")
            m_key = segment_occ_map_m.get(segment, "commerce_trade")
            f_pool = reality["female_occupations"].get(f_key, [])
            m_pool = reality["male_occupations"].get(m_key, [])
            if f_pool:
                occ_lines.append(f"Realistic female occupations: {', '.join(f_pool[:10])}")
            if m_pool:
                occ_lines.append(f"Realistic male occupations: {', '.join(m_pool[:10])}")

        # Provincial zone dynamics
        zone_key = region.lower().replace(" ", "_")
        zone_map = {
            "karachi": "sindh_karachi", "lahore": "punjab_north",
            "islamabad": "punjab_north", "peshawar": "kp_peshawar",
            "quetta": "balochistan", "multan": "punjab_south_seraiki",
            "interior_sindh": "sindh_interior", "faisalabad": "punjab_north",
            "mixed": None,
        }
        zone_data = reality["provincial_zones"].get(zone_map.get(zone_key, zone_key))
        if zone_data:
            occ_lines.append(f"Province women's work norms: {zone_data.get('women_work_norms', 'Variable by province and ethnicity')}")

        # Sectarian/ethnic rules
        sec = reality["sectarian_ethnic_rules"]
        occ_lines.append("Sectarian-ethnic identity shapes occupation and safety:")
        occ_lines.append(f"  - {sec['shia_15_20_percent']}")
        occ_lines.append(f"  - {sec['ahmadi_persecuted']}")
        occ_lines.append(f"  - {sec['christian_2_3_percent']}")
        occ_lines.append(f"  - {sec['punjabi_biradari']}")

        # Gender-occupation constraints
        rules = reality["gender_occupation_rules"]
        occ_lines.append("Gender-occupation constraints:")
        for rule in rules["universal"][:5]:
            occ_lines.append(f"  - {rule}")

        # Political context
        pol = reality["political_crisis_2022_2026"]
        occ_lines.append(f"Political crisis: {pol['overview']}")
        occ_lines.append(f"IMPORTANT: {pol['agent_generation_note']}")

        # Macro facts
        macro = reality["macro_labor_facts"]
        occ_lines.append(f"Labor market: {macro['informal_sector']}. Female LFPR: {macro['female_lfpr']}.")
        occ_lines.append(f"Unpaid care: {macro['unpaid_domestic_care']}")

        return "\n".join(occ_lines)

    @staticmethod
    def _get_srilanka_occupation_context(segment: str, region: str, gender: str = "random") -> str:
        """Build Sri Lanka-specific occupation and ethnic/zone context for the LLM prompt."""
        reality = SRI_LANKA_OCCUPATIONAL_REALITY

        if gender == "female" or (gender == "random" and segment in ("women",)):
            occ_pools = reality["female_occupations"]
        elif gender == "male":
            occ_pools = reality["male_occupations"]
        else:
            occ_pools = None

        segment_occ_map_f = {
            "rural": "agricultural_rural", "urban_working": "urban_working_class",
            "middle_class": "middle_professional", "corporate": "corporate_professional",
            "migration_workers": "overseas_migrant", "students": "urban_working_class",
            "women": "agricultural_rural", "elderly": "middle_professional",
        }
        segment_occ_map_m = {
            "rural": "agriculture_fishing", "urban_working": "transport",
            "middle_class": "professional_government", "corporate": "corporate_professional",
            "migration_workers": "overseas_migrant", "students": "transport",
            "women": "agriculture_fishing", "elderly": "professional_government",
        }

        occ_lines = []
        if occ_pools:
            key = segment_occ_map_f.get(segment, "urban_working_class") if (gender == "female" or segment == "women") else segment_occ_map_m.get(segment, "transport")
            pool = occ_pools.get(key, [])
            if pool:
                sample = pool[:15] if len(pool) > 15 else pool
                occ_lines.append(f"Realistic occupations for this segment ({gender}): {', '.join(sample)}")
        else:
            f_key = segment_occ_map_f.get(segment, "urban_working_class")
            m_key = segment_occ_map_m.get(segment, "transport")
            f_pool = reality["female_occupations"].get(f_key, [])
            m_pool = reality["male_occupations"].get(m_key, [])
            if f_pool:
                occ_lines.append(f"Realistic female occupations: {', '.join(f_pool[:10])}")
            if m_pool:
                occ_lines.append(f"Realistic male occupations: {', '.join(m_pool[:10])}")

        # Zone dynamics
        zone_key = region.lower().replace(" ", "_")
        zone_map = {
            "colombo": "colombo_western", "kandy": "central_hill_country",
            "galle": "southern", "jaffna": "northern_jaffna_vanni",
            "batticaloa": "eastern", "nuwara_eliya": "central_hill_country",
            "ratnapura": "colombo_western", "mixed": None,
        }
        zone_data = reality["zone_dynamics"].get(zone_map.get(zone_key, zone_key))
        if zone_data:
            occ_lines.append(f"Zone women's work norms: {zone_data.get('women_work_norms', 'Variable by ethnicity')}")

        # Ethnicity and plantation
        demo = reality["demographics_ethnicity"]
        occ_lines.append(f"Ethnicity: {demo['sinhalese']} / {demo['sri_lankan_tamil']} / {demo['malaiyaha_tamil']} / {demo['muslim_moor']}")

        plant = reality["plantation_tamil_reality"]
        occ_lines.append(f"Plantation Tamil: {plant['history']} Living: {plant['living_conditions'][:100]}... {plant['distinct_from_jaffna']}")

        # Gender-occupation constraints
        rules = reality["gender_occupation_rules"]
        occ_lines.append("Gender-occupation constraints:")
        for rule in rules["universal"][:5]:
            occ_lines.append(f"  - {rule}")

        # Crisis and political context
        crisis = reality["economic_crisis_2022"]
        occ_lines.append(f"2022 crisis: {crisis['overview'][:150]}...")
        occ_lines.append(f"IMPORTANT: {crisis['agent_note']}")

        pol = reality["political_transformation_2024"]
        occ_lines.append(f"Political: {pol['npp_victory']}")

        war = reality["civil_war_legacy"]
        occ_lines.append(f"War legacy: {war['agent_note']}")

        macro = reality["macro_labor_facts"]
        occ_lines.append(f"Labor: Female LFPR {macro['female_lfpr']}. Poverty: {macro['poverty_rate']}. Youth unemployment: {macro['unemployment_rate']}")

        return "\n".join(occ_lines)

    @staticmethod
    def _get_nepal_occupation_context(segment: str, region: str, gender: str = "random") -> str:
        """Build Nepal-specific occupation, caste, and geography context for the LLM prompt."""
        reality = NEPAL_OCCUPATIONAL_REALITY

        if gender == "female" or (gender == "random" and segment in ("women",)):
            occ_pools = reality["female_occupations"]
        elif gender == "male":
            occ_pools = reality["male_occupations"]
        else:
            occ_pools = None

        segment_occ_map_f = {
            "rural": "agricultural_rural", "urban_working": "urban_working_class",
            "middle_class": "middle_professional", "corporate": "corporate_professional",
            "migration_workers": "overseas_migrant", "students": "urban_working_class",
            "women": "agricultural_rural", "elderly": "middle_professional",
        }
        segment_occ_map_m = {
            "rural": "agricultural", "urban_working": "transport_services",
            "middle_class": "professional_government", "corporate": "corporate_professional",
            "migration_workers": "overseas_migrant", "students": "transport_services",
            "women": "agricultural", "elderly": "professional_government",
        }

        occ_lines = []
        if occ_pools:
            key = segment_occ_map_f.get(segment, "urban_working_class") if (gender == "female" or segment == "women") else segment_occ_map_m.get(segment, "transport_services")
            pool = occ_pools.get(key, [])
            if pool:
                sample = pool[:15] if len(pool) > 15 else pool
                occ_lines.append(f"Realistic occupations ({gender}): {', '.join(sample)}")
        else:
            f_key = segment_occ_map_f.get(segment, "urban_working_class")
            m_key = segment_occ_map_m.get(segment, "transport_services")
            f_pool = reality["female_occupations"].get(f_key, [])
            m_pool = reality["male_occupations"].get(m_key, [])
            if f_pool:
                occ_lines.append(f"Female occupations: {', '.join(f_pool[:10])}")
            if m_pool:
                occ_lines.append(f"Male occupations: {', '.join(m_pool[:10])}")

        # Zone dynamics
        zone_key = region.lower().replace(" ", "_")
        zone_map = {
            "kathmandu": "kathmandu_valley", "pokhara": "hill_regions",
            "terai": "terai_madhesh", "eastern_hills": "hill_regions",
            "western_hills": "hill_regions", "mountain": "mountain_high_altitude",
            "mixed": None,
        }
        zone_data = reality["geography_zones"].get(zone_map.get(zone_key, zone_key))
        if zone_data:
            occ_lines.append(f"Zone women's work norms: {zone_data.get('women_work_norms', 'Variable by caste/ethnicity')}")

        # Caste-ethnicity rules
        caste = reality["caste_ethnicity_rules"]
        occ_lines.append("Caste-ethnicity shapes occupation:")
        occ_lines.append(f"  - {caste['brahmin_chhetri'][:120]}...")
        occ_lines.append(f"  - {caste['janajati_36_percent'][:120]}...")
        occ_lines.append(f"  - {caste['dalit_13_6_percent'][:120]}...")
        occ_lines.append(f"  - {caste['madhesi_32_percent'][:120]}...")

        # Gender rules
        rules = reality["gender_occupation_rules"]
        occ_lines.append("Gender-occupation constraints:")
        for rule in rules["universal"][:5]:
            occ_lines.append(f"  - {rule}")

        # Political and migration context
        pol = reality["political_context"]
        occ_lines.append(f"Political: {pol['gen_z_september_2025']}")
        occ_lines.append(f"Election: {pol['march_2026_election']}")
        occ_lines.append(f"IMPORTANT: {pol['agent_note']}")

        mig = reality["migration_facts"]
        occ_lines.append(f"Migration: {mig['gulf_malaysia_share']}. {mig['european_explosion']}")

        macro = reality["macro_labor_facts"]
        occ_lines.append(f"Remittance: {macro['remittance_share_gdp']}. {macro['absent_population']}")

        return "\n".join(occ_lines)

    def _build_population_prompt(
        self,
        country: str,
        segment: str,
        region: str,
        scenario_context: str,
        diaspora_region: Optional[str],
        diaspora_context: Optional[str],
    ) -> str:
        settings = COUNTRY_SETTINGS.get(country, COUNTRY_SETTINGS["Bangladesh"])
        region_context = settings["regions"].get(region.lower(), settings["regions"]["mixed"])
        segment_rule = GENERIC_SEGMENT_RULES.get(segment, "The agent should feel like a specific person shaped by class, place, and everyday risk.")
        segment_prior = COUNTRY_SEGMENT_PRIORS.get(country, {}).get(segment, "")
        country_rules = "\n".join(f"- {rule}" for rule in settings["country_rules"])

        diaspora_block = ""
        if diaspora_region:
            diaspora_block = (
                f"\nDiaspora context: {diaspora_context or DIASPORA_REGION_SETTINGS.get(diaspora_region.lower(), DIASPORA_REGION_SETTINGS['mixed'])}\n"
                "- If this person is migration-linked, include current-location abroad or family-remittance obligations in the persona.\n"
                "- Romanized South Asian language mixed with English is acceptable for diaspora identity markers.\n"
            )

        # Country-specific occupational reality injection
        reality_block = ""
        if country == "Bangladesh":
            reality_block = f"""

BANGLADESH OCCUPATIONAL REALITY (use this to select authentic occupation):
{self._get_bangladesh_occupation_context(segment, region)}
"""
        elif country == "India":
            reality_block = f"""

INDIA OCCUPATIONAL REALITY (use this to select authentic occupation):
{self._get_india_occupation_context(segment, region)}
"""
        elif country == "Pakistan":
            reality_block = f"""

PAKISTAN OCCUPATIONAL REALITY (use this to select authentic occupation):
{self._get_pakistan_occupation_context(segment, region)}
"""
        elif country == "Sri Lanka":
            reality_block = f"""

SRI LANKA OCCUPATIONAL REALITY (use this to select authentic occupation):
{self._get_srilanka_occupation_context(segment, region)}
"""
        elif country == "Nepal":
            reality_block = f"""

NEPAL OCCUPATIONAL REALITY (use this to select authentic occupation):
{self._get_nepal_occupation_context(segment, region)}
"""

        # Country-specific name and trust guidance
        if country == "Bangladesh":
            name_guidance = "Bangladesh: 88% Muslim, 10% Hindu, 2% other — weight accordingly. Use authentic Bangla Muslim names like Rahim, Sajjad, Kamal, Ayesha, Halima, Nasreen OR Hindu names like Ratan, Sunil, Rina, Shilpi where appropriate"
            trust_guidance = "Bangladesh post-July 2024: skew LOW across all segments, 2-5 typical for most, 1-3 for students/urban working"
            dialect_guidance = "Bangladesh: match to region — Dhaka standard, Sylheti, Chatgaayan, Noakhali, Barishal, Rangpur"
            occupation_note = "Bangladesh: A woman's occupation MUST match her zone norms. Garments OK in Dhaka, stigmatized in Chittagong/Sylhet for local women. Domestic work = migrant women only.\n- Bangladesh: 84% of employment is informal. Most agents should NOT have formal salaried employment unless corporate or middle_class segment."
        elif country == "India":
            name_guidance = "India: Name MUST reflect community — Hindu upper caste (Sharma, Mishra, Pandey, Iyer), OBC (Yadav, Kurmi, Vishwakarma), Dalit (Jatav, Paswan, Valmiki, Ram), Muslim (Khan, Ansari, Qureshi, Sheikh), Sikh (Singh/Kaur), Christian (Thomas, D'Souza, Fernandes). Caste distribution: ~30% upper, 41% OBC, 16.6% SC, 8.6% ST, 14% Muslim, others — weight accordingly"
            trust_guidance = "India: varies by community — upper-caste Hindu: moderate-high (5-8). Muslim: LOW (2-4) under BJP. Dalit: variable — politically aware, Ambedkarite. OBC: variable. Adivasi: low institutional trust."
            dialect_guidance = "India: Hindi-English mix (Delhi/UP), Bambaiya Hindi (Mumbai), Bengali (Kolkata), Tamil-English (Chennai), Kannada-English (Bangalore), Telugu-English (Hyderabad), Bhojpuri (Bihar migrants), Malayalam (Kerala)"
            occupation_note = "India: Caste shapes occupation — infer from name/occupation, NEVER state explicitly. 81% informal. ASHA/Anganwadi = massive female occupation.\n- India: Domestic work = migrant women from poor states. Rajput/Jat women: extreme restrictions. Kerala women: most empowered."
        elif country == "Pakistan":
            name_guidance = "Pakistan: Name MUST reflect ethnicity — Punjabi biradari surnames (Butt, Chaudhry, Awan, Rajput, Arain, Gujjar, Sheikh, Malik, Jat), Pashtun (Khan, Yousafzai, Afridi, Khattak, Durrani, Wazir), Sindhi (Soomro, Jatoi, Chandio, Laghari, Brohi, Bheel), Baloch (Bugti, Mengal, Raisani, Baloch), Mohajir (Siddiqui, Ansari, Hashmi, Rizvi, Qureshi), Christian (Masih, Gill, Bhatti), Hindu Sindhi (Bheel, Meghwar, Kolhi). Syed = Prophet's lineage (high status). Muhammad/Mohammad as first name very common."
            trust_guidance = "Pakistan: PTI supporters (majority youth/urban): VERY LOW trust (1-3). PML-N/PPP supporters: moderate (4-6). Shia: low (2-4). Ahmadi: ZERO. Christian/Hindu: VERY LOW. Establishment-aligned: higher (5-7)."
            dialect_guidance = "Pakistan: Karachi Urdu (urban Mohajir), Punjabi-influenced Urdu (Lahore), formal Islamabad Urdu-English, Pashto-influenced speech (KP), Seraiki (south Punjab), Sindhi (interior Sindh), Roman Urdu (social media)"
            occupation_note = "Pakistan: Factory work for women is STIGMATIZED (unlike Bangladesh). Home-based work (stitching, food) universally acceptable. KP women: doctor/teacher/LHW only.\n- Pakistan: 72% informal. 77% of women in unpaid care work. Biradari (clan) system shapes Punjab occupations. Sectarian identity shapes safety — Ahmadis must hide, Shia face targeted killing, Christians face blasphemy weapon."
        elif country == "Sri Lanka":
            name_guidance = "Sri Lanka: Name MUST reflect ethnicity — Sinhala Buddhist (Jayawardena, Bandara, Kumara, Dissanayake, Senanayake, Karunaratne), Sinhala Catholic (Silva, Perera, Fernando, de Mel), Sri Lankan Tamil (Nadarajah, Pillai, Rajaratnam, Sellaiah — S. Sivaganesh format), Malaiyaha Tamil (Suppiah, Periyasamy, Kandasamy, Arumugam — South Indian origin names), Muslim Moor (Mohamed, Cader, Hakeem, Salley), Burgher (Jansz, van Dort, Ondaatje). Distribution: 74.9% Sinhala (70% Buddhist + 5% Catholic), 11.2% Lankan Tamil, 4.1% Malaiyaha Tamil, 9.3% Muslim."
            trust_guidance = "Sri Lanka: Sinhala: moderate (4-7) — NPP supporters higher, former Rajapaksa supporters variable. Lankan Tamil: VERY LOW (1-4) — decades of betrayal. Malaiyaha Tamil: LOW (2-4) — 200 years marginalization. Muslim: LOW (2-5) — post-Easter backlash. 2022 crisis lowered trust for ALL."
            dialect_guidance = "Sri Lanka: Sinhala urban (Colombo — English code-switching), formal Sinhala (Kandy), Tamil Jaffna (educated 'pure'), Malaiyaha estate Tamil (South Indian mixing — distinct), Tamil-English (professional), Sinhala-English corporate, Muslim Tamil (Eastern Province)"
            occupation_note = "Sri Lanka: Ethnicity is PRIMARY variable. Tea plucking = Malaiyaha Tamil women. Garments FTZ = young Sinhala women. Domestic work = rural→urban migration. Gulf housemaid = poverty-driven.\n- Sri Lanka: 2022 crisis is shared national trauma — elevated baseline_anxiety for ALL. Malaiyaha Tamil ≠ Jaffna Tamil (different community). War widows (89,000) work from necessity. 24.5% poverty."
        elif country == "Nepal":
            name_guidance = "Nepal: Name MUST reflect caste/ethnicity — Brahmin (Sharma, Poudel, Aryal, Bhatta), Chhetri (Thapa, KC, Khadka, Bista), Newar (Shrestha, Bajracharya, Shakya, Maharjan), Gurung/Magar (Gurung, Pun, Thapa Magar), Rai/Limbu (Rai, Limbu, Subba), Tamang (Tamang, Lama, Moktan), Sherpa (Sherpa — day-names: Ang Tshering, Mingma, Pemba), Tharu (Chaudhary), Dalit Hill (Biswakarma/BK, Pariyar, Sarki), Dalit Terai (Chamar, Musahar, Dom, Paswan), Madhesi (Yadav, Mandal, Jha, Gupta), Muslim (Khan, Ansari). Distribution: ~29% Brahmin-Chhetri, 36% Janajati, 32% Madhesi, 13.6% Dalit."
            trust_guidance = "Nepal post-March 2026: RSP/Balen supporters: hopeful (5-7). Old-guard (UML/Congress/Maoist): low (2-4). Gen Z protesters: carry trauma but empowered (3-6). Dalit: low (2-4). Madhesi: cautiously optimistic (3-5). Gurkha families: moderate (4-6)."
            dialect_guidance = "Nepal: Kathmandu Nepali (urban, English-mixing), standard Nepali (hill), Maithili (Terai Madhesh), Bhojpuri (western Terai), Newari (Kathmandu Valley Newar), Tamang, Sherpa (Tibetan-related), Tharu (Terai indigenous)"
            occupation_note = "Nepal: Remittance = 25% of GDP. Most young men ABSENT. Left-behind women manage everything but not counted as 'employed.' FCHV = significant female occupation.\n- Nepal: Caste + ethnicity + geography = the person. Gurkha = distinct military pathway. Kamaiya legacy (Tharu bonded labor). Dalit 42% below poverty line. Madhesi women most restricted."
        else:
            name_guidance = f"Use authentic real-world personal names appropriate to religion, class, and region of {country}"
            trust_guidance = "Based on segment reality"
            dialect_guidance = f"Match to region in {country}"
            occupation_note = "Keep values internally consistent with the segment and country."

        return f"""Generate one authentic {country} person for an OPS behavioral simulation.

Segment: {segment}
Region: {region}
Scenario context: {scenario_context}

Country-specific region context:
{region_context}

Segment rule:
- {segment_rule}

Country-segment prior (with occupation guidance):
- {segment_prior or "Use country-appropriate class, language, and household pressure patterns."}

Country rules:
{country_rules}

Dialect guidance:
- {settings['dialects']}
{diaspora_block}{reality_block}
Generate a complete OPS persona as valid JSON with ALL of these fields:
- name: {name_guidance}
- age: realistic integer for the segment
- gender: realistic for the segment, usually "male", "female", or "other" if needed
- occupation: SPECIFIC job title from the occupational reality data — not generic. Must be plausible for this person's gender, zone, class, and religion.
- location: specific district/city/locality string appropriate to the region
- trust_government: integer 0-10 ({trust_guidance})
- shame_sensitivity: integer 0-10 based on segment, class, age, and gendered pressure
- primary_fear: specific and personal, not abstract (e.g. "rice price doubles before Ramadan" not "economic instability")
- influence_radius: realistic integer for the segment
- fb_intensity: integer 0-10 realistic for the segment
- dialect: specific speech style for this person ({dialect_guidance})
- income_stability: concrete description of income stability
- rumour_amplifier: boolean true/false based on segment behavior
- baseline_anxiety: number 0-10
- interested_topics: array of recurring topics
- mbti: plausible MBTI shorthand
- bio: exactly 2 sentences written as their social media bio would read
- persona: about 300 words covering daily life, inner fears, social position, family pressure, communication style, and likely reaction patterns

Critical rules:
- All agents must feel like real specific people, not demographic averages.
- Do not output institutions or brand accounts.
- Use the scenario context to sharpen fear, trust, and posting intensity.
- Keep values internally consistent with the segment and country.
- Rural agents should skew toward higher food and transport vulnerability and stronger community pressure.
- Urban working-class agents should show stronger wage, rent, or utility pressure.
- Migration workers should often have remittance obligations and migration anxiety.
- Corporate agents should feel more polished and professionally cautious.
- Students should have high social intensity and rumor exposure.
- Elderly women should have low posting intensity and high shame pressure when appropriate.
- {occupation_note}

Return valid JSON only."""

    def _build_institution_prompt(
        self,
        country: str,
        role_type: str,
        region: str,
        scenario_context: str,
        diaspora_region: Optional[str],
        diaspora_context: Optional[str],
    ) -> str:
        settings = COUNTRY_SETTINGS.get(country, COUNTRY_SETTINGS["Bangladesh"])
        priors = COUNTRY_INSTITUTIONAL_PRIORS.get(country, COUNTRY_INSTITUTIONAL_PRIORS["Bangladesh"])
        region_context = settings["regions"].get(region.lower(), settings["regions"]["mixed"])
        examples = ", ".join(priors.get(role_type, []))
        diaspora_block = ""
        if diaspora_region:
            diaspora_block = (
                f"\nDiaspora context: {diaspora_context or DIASPORA_REGION_SETTINGS.get(diaspora_region.lower(), DIASPORA_REGION_SETTINGS['mixed'])}\n"
                "- The institutional voice should understand cross-border family obligations and remittance-sensitive publics.\n"
            )

        return f"""Generate one authentic {country}-relevant institutional seed voice for an OPS simulation.

Role type: {role_type}
Primary region: {region}
Scenario context: {scenario_context}

Regional context:
{region_context}

Reference examples for naming and style:
- {examples}

Dialect guidance:
- {settings['dialects']}
{diaspora_block}
Generate one complete institutional or expert OPS profile as valid JSON with these fields:
- name: realistic account or public-facing identity appropriate to the role and country
- age: realistic integer, usually 30 for institutional accounts and 35-55 for experts
- gender: "other" for institutional accounts, otherwise realistic
- occupation: specific institutional or expert role
- location: specific city/district/locality string
- trust_government: integer 0-10 consistent with the role
- shame_sensitivity: integer 0-10
- primary_fear: specific institutional concern
- influence_radius: high but realistic integer
- fb_intensity: integer 0-10 consistent with platform use
- dialect: public-facing language style used by this voice
- income_stability: concrete stability description
- rumour_amplifier: boolean
- baseline_anxiety: number 0-10
- interested_topics: array of recurring agenda topics
- mbti: plausible shorthand for tone/style
- bio: exactly 2 sentences written as the account or expert bio
- persona: about 250-320 words covering incentives, reputation risk, communication style, and how this voice frames the scenario

Critical rules:
- This voice must feel like a real institution, newsroom, civic group, or expert that people would actually encounter in {country}.
- It must be more influential than an ordinary household voice.
- GovernmentAgency should sound measured, cautious, and legitimacy-protective.
- MediaOutlet should sound fast, public-facing, and alert to amplification risk.
- Organization should sound advocacy-oriented and community-aware.
- Expert should sound analytical and reputationally cautious, not generic.
- Keep the voice grounded in the scenario rather than speaking in vague policy clichés.

Return valid JSON only."""

    def _build_profile(
        self,
        country: str,
        segment: str,
        agent_index: int,
        region: str,
        profile_data: Dict[str, Any],
        diaspora_region: Optional[str],
    ) -> OasisAgentProfile:
        is_institutional = self._is_institutional_segment(segment)
        name = str(profile_data.get("name") or f"{country} Citizen {agent_index + 1}").strip()
        user_name = self._generate_username(name, agent_index)
        trust = OasisAgentProfile._clamp_int(profile_data.get("trust_government"), 0, 10)
        shame = OasisAgentProfile._clamp_int(profile_data.get("shame_sensitivity"), 0, 10)
        baseline_anxiety = OasisAgentProfile._clamp_float(profile_data.get("baseline_anxiety", 5.0), 0.0, 10.0)

        profile = OasisAgentProfile(
            user_id=agent_index,
            user_name=user_name,
            name=name,
            bio=str(profile_data.get("bio") or f"{name} is part of the {segment} segment in {country}.").strip(),
            persona=str(profile_data.get("persona") or f"{name} is a socially active {segment} citizen in {country}.").strip(),
            karma=random.randint(1500, 8000) if is_institutional else random.randint(500, 4000),
            friend_count=random.randint(120, 600) if is_institutional else random.randint(40, 400),
            follower_count=random.randint(5000, 50000) if is_institutional else random.randint(80, 1200),
            statuses_count=random.randint(500, 4000) if is_institutional else random.randint(80, 1800),
            age=OasisAgentProfile._clamp_int(profile_data.get("age"), 13, 100),
            gender=str(profile_data.get("gender") or ("other" if is_institutional else "other")).strip().lower(),
            mbti=str(profile_data.get("mbti") or random.choice(self.profile_helper.MBTI_TYPES)).strip(),
            country=country,
            location=str(profile_data.get("location") or f"{country} ({region})").strip(),
            profession=str(profile_data.get("occupation") or profile_data.get("profession") or "Unknown").strip(),
            interested_topics=self._coerce_topics(profile_data.get("interested_topics")),
            trust_government=trust,
            shame_sensitivity=shame,
            primary_fear=str(profile_data.get("primary_fear") or "income insecurity").strip(),
            influence_radius=OasisAgentProfile._clamp_int(profile_data.get("influence_radius"), 0, 1_000_000),
            fb_intensity=OasisAgentProfile._clamp_int(profile_data.get("fb_intensity"), 0, 10),
            dialect=str(profile_data.get("dialect") or region).strip(),
            income_stability=str(profile_data.get("income_stability") or "variable").strip(),
            rumour_amplifier=self._coerce_bool(profile_data.get("rumour_amplifier")),
            migration_worker_flag=self._coerce_bool(profile_data.get("migration_worker_flag"), default=segment == "migration_workers"),
            remittance_dependency_flag=self._coerce_bool(
                profile_data.get("remittance_dependency_flag"),
                default=segment == "migration_workers" or bool(diaspora_region),
            ),
            baseline_anxiety=baseline_anxiety,
            source_entity_uuid=f"ops_population_{country.lower().replace(' ', '_')}_{agent_index}",
            source_entity_type=segment,
        )

        if trust is not None:
            profile.current_trust_government = trust
        if shame is not None:
            profile.current_shame_sensitivity = shame

        return profile

    def _generate_fallback_profile(
        self,
        country: str,
        segment: str,
        region: str,
        agent_index: int,
        diaspora_region: Optional[str],
    ) -> Dict[str, Any]:
        settings = COUNTRY_SETTINGS.get(country, COUNTRY_SETTINGS["Bangladesh"])
        gender = random.choice(["male", "female"])

        # Bangladesh uses the occupational reality system for authentic names and jobs
        if country == "Bangladesh":
            bd_names = BANGLADESH_OCCUPATIONAL_REALITY["name_pools"]
            # 88% Muslim, 10% Hindu, 2% Adivasi/other — weighted selection
            religion_roll = random.random()
            if religion_roll < 0.88:
                name_key = f"muslim_{gender}"
            elif religion_roll < 0.98:
                name_key = f"hindu_{gender}"
            else:
                name_key = f"adivasi_{gender}"
            name_list = bd_names.get(name_key, bd_names[f"muslim_{gender}"])
        elif country == "India":
            in_names = INDIA_OCCUPATIONAL_REALITY["name_pools"]
            # India community distribution: ~30% upper Hindu, 41% OBC, 16.6% Dalit, 8.6% Adivasi, 14% Muslim, 1.7% Sikh, 2.3% Christian
            community_roll = random.random()
            if community_roll < 0.30:
                name_key = f"hindu_upper_caste_{gender}"
            elif community_roll < 0.71:
                name_key = f"obc_{gender}"
            elif community_roll < 0.876:
                name_key = f"dalit_{gender}"
            elif community_roll < 0.93:
                name_key = f"adivasi_{gender}"
            elif community_roll < 0.96:
                name_key = f"muslim_{gender}"
            elif community_roll < 0.977:
                name_key = f"sikh_{gender}"
            else:
                name_key = f"christian_{gender}"
            name_list = in_names.get(name_key, in_names[f"obc_{gender}"])
        elif country == "Pakistan":
            pk_names = PAKISTAN_OCCUPATIONAL_REALITY["name_pools"]
            # Pakistan ethnicity: ~45% Punjabi, ~15% Pashtun, ~14% Sindhi, ~8% Mohajir, ~4% Baloch, ~2% Christian, ~2% Hindu, ~2% Hazara, others
            eth_roll = random.random()
            if eth_roll < 0.45:
                name_key = f"muslim_punjabi_{gender}"
            elif eth_roll < 0.60:
                name_key = f"pashtun_{gender}"
            elif eth_roll < 0.74:
                name_key = f"sindhi_{gender}"
            elif eth_roll < 0.82:
                name_key = f"mohajir_{gender}"
            elif eth_roll < 0.86:
                name_key = f"baloch_{gender}"
            elif eth_roll < 0.88:
                name_key = f"christian_{gender}"
            elif eth_roll < 0.90:
                name_key = f"hindu_{gender}"
            elif eth_roll < 0.92:
                name_key = f"hazara_{gender}"
            else:
                name_key = f"muslim_punjabi_{gender}"
            name_list = pk_names.get(name_key, pk_names[f"muslim_punjabi_{gender}"])
        elif country == "Sri Lanka":
            sl_names = SRI_LANKA_OCCUPATIONAL_REALITY["name_pools"]
            # Sri Lanka: 70% Sinhala Buddhist, 5% Sinhala Catholic, 11.2% Lankan Tamil, 4.1% Malaiyaha Tamil, 9.3% Muslim, 0.4% Burgher
            eth_roll = random.random()
            if eth_roll < 0.70:
                name_key = f"sinhala_buddhist_{gender}"
            elif eth_roll < 0.75:
                name_key = f"sinhala_catholic_{gender}"
            elif eth_roll < 0.862:
                name_key = f"sri_lankan_tamil_{gender}"
            elif eth_roll < 0.903:
                name_key = f"malaiyaha_tamil_{gender}"
            elif eth_roll < 0.996:
                name_key = f"muslim_moor_{gender}"
            else:
                name_key = f"burgher_{gender}"
            name_list = sl_names.get(name_key, sl_names[f"sinhala_buddhist_{gender}"])
        elif country == "Nepal":
            np_names = NEPAL_OCCUPATIONAL_REALITY["name_pools"]
            # Nepal: ~12% Brahmin, ~17% Chhetri, ~5% Newar, ~10% Gurung/Magar, ~7% Rai/Limbu, ~5% Tamang, ~3% Sherpa, ~5% Tharu, ~7% Dalit Hill, ~7% Dalit Terai, ~15% Madhesi upper, ~4% Muslim, others
            eth_roll = random.random()
            if eth_roll < 0.12:
                name_key = f"brahmin_{gender}"
            elif eth_roll < 0.29:
                name_key = f"chhetri_{gender}"
            elif eth_roll < 0.34:
                name_key = f"newar_{gender}"
            elif eth_roll < 0.44:
                name_key = f"gurung_magar_{gender}"
            elif eth_roll < 0.51:
                name_key = f"rai_limbu_{gender}"
            elif eth_roll < 0.56:
                name_key = f"tamang_{gender}"
            elif eth_roll < 0.59:
                name_key = f"sherpa_{gender}"
            elif eth_roll < 0.64:
                name_key = f"tharu_{gender}"
            elif eth_roll < 0.71:
                name_key = f"dalit_hill_{gender}"
            elif eth_roll < 0.78:
                name_key = f"dalit_terai_{gender}"
            elif eth_roll < 0.93:
                name_key = f"madhesi_{gender}"
            elif eth_roll < 0.97:
                name_key = f"muslim_{gender}"
            else:
                name_key = f"brahmin_{gender}"
            name_list = np_names.get(name_key, np_names[f"brahmin_{gender}"])
        else:
            name_list = None

        name_pool = {
            "Nepal": {
                "male": ["Suman Karki", "Ramesh Thapa", "Bikash Gurung", "Dipesh Yadav"],
                "female": ["Sita Thapa", "Anjana Koirala", "Mina Gurung", "Rita Yadav"],
            },
            "Sri Lanka": {
                "male": ["Nimal Perera", "Suren Fernando", "Sivakumar Rajan", "Kasun Jayasekara"],
                "female": ["Dilani Perera", "Nadeesha Silva", "Kavitha Rajan", "Ishara Fernando"],
            },
        }
        if name_list is None:
            fallback = name_pool.get(country, {"male": ["Citizen"], "female": ["Citizen"]})
            name_list = fallback.get(gender, fallback.get("male", ["Citizen"]))

        # Bangladesh segment-specific job pools from occupational reality data
        if country == "Bangladesh":
            bd_occ = BANGLADESH_OCCUPATIONAL_REALITY
            bd_f_occ = bd_occ["female_occupations"]
            bd_m_occ = bd_occ["male_occupations"]
            bd_job_pool = {
                "rural": {
                    "male": ["paddy farmer — own land", "sharecropper — bargadar", "agricultural day laborer — hari", "fish farmer — pond aquaculture", "river fisherman", "char land farmer", "livestock and dairy farmer", "vegetable farmer", "jute farmer", "irrigation pump operator"],
                    "female": ["subsistence paddy farmer (own small plot)", "agricultural day laborer", "homestead poultry farmer", "vegetable cultivator (homestead garden)", "goat and cattle rearing", "shrimp peeling shed worker (Khulna)", "rice husking and processing", "fish drying worker (coastal)", "unpaid family agricultural labor", "jute processing worker"],
                },
                "urban_working": {
                    "male": ["CNG auto-rickshaw driver", "battery-powered rickshaw driver", "garments cutting master", "garments ironing and pressing worker", "construction mason — rajmistri", "construction day laborer", "security guard", "Pathao motorcycle rider", "foodpanda delivery rider", "tea stall owner", "hotel restaurant cook", "office peon", "market porter"],
                    "female": ["garments sewing machine operator", "garments helper", "garments quality checker", "beauty parlor worker", "domestic helper — part-time", "private school teacher — primary", "NGO field worker — BRAC shasthya shebika", "community health worker", "call center agent", "supermarket sales staff", "street food hawker — pitha and tea", "childcare center worker"],
                },
                "middle_class": {
                    "male": ["government school teacher", "bank officer", "NGO program officer", "journalist — newspaper", "court lawyer — junior advocate", "police sub-inspector", "government office clerk", "pharmaceutical sales representative", "upazila health officer", "coaching center teacher"],
                    "female": ["government primary school teacher", "nurse — government hospital", "NGO program officer", "microfinance branch manager", "bank clerk", "college lecturer", "pharmacist", "private tutor", "government office clerk", "journalist — online portal"],
                },
                "corporate": {
                    "male": ["software engineer — tech company", "corporate executive — manager", "commercial banker — senior officer", "doctor — senior consultant", "lawyer — high court advocate", "university professor", "engineer — BUET-trained", "real estate developer", "garments factory owner", "tech startup founder"],
                    "female": ["doctor — MBBS", "software developer", "banker — officer grade", "corporate manager — HR", "university lecturer", "lawyer — district court", "NGO senior management", "development consultant — World Bank", "architect", "engineer — civil"],
                },
                "migration_workers": {
                    "male": ["construction laborer — Saudi Arabia", "construction project worker — Qatar", "domestic driver — UAE", "security guard — Bahrain", "factory worker — Malaysia", "cleaning worker — Qatar", "restaurant worker — Italy", "agricultural worker — Saudi Arabia", "ship crew", "manpower agent — dalal"],
                    "female": ["domestic worker — Saudi Arabia", "domestic worker — UAE", "domestic worker — Kuwait", "garments factory worker — Jordan EPZ", "factory worker — Malaysia", "hotel worker — Maldives"],
                },
                "students": {
                    "male": ["university student", "college student — HSC level", "private university student", "coaching student", "madrasa student — qawmi", "Pathao rider (student)", "freelancer — graphic design", "polytechnic student"],
                    "female": ["university student", "college student — HSC level", "private university student", "coaching student", "madrasa student — girls section", "online freelancer — data entry", "F-commerce seller (student)"],
                },
                "women": {
                    "male": [],  # Not applicable
                    "female": ["home-based tailor", "nakshi kantha embroiderer", "hand loom weaver (Tangail)", "domestic helper — full-time live-in", "brick field worker — seasonal", "vegetable vendor — bazaar hawker", "waste picker and recycler", "garments worker — sewing operator", "beauty parlor owner", "F-commerce seller", "pitha maker for local market"],
                },
                "elderly": {
                    "male": ["retired government teacher", "retired trader", "retired imam", "elder family caretaker", "pensioner — government service", "village elder — matbar", "retired army subedar"],
                    "female": ["retired teacher", "elder family caretaker", "pensioner — government service", "community volunteer — senior", "home-based poultry manager"],
                },
            }
            segment_jobs = bd_job_pool.get(segment, bd_job_pool["middle_class"])
            job_list = segment_jobs.get(gender, segment_jobs.get("male", ["community member"]))
            if not job_list:
                job_list = segment_jobs.get("female", segment_jobs.get("male", ["community member"]))
        elif country == "India":
            in_job_pool = {
                "rural": {
                    "male": ["farmer — marginal holding", "agricultural day laborer", "NREGA worker", "cattle and dairy farmer", "fisherman — freshwater", "tea garden worker (Assam — Adivasi)", "sugarcane cutter (Maharashtra migrant)", "toddy tapper (Kerala)", "poultry farmer", "tractor driver"],
                    "female": ["unpaid family farm worker", "agricultural day laborer", "NREGA worker", "ASHA health worker", "anganwadi worker", "tea garden plucker (Assam/WB — Adivasi)", "bidi roller (home-based — Dalit/Muslim)", "cotton picker (seasonal)", "self help group member", "tendu leaf collector (tribal — seasonal)"],
                },
                "urban_working": {
                    "male": ["auto-rickshaw driver", "e-rickshaw driver", "Swiggy delivery rider", "Zomato delivery rider", "construction laborer (migrant)", "security guard", "hotel restaurant cook", "office peon", "garments factory worker", "Ola/Uber driver", "municipal sweeper (Dalit)", "roadside food vendor", "porter — railway station"],
                    "female": ["domestic worker — maid (migrant from UP/Bihar)", "garments factory worker (Tirupur/Bangalore)", "ASHA health worker", "anganwadi worker", "construction laborer — carrying loads", "rag picker / waste sorter (Dalit)", "beauty parlor worker", "private school teacher (low pay)", "call center agent", "retail sales staff", "vegetable vendor — street hawker", "bidi roller"],
                },
                "middle_class": {
                    "male": ["government school teacher", "bank officer (SBI/PNB — IBPS exam)", "police sub-inspector", "army jawan", "journalist — regional newspaper", "court lawyer — junior advocate", "government clerk (SSC exam)", "pharmaceutical sales representative", "railway clerk", "LIC insurance agent"],
                    "female": ["government school teacher", "nurse — government hospital (BSc Nursing)", "bank clerk (IBPS exam)", "NGO program officer", "government administrative staff (state PSC)", "microfinance field officer", "self help group leader (NRLM)", "police constable", "journalist — regional media", "private tutor"],
                },
                "corporate": {
                    "male": ["software engineer — IT (TCS/Infosys/Wipro/startup)", "corporate executive — manager", "doctor — senior consultant (Apollo/Fortis)", "chartered accountant", "lawyer — high court advocate", "university professor (IIT/IIM faculty)", "investment banker", "startup founder", "real estate developer", "engineer — IIT-trained"],
                    "female": ["software engineer — IT", "doctor — MBBS/MD", "corporate manager — HR/marketing", "chartered accountant", "IAS/IPS officer (UPSC)", "lawyer — advocate", "university professor", "media professional — TV anchor", "architect", "startup founder"],
                },
                "migration_workers": {
                    "male": ["construction laborer — Gulf (Saudi/UAE/Qatar)", "domestic driver — Gulf", "factory worker — Malaysia", "IT professional — USA (H1B)", "restaurant/hotel worker — Gulf", "truck driver — Gulf", "seafarer / merchant navy", "agricultural worker — Gulf"],
                    "female": ["nurse abroad — Gulf/UK/USA (Kerala)", "domestic worker — Gulf (Saudi/UAE)", "IT professional — USA (H1B/H4)", "doctor — UK NHS/USA", "care worker — elderly care (Israel/Gulf)"],
                },
                "students": {
                    "male": ["university student", "IIT/NIT aspirant (Kota coaching)", "UPSC aspirant", "engineering student", "medical student", "Swiggy/Zomato rider (student)", "polytechnic student", "government exam aspirant (SSC/banking)"],
                    "female": ["university student", "medical student", "engineering student", "UPSC aspirant", "government exam aspirant", "nursing student", "private university student"],
                },
                "women": {
                    "male": [],
                    "female": ["ASHA health worker", "anganwadi worker", "domestic worker — maid (migrant)", "bidi roller (Dalit/Muslim home-based)", "agricultural day laborer", "NREGA worker", "garments factory worker (Tirupur)", "chikan embroidery worker (Lucknow Muslim)", "self help group leader", "construction laborer — carrying loads", "vegetable vendor"],
                },
                "elderly": {
                    "male": ["retired government teacher", "retired army jawan/subedar", "retired bank officer", "retired shopkeeper/trader", "pensioner — government", "village sarpanch/elder", "retired priest/pandit"],
                    "female": ["retired teacher", "elder family caretaker", "pensioner — government", "self help group elder", "retired nurse"],
                },
            }
            segment_jobs = in_job_pool.get(segment, in_job_pool["middle_class"])
            job_list = segment_jobs.get(gender, segment_jobs.get("male", ["community member"]))
            if not job_list:
                job_list = segment_jobs.get("female", segment_jobs.get("male", ["community member"]))
        elif country == "Pakistan":
            pk_job_pool = {
                "rural": {
                    "male": ["wheat farmer", "cotton farmer", "rice farmer (basmati)", "sugarcane farmer", "livestock herder (pastoral)", "dairy farmer (buffalo milk)", "agricultural day laborer", "fisherman (Sindh coast)", "date farmer (Balochistan)", "tractor operator"],
                    "female": ["cotton picker (seasonal — women and children)", "livestock management at home (goats, cattle)", "home-based embroidery (phulkari, mirror work)", "lady health worker (LHW)", "home-based food preparation", "agricultural day laborer (Sindh — bonded conditions)"],
                },
                "urban_working": {
                    "male": ["auto-rickshaw driver", "chingchi driver", "Careem/inDriver driver", "foodpanda/Bykea delivery rider", "construction mason — mistri", "construction laborer — mazdoor", "security guard", "textile factory worker (Faisalabad)", "sports goods worker (Sialkot)", "kiryana (grocery) shop owner", "hotel/restaurant cook", "auto mechanic", "mobile phone repair", "pharmaceutical sales rep (MR)"],
                    "female": ["private school teacher (Rs 8,000-25,000/month)", "beauty parlor worker", "home-based tailoring (stitching shalwar kameez)", "home-based food business (catering/baking — social media)", "nurse (hospital)", "call center agent (Lahore, Karachi)", "domestic helper (poorest — often Christian)", "factory worker (textiles — stigmatized)"],
                },
                "middle_class": {
                    "male": ["government teacher (NTS)", "bank officer (HBL, UBL, MCB, Meezan)", "police officer", "army officer (PMA Kakul)", "CSS officer (Pakistan Administrative Service)", "doctor (government hospital)", "engineer (government — PWD, NHA, WAPDA)", "university professor (HEC)", "lawyer (district court)", "journalist (newspaper)"],
                    "female": ["government teacher (PPSC)", "nurse (growing sector)", "bank officer", "doctor (STRONG demand — female patients MUST see female)", "call center agent", "NGO worker", "IT freelancer (graphic design, content)", "university lecturer", "pharmacist", "lawyer (growing)"],
                },
                "corporate": {
                    "male": ["software developer (10Pearls, Systems Ltd, Netsol)", "corporate executive (Unilever, Engro, Lucky Group)", "chartered accountant (ICAP)", "lawyer (Supreme Court)", "doctor (Aga Khan, Shifa — private)", "media professional (TV anchor — Geo, ARY)", "startup founder", "architect"],
                    "female": ["software developer / IT professional", "corporate professional (MNC)", "doctor (specialist — gynecology, pediatrics)", "media and journalism", "fashion designer (Karachi)", "banker (officer grade)", "university professor", "lawyer (Karachi, Lahore)"],
                },
                "migration_workers": {
                    "male": ["construction worker — Saudi Arabia", "construction worker — UAE", "construction worker — Qatar", "driver — Gulf household", "factory worker — Malaysia", "restaurant worker — UK", "taxi driver — London", "IT professional — UK/Canada/UAE", "doctor — UK NHS", "student-worker — Canada/Australia"],
                    "female": ["domestic worker — Saudi Arabia/UAE", "nurse — Gulf countries", "doctor — UK NHS", "IT professional — UK/Canada", "call center — Dubai"],
                },
                "students": {
                    "male": ["university student", "CSS aspirant", "medical student (MDCAT)", "engineering student (NUST/GIKI/UET)", "madrasa student (qawmi/alia)", "O/A levels student (elite)", "IT freelancer (student)", "Bykea/foodpanda rider (student)"],
                    "female": ["university student", "medical student", "CSS aspirant", "O/A levels student", "IT freelancer (student)", "home-based tutor"],
                },
                "women": {
                    "male": [],
                    "female": ["home-based embroidery and stitching", "home-based tailoring", "home-based food business (social media)", "lady health worker (LHW)", "beauty parlor owner", "private school teacher", "domestic helper — maid (poorest)", "brick kiln worker (bonded — Christian/Hindu)", "cotton picker (seasonal)"],
                },
                "elderly": {
                    "male": ["retired CSS/PCS officer (pensioned)", "retired army officer (pension + cantonment)", "retired teacher", "retired shopkeeper", "retired imam", "village elder/numberdar"],
                    "female": ["retired teacher", "elder family caretaker", "pensioner — government", "community elder"],
                },
            }
            segment_jobs = pk_job_pool.get(segment, pk_job_pool["middle_class"])
            job_list = segment_jobs.get(gender, segment_jobs.get("male", ["community member"]))
            if not job_list:
                job_list = segment_jobs.get("female", segment_jobs.get("male", ["community member"]))
        elif country == "Sri Lanka":
            sl_job_pool = {
                "rural": {
                    "male": ["paddy farmer", "fisherman — traditional outrigger", "fisherman — mechanized trawler", "coconut toddy tapper", "cinnamon plantation worker", "vegetable farmer (commercial — upcountry)", "rubber tapper", "tea estate worker — male (factory processing)", "prawn/shrimp farmer (lagoon)"],
                    "female": ["tea plucker (Malaiyaha Tamil — Rs 1,350/day)", "rubber tapper", "cinnamon peeler (Galle/Matara — paid by weight)", "paddy transplanting laborer", "fish processor (dried fish — coastal)", "fish seller (market women)", "palmyra product maker (Jaffna — toddy, jaggery)", "coconut processing worker", "vegetable farmer (hill country)"],
                },
                "urban_working": {
                    "male": ["tuk-tuk (three-wheeler) driver", "bus driver (SLTB and private)", "bus conductor", "construction laborer", "construction mason", "hotel and tourism worker", "PickMe/Uber driver", "delivery rider (PickMe Food)", "shopkeeper", "fish vendor", "garments factory worker (male — cutting, technical)"],
                    "female": ["garments FTZ worker — sewing operator (Katunayake/Biyagama — young Sinhala)", "domestic worker (rural → Colombo migration)", "beauty parlor worker", "small shopkeeper", "home-based sewing and tailoring", "home-based food preparation (short eats — wadai, rolls)", "market vendor", "hotel housekeeping", "retail staff (Odel, NOLIMIT)"],
                },
                "middle_class": {
                    "male": ["government SLAS officer", "police officer", "military officer/soldier", "government school teacher", "university lecturer", "doctor (government hospital)", "lawyer", "accountant (CIMA/ACCA)", "bank officer (BOC, People's Bank, Commercial Bank)"],
                    "female": ["government school teacher (Sinhala/Tamil/English medium)", "nurse (government hospital — many migrating abroad)", "midwife (public health midwife — PHM)", "bank clerk/officer", "government administrative officer (SLAS)", "NGO worker (post-war/post-crisis)", "journalist", "accountant"],
                },
                "corporate": {
                    "male": ["IT professional (WSO2, Virtusa, 99X, IFS)", "corporate executive (John Keells, MAS, Dialog)", "hotel/tourism manager", "tour guide (multi-lingual)", "lawyer", "doctor (private)", "gem dealer"],
                    "female": ["IT professional", "corporate manager (MAS Holdings, Brandix, Dialog)", "doctor", "lawyer", "accountant (CIMA/ACCA)", "architect", "media professional"],
                },
                "migration_workers": {
                    "male": ["construction worker — Gulf (Saudi/UAE/Qatar/Kuwait)", "IT professional — Australia/Canada/UK/Singapore", "doctor — UK NHS/Maldives", "merchant navy seafarer", "hotel worker — Maldives", "factory worker — South Korea (EPS)", "military — UN peacekeeping"],
                    "female": ["domestic worker — Gulf (Saudi/Kuwait/UAE — largest female category)", "nurse abroad (Gulf/UK/Australia/Canada)", "IT professional abroad", "care worker (elderly — Israel/Italy/Japan)", "garments worker abroad (Jordan/Maldives)"],
                },
                "students": {
                    "male": ["university student (Colombo/Peradeniya/Moratuwa)", "A/L student", "IT student", "medical student"],
                    "female": ["university student", "A/L student", "nursing student", "IT student", "medical student"],
                },
                "women": {
                    "male": [],
                    "female": ["tea plucker (Malaiyaha Tamil — estate)", "garments FTZ worker (Sinhala — boarding house)", "domestic worker (rural → Colombo)", "Gulf domestic worker (poverty-driven)", "war widow — multiple informal jobs (north/east)", "cinnamon peeler", "fish processor/seller", "home-based tailoring", "beauty parlor worker", "NGO worker (post-war areas)"],
                },
                "elderly": {
                    "male": ["retired government teacher", "retired military (large standing army)", "retired bank officer", "retired fisherman", "temple community elder"],
                    "female": ["retired teacher", "retired nurse", "elder family caretaker", "retired plantation worker (inadequate pension)"],
                },
            }
            segment_jobs = sl_job_pool.get(segment, sl_job_pool["middle_class"])
            job_list = segment_jobs.get(gender, segment_jobs.get("male", ["community member"]))
            if not job_list:
                job_list = segment_jobs.get("female", segment_jobs.get("male", ["community member"]))
        elif country == "Nepal":
            np_job_pool = {
                "rural": {
                    "male": ["subsistence farmer — terraced rice and maize", "livestock herder (goats, buffalo)", "Gulf construction worker (absent — Saudi/Qatar/UAE)", "trekking guide (seasonal — Annapurna/Everest)", "porter (trekking — carrying 30kg+ loads)", "Gurkha soldier (British/Indian Army)", "seasonal labor in India (open border)", "bus/jeep driver (mountain roads)", "carpenter", "stonemason"],
                    "female": ["subsistence farmer (managing alone — husband abroad)", "livestock keeper (goats, buffalo, cattle)", "FCHV — Female Community Health Volunteer (Rs 3,000/month)", "remittance household manager", "tea house/lodge worker (trekking routes)", "porter — female (doko baskets)", "carpet/dhaka weaver", "agricultural day laborer (Terai — paddy)", "brick kiln worker (Terai — Tharu/Dalit)"],
                },
                "urban_working": {
                    "male": ["taxi/Pathao driver (Kathmandu — ex-Gulf returnee common)", "construction worker", "shopkeeper", "restaurant worker", "hotel/tourism worker", "motorcycle taxi driver", "handicraft seller (Thamel tourist market)", "delivery rider"],
                    "female": ["domestic worker in Kathmandu (from rural — Tamang/Dalit/Terai)", "beauty parlor worker", "restaurant worker", "hotel housekeeping", "small shopkeeper", "market vendor", "home-based tailoring and embroidery", "garment factory worker"],
                },
                "middle_class": {
                    "male": ["government officer (Lok Sewa Aayog exam)", "teacher (government school)", "police officer", "Nepal Army officer", "bank clerk (Nabil, NIC Asia, Sanima)", "NGO worker", "journalist", "lawyer", "doctor (government hospital)"],
                    "female": ["government school teacher (significant female occupation)", "nurse (government hospital — many migrating abroad)", "FCHV coordinator (district)", "NGO program officer", "bank clerk", "government officer (Lok Sewa)", "journalist"],
                },
                "corporate": {
                    "male": ["IT professional (Kathmandu)", "corporate executive (Chaudhary Group, Ncell)", "hotel/tourism manager", "doctor (private)", "lawyer", "startup founder"],
                    "female": ["IT professional", "corporate professional", "doctor", "lawyer", "journalist", "hotel/tourism manager"],
                },
                "migration_workers": {
                    "male": ["construction worker — Gulf (Saudi/Qatar/UAE/Kuwait — kafala)", "factory worker — Malaysia", "factory worker — South Korea (EPS — well-paid, competitive)", "factory/warehouse — Romania/Croatia/Poland (emerging)", "seasonal labor — India (open border)", "Gurkha — British Army (Gurung/Magar/Rai/Limbu)", "student-worker — Australia/UK/Canada"],
                    "female": ["domestic worker — Gulf (Saudi/Kuwait/UAE — abuse documented)", "factory worker abroad (Malaysia)", "nurse abroad (Gulf/UK)", "care worker abroad (Israel/Japan)"],
                },
                "students": {
                    "male": ["university student (TU, KU, Pokhara)", "IT student", "medical student", "Pathao delivery rider (student)", "government exam aspirant (Lok Sewa)"],
                    "female": ["university student", "nursing student", "IT student", "medical student"],
                },
                "women": {
                    "male": [],
                    "female": ["remittance household manager (husband abroad — manages farm, children, elderly)", "FCHV health volunteer", "subsistence farmer (alone)", "domestic worker (Kathmandu — from rural)", "domestic worker Gulf (Saudi/Kuwait)", "brick kiln worker (Terai — Tharu/Dalit)", "Madhubani art painter (Terai)", "carpet weaver", "beauty parlor owner"],
                },
                "elderly": {
                    "male": ["retired government teacher", "retired Nepal Army", "retired Gurkha (British/Indian — pension)", "retired farmer", "village elder"],
                    "female": ["retired teacher", "elder family caretaker", "retired farmer", "community elder"],
                },
            }
            segment_jobs = np_job_pool.get(segment, np_job_pool["middle_class"])
            job_list = segment_jobs.get(gender, segment_jobs.get("male", ["community member"]))
            if not job_list:
                job_list = segment_jobs.get("female", segment_jobs.get("male", ["community member"]))
        else:
            generic_job_pool = {
                "rural": ["small farmer", "fish trader", "village shopkeeper", "day laborer"],
                "urban_working": ["garments worker", "rickshaw driver", "CNG driver", "market helper"],
                "middle_class": ["school teacher", "office clerk", "NGO field officer", "bank assistant"],
                "corporate": ["operations manager", "HR executive", "software analyst", "brand manager"],
                "migration_workers": ["construction worker abroad", "domestic worker abroad", "factory worker abroad", "airport cleaner abroad"],
                "students": ["university student", "college student", "private university student", "coaching student"],
                "women": ["home-based tailor", "school mother", "informal vendor", "community volunteer"],
                "elderly": ["retired school staff", "retired trader", "elder family caretaker", "pensioner"],
            }
            job_list = generic_job_pool.get(segment, generic_job_pool["middle_class"])

        name = random.choice(name_list)
        job = random.choice(job_list)
        location = diaspora_region or f"{country} ({region})"

        # Bangladesh-specific dialect mapping by region
        if country == "Bangladesh":
            bd_dialect_map = {
                "dhaka": "standard Dhaka Bangla",
                "chittagong": "Chatgaayan",
                "sylhet": "Sylheti",
                "rajshahi": "Rajshahi regional Bangla",
                "barisal": "Barishal speech",
                "khulna": "Khulna regional Bangla",
                "rangpur": "Rangpur dialect",
                "comilla": "Noakhali-influenced Bangla",
                "mymensingh": "Mymensingh regional Bangla",
                "mixed": random.choice(["standard Dhaka Bangla", "Chatgaayan", "Sylheti", "Barishal speech", "Rangpur dialect"]),
            }
            dialect_default = bd_dialect_map.get(region.lower(), "standard Dhaka Bangla")
        elif country == "India":
            in_dialect_map = {
                "delhi": random.choice(["Hindi-English mix", "Hinglish corporate-speak", "Bhojpuri-influenced Hindi"]),
                "mumbai": random.choice(["Bambaiya Hindi", "Marathi-English mix", "Hindi-English mix"]),
                "kolkata": random.choice(["Bengali", "Bengali-English mix", "Hindi (migrant)"]),
                "chennai": random.choice(["Tamil-English mix", "Tamil formal", "English (IT sector)"]),
                "bengaluru": random.choice(["Kannada-English mix", "English (IT sector)", "Hindi-English (migrant)"]),
                "hyderabad": random.choice(["Telugu-English mix", "Deccani Urdu-Telugu", "English (IT sector)"]),
                "lucknow": random.choice(["Awadhi-influenced Hindi", "Urdu-Hindi mix (Lucknow)", "Bhojpuri (Bihar migrant)"]),
                "kerala": random.choice(["Malayalam", "Malayalam-English mix"]),
                "punjab": random.choice(["Punjabi-Hindi mix", "Punjabi", "Haryanvi Hindi"]),
                "rajasthan": random.choice(["Rajasthani-Hindi mix", "Marwari", "Gujarati (Gujarat)"]),
                "northeast": random.choice(["English (NE)", "Assamese", "Hindi-English (NE)"]),
                "mixed": random.choice(["Hindi-English mix", "Tamil-English mix", "Bengali", "Bambaiya Hindi", "Malayalam"]),
            }
            dialect_default = in_dialect_map.get(region.lower(), "Hindi-English mix")
        elif country == "Pakistan":
            pk_dialect_map = {
                "karachi": random.choice(["Karachi Urdu (Mohajir)", "Urdu-English mix", "Pashto-influenced Urdu (Pashtun community)"]),
                "lahore": random.choice(["Punjabi-influenced Urdu", "Lahori Punjabi", "Urdu-English mix"]),
                "islamabad": random.choice(["formal Islamabad Urdu-English", "Potohari-influenced Urdu"]),
                "peshawar": random.choice(["Pashto-influenced speech", "Pashto"]),
                "quetta": random.choice(["Balochi", "Pashto", "Hazaragi Persian-influenced"]),
                "multan": random.choice(["Seraiki", "Multani Punjabi"]),
                "interior_sindh": random.choice(["Sindhi", "Sindhi-Urdu mix"]),
                "faisalabad": "Punjabi-influenced Urdu",
                "mixed": random.choice(["Punjabi-influenced Urdu", "Karachi Urdu", "Pashto-influenced speech", "Seraiki", "Sindhi"]),
            }
            dialect_default = pk_dialect_map.get(region.lower(), "Punjabi-influenced Urdu")
        elif country == "Sri Lanka":
            sl_dialect_map = {
                "colombo": random.choice(["Sinhala-English code-switching", "Sinhala urban (Colombo)", "English (corporate)"]),
                "kandy": random.choice(["formal Sinhala (Kandyan)", "Malaiyaha estate Tamil"]),
                "galle": "Sinhala (southern)",
                "jaffna": random.choice(["Tamil Jaffna (educated)", "Tamil-English mix"]),
                "batticaloa": random.choice(["Tamil (eastern)", "Muslim Tamil (eastern)"]),
                "nuwara_eliya": random.choice(["Malaiyaha estate Tamil (South Indian mixing)", "Sinhala (hill country)"]),
                "ratnapura": "Sinhala (Sabaragamuwa)",
                "mixed": random.choice(["Sinhala-English mix", "Tamil Jaffna", "Malaiyaha estate Tamil", "Sinhala urban"]),
            }
            dialect_default = sl_dialect_map.get(region.lower(), "Sinhala urban")
        elif country == "Nepal":
            np_dialect_map = {
                "kathmandu": random.choice(["Kathmandu Nepali (urban, English-mixing)", "Newari/Nepal Bhasa", "Nepali-English mix"]),
                "pokhara": "Nepali (Gandaki — Gurung influence)",
                "terai": random.choice(["Maithili", "Bhojpuri", "Tharu", "Hindi-Nepali mix"]),
                "eastern_hills": random.choice(["Nepali (eastern hill)", "Rai Kiranti-influenced Nepali", "Limbu-influenced Nepali"]),
                "western_hills": "Nepali (western hill)",
                "mountain": random.choice(["Sherpa (Tibetan-related)", "Nepali (mountain)"]),
                "mixed": random.choice(["Kathmandu Nepali", "Maithili", "Nepali (hill)", "Nepali-English mix"]),
            }
            dialect_default = np_dialect_map.get(region.lower(), "Nepali (standard)")
        else:
            dialect_default = settings["dialects"].split(" such as ")[-1].split(",")[0]

        # Country-specific location mapping
        if country == "Bangladesh":
            bd_location_map = {
                "dhaka": random.choice(["Mirpur, Dhaka", "Mohammadpur, Dhaka", "Uttara, Dhaka", "Dhanmondi, Dhaka", "Gulshan, Dhaka", "Gazipur Industrial Area", "Savar, Dhaka", "Keraniganj, Dhaka", "Korail Slum, Dhaka", "Narayanganj"]),
                "chittagong": random.choice(["Chittagong port area", "Sitakunda, Chittagong", "Chittagong EPZ", "Halishahar, Chittagong", "Sadarghat, Chittagong"]),
                "sylhet": random.choice(["Sylhet city", "Moulvibazar", "Sunamganj", "Habiganj"]),
                "rajshahi": random.choice(["Rajshahi city", "Chapainawabganj", "Natore", "Naogaon"]),
                "barisal": random.choice(["Barisal city", "Bhola", "Patuakhali", "Pirojpur"]),
                "khulna": random.choice(["Khulna city", "Satkhira", "Bagerhat", "Jessore"]),
                "rangpur": random.choice(["Rangpur city", "Kurigram", "Gaibandha", "Dinajpur", "Lalmonirhat"]),
                "comilla": random.choice(["Comilla city", "Noakhali", "Feni", "Lakshmipur", "Hatiya Island"]),
                "mixed": random.choice(["Mirpur, Dhaka", "Chittagong port area", "Sylhet city", "Rajshahi city", "Barisal city", "Khulna city", "Rangpur city", "Comilla city"]),
            }
            location = diaspora_region or bd_location_map.get(region.lower(), f"Bangladesh ({region})")
        elif country == "India":
            in_location_map = {
                "delhi": random.choice(["Lajpat Nagar, New Delhi", "Dwarka, Delhi", "Gurgaon, Haryana", "Noida, UP", "Rohini, Delhi", "Chandni Chowk, Old Delhi", "Nehru Place, Delhi", "Greater Noida", "Faridabad", "Shahdara, Delhi"]),
                "mumbai": random.choice(["Andheri, Mumbai", "Dharavi, Mumbai", "Bandra, Mumbai", "Dadar, Mumbai", "Navi Mumbai", "Thane", "Borivali, Mumbai", "Worli, Mumbai", "Pune", "Bhiwandi, Thane"]),
                "kolkata": random.choice(["Salt Lake, Kolkata", "Howrah", "Park Street, Kolkata", "Dum Dum, Kolkata", "Rajarhat, Kolkata", "Barasat", "Murshidabad", "Siliguri"]),
                "chennai": random.choice(["T Nagar, Chennai", "Adyar, Chennai", "Tirupur", "Coimbatore", "Madurai", "Kanchipuram", "Vellore", "Salem"]),
                "bengaluru": random.choice(["Whitefield, Bangalore", "Koramangala, Bangalore", "Electronic City, Bangalore", "Jayanagar, Bangalore", "Mysore", "Mangalore", "Hubli"]),
                "hyderabad": random.choice(["HITEC City, Hyderabad", "Secunderabad", "Gachibowli, Hyderabad", "Vijayawada, AP", "Visakhapatnam, AP", "Guntur, AP", "Warangal, Telangana"]),
                "lucknow": random.choice(["Hazratganj, Lucknow", "Aminabad, Lucknow", "Varanasi", "Allahabad (Prayagraj)", "Kanpur", "Agra", "Gorakhpur", "Aligarh", "Patna", "Muzaffarpur, Bihar", "Gaya, Bihar"]),
                "kerala": random.choice(["Trivandrum (Thiruvananthapuram)", "Kochi (Ernakulam)", "Kozhikode (Calicut)", "Thrissur", "Alleppey (Alappuzha)", "Kollam", "Kannur"]),
                "punjab": random.choice(["Ludhiana, Punjab", "Amritsar, Punjab", "Chandigarh", "Jalandhar, Punjab", "Bathinda, Punjab", "Karnal, Haryana", "Panipat, Haryana"]),
                "rajasthan": random.choice(["Jaipur", "Jodhpur", "Udaipur", "Surat, Gujarat", "Ahmedabad, Gujarat", "Bhopal, MP", "Indore, MP", "Raipur, Chhattisgarh"]),
                "northeast": random.choice(["Guwahati, Assam", "Shillong, Meghalaya", "Imphal, Manipur", "Dimapur, Nagaland", "Aizawl, Mizoram", "Agartala, Tripura", "Itanagar, Arunachal"]),
                "mixed": random.choice(["Lajpat Nagar, New Delhi", "Andheri, Mumbai", "Salt Lake, Kolkata", "T Nagar, Chennai", "Whitefield, Bangalore", "HITEC City, Hyderabad", "Trivandrum", "Ludhiana, Punjab"]),
            }
            location = diaspora_region or in_location_map.get(region.lower(), f"India ({region})")
        elif country == "Pakistan":
            pk_location_map = {
                "karachi": random.choice(["Clifton, Karachi", "SITE Industrial Area, Karachi", "Korangi, Karachi", "North Nazimabad, Karachi", "Gulshan-e-Iqbal, Karachi", "Saddar, Karachi", "Orangi Town, Karachi", "Malir, Karachi", "Defence (DHA), Karachi"]),
                "lahore": random.choice(["Gulberg, Lahore", "Model Town, Lahore", "Anarkali, Lahore", "DHA Lahore", "Johar Town, Lahore", "Ichra, Lahore", "Faisalabad", "Sialkot", "Gujranwala"]),
                "islamabad": random.choice(["F-7, Islamabad", "G-9, Islamabad", "Blue Area, Islamabad", "Rawalpindi Cantonment", "Rawalpindi City", "Bahria Town, Rawalpindi"]),
                "peshawar": random.choice(["Peshawar city", "Hayatabad, Peshawar", "University Town, Peshawar", "Mardan", "Swat", "Abbottabad", "Waziristan (ex-FATA)"]),
                "quetta": random.choice(["Quetta city", "Hazara Town, Quetta", "Gwadar", "Turbat", "Khuzdar", "Ziarat"]),
                "multan": random.choice(["Multan city", "Bahawalpur", "DG Khan", "Rahim Yar Khan", "Rajanpur"]),
                "interior_sindh": random.choice(["Hyderabad", "Sukkur", "Larkana", "Tharparkar", "Mirpurkhas", "Sanghar"]),
                "mixed": random.choice(["Gulberg, Lahore", "North Nazimabad, Karachi", "F-7, Islamabad", "Peshawar city", "Multan city", "Hyderabad, Sindh"]),
            }
            location = diaspora_region or pk_location_map.get(region.lower(), f"Pakistan ({region})")
        elif country == "Sri Lanka":
            sl_location_map = {
                "colombo": random.choice(["Colombo 7, Cinnamon Gardens", "Colombo 11, Pettah", "Colombo 3, Kollupitiya", "Negombo", "Gampaha", "Katunayake FTZ area", "Biyagama", "Kalutara", "Mount Lavinia"]),
                "kandy": random.choice(["Kandy city", "Peradeniya", "Nuwara Eliya", "Matale", "Badulla", "Bandarawela"]),
                "galle": random.choice(["Galle Fort", "Unawatuna", "Mirissa", "Weligama", "Matara", "Hambantota", "Tangalle"]),
                "jaffna": random.choice(["Jaffna city", "Nallur, Jaffna", "Kilinochchi", "Mullaitivu", "Mannar", "Vavuniya"]),
                "batticaloa": random.choice(["Batticaloa city", "Kalmunai", "Ampara", "Sammanthurai", "Trincomalee", "Arugam Bay"]),
                "nuwara_eliya": random.choice(["Nuwara Eliya estate", "Dimbula estate", "Hatton", "Maskeliya", "Bogawantalawa"]),
                "ratnapura": random.choice(["Ratnapura city", "Balangoda", "Embilipitiya", "Kegalle"]),
                "mixed": random.choice(["Colombo 3", "Kandy city", "Galle Fort", "Jaffna city", "Nuwara Eliya", "Batticaloa city"]),
            }
            location = diaspora_region or sl_location_map.get(region.lower(), f"Sri Lanka ({region})")
        elif country == "Nepal":
            np_location_map = {
                "kathmandu": random.choice(["Kathmandu, Bagmati", "Lalitpur (Patan)", "Bhaktapur", "Kirtipur", "Budhanilkantha"]),
                "pokhara": random.choice(["Pokhara, Gandaki", "Gorkha", "Tanahu", "Syangja", "Lamjung"]),
                "terai": random.choice(["Birgunj, Madhesh Province", "Biratnagar, Koshi", "Janakpur, Madhesh", "Nepalgunj, Lumbini", "Dhangadhi, Sudurpashchim", "Butwal, Lumbini", "Bharatpur, Bagmati"]),
                "eastern_hills": random.choice(["Dhankuta, Koshi", "Ilam, Koshi", "Taplejung, Koshi", "Solukhumbu, Koshi", "Bhojpur, Koshi"]),
                "western_hills": random.choice(["Jumla, Karnali", "Surkhet, Karnali", "Dang, Lumbini", "Palpa, Lumbini", "Baglung, Gandaki"]),
                "mountain": random.choice(["Namche Bazaar, Solukhumbu", "Lukla, Solukhumbu", "Jomsom, Mustang", "Manang", "Humla"]),
                "mixed": random.choice(["Kathmandu, Bagmati", "Pokhara, Gandaki", "Birgunj, Madhesh", "Biratnagar, Koshi", "Dhankuta, Koshi", "Namche Bazaar, Solukhumbu"]),
            }
            location = diaspora_region or np_location_map.get(region.lower(), f"Nepal ({region})")

        # Country-specific primary fears and trust_government
        if country == "Bangladesh":
            bd_fears = {
                "rural": ["rice price doubles before Ramadan", "flood destroys standing crop", "fertilizer price spike at planting season", "river erosion takes homestead land", "day-wage work dries up after harvest"],
                "urban_working": ["factory closes without paying dues", "rent increase in Dhaka", "Pathao reduces rider commission", "construction work stops in monsoon", "garments order cancelled — layoff risk"],
                "middle_class": ["school fees increase faster than salary", "government job abolishment", "bank loan default risk", "medical emergency without savings", "coaching center costs for children"],
                "corporate": ["company downsizing after economic slowdown", "career stagnation", "political instability disrupts business", "investment loss", "professional reputation damage on social media"],
                "migration_workers": ["employer withholds passport (kafala)", "recruitment agent cheated — fake visa", "family back home cannot manage without remittance", "contract terminated early — deportation", "dying alone abroad"],
                "students": ["family cannot afford next semester tuition", "job market has nothing after graduation", "friends killed or blinded in July uprising", "coaching center fees drain family savings", "political targeting for activism"],
                "women": ["husband stops sending remittance from abroad", "price of cooking gas and rice", "daughter's marriage dowry pressure", "safety walking to garments factory at dawn", "community gossip about working outside home"],
                "elderly": ["medicine costs exceed pension", "children migrate and leave elderly alone", "loss of family authority with age", "memory of 1974 famine returning", "hospital costs for chronic illness"],
            }
            primary_fear = random.choice(bd_fears.get(segment, bd_fears["urban_working"]))
            trust_gov = random.randint(1, 5) if segment in {"students", "urban_working"} else random.randint(2, 6)
        elif country == "India":
            in_fears = {
                "rural": ["crop failure from drought or flood", "fertilizer and diesel price hike", "NREGA wages delayed by weeks", "medical emergency with no insurance", "children's school fees impossible to pay", "well runs dry — groundwater depleted"],
                "urban_working": ["Swiggy/Zomato cuts delivery commission again", "rent increase forces move to further slum", "construction contractor disappears with wages", "factory lays off without notice", "auto-rickshaw permit revoked", "communal violence disrupts livelihood (Muslim agents)"],
                "middle_class": ["government exam paper leak wastes year of preparation", "EMI default on home or car loan", "private school fee hike", "hospital bill wipes out savings", "son fails engineering entrance despite Kota coaching", "transfer posting to remote district"],
                "corporate": ["IT layoffs — company restructuring", "startup fails — investor pulls out", "H1B visa denied — must return from USA", "career stagnation — passed over for promotion", "LinkedIn reputation damage from controversy"],
                "migration_workers": ["Gulf employer withholds passport (kafala)", "agent cheated — fake job in Saudi", "COVID lockdown stranded again", "family back home cannot manage without remittance", "construction accident abroad — no insurance", "dying alone in Gulf — body repatriation impossible"],
                "students": ["UPSC exam — 5th attempt failed — age bar approaching", "engineering degree but no job — unemployment", "Kota coaching — friend died by suicide from pressure", "exam paper leak — year wasted", "family sold land for coaching fees — cannot fail", "Agniveer short-term military — no permanent job security"],
                "women": ["husband's drinking and violence", "dowry harassment from in-laws", "LPG cylinder price increase — cooking cost", "daughter's safety walking to work/school", "caste-based sexual harassment at workplace (Dalit women)", "ASHA work 12 hours but government says I'm a volunteer not worker"],
                "elderly": ["pension is Rs 200/month — barely buys rice", "hospital costs for diabetes/heart — no insurance", "children migrated — live alone", "joint family breaking down — no one to care", "chronic illness without affordable medicine"],
            }
            primary_fear = random.choice(in_fears.get(segment, in_fears["urban_working"]))
            # India trust varies by community context — we approximate
            trust_gov = random.randint(4, 8) if segment in {"corporate", "middle_class"} else random.randint(2, 6)
        elif country == "Pakistan":
            pk_fears = {
                "rural": ["wheat price spike before Ramadan", "electricity bill doubled — cannot pay", "flood destroys crop again like 2022", "fertilizer too expensive at planting", "feudal landlord takes larger share of harvest", "tube well diesel cost impossible"],
                "urban_working": ["electricity load-shedding stops work", "gas shortage — cannot cook", "Careem/foodpanda cuts commission", "construction work disappears in monsoon", "factory closes without paying wages", "rent increase in Karachi/Lahore"],
                "middle_class": ["CSS exam — 5th attempt — age bar approaching", "school fees increase faster than government salary", "medical emergency wipes out savings", "brain drain — colleagues leaving for Canada/UK", "political instability threatens government job", "EMI default on car/house loan"],
                "corporate": ["IT sector layoffs despite $3.8B exports", "company restructuring after economic crisis", "political instability disrupts business environment", "career stagnation — passed over", "brain drain temptation — offer from Dubai/London"],
                "migration_workers": ["Gulf employer withholds passport (kafala)", "agent cheated — paid Rs 800,000 for fake Saudi visa", "family back home cannot manage without remittance", "deported — lost everything", "dying alone abroad — construction accident", "undocumented in UK — fear of deportation"],
                "students": ["CSS/MDCAT exam — family sold land for coaching fees — cannot fail", "no job after engineering degree — unemployment", "PTI activism led to arrest of friend", "madrasa vs modern education dilemma", "brain drain — half my class wants to leave Pakistan", "exam paper leak — year wasted"],
                "women": ["electricity and gas bill — cooking impossible", "husband abroad stops sending money", "daughter's safety — harassment on street", "blasphemy accusation against family (Christian women)", "forced conversion fear (Hindu women in Sindh)", "community gossip about working outside home"],
                "elderly": ["pension is Rs 15,000/month — inflation destroyed purchasing power", "electricity bill exceeds pension", "children emigrated — live alone", "hospital costs for diabetes/heart", "political chaos — never seen Pakistan this bad", "memory of 1971 and martial law"],
            }
            primary_fear = random.choice(pk_fears.get(segment, pk_fears["urban_working"]))
            # Pakistan post-2022 crisis: trust generally LOW, varies by political identity
            trust_gov = random.randint(1, 4) if segment in {"students", "urban_working"} else random.randint(2, 5)
        elif country == "Sri Lanka":
            sl_fears = {
                "rural": ["paddy harvest destroyed by drought", "tea estate wage not enough for family", "rubber price collapsed — tapping not worth it", "fish catch declining — overfishing", "cinnamon harvest buyer offers below cost", "2022 crisis debts still unpaid"],
                "urban_working": ["garments factory closes due to Trump 44% tariff", "tuk-tuk fuel cost eats into earnings", "construction work dries up — tourism slowdown", "FTZ boarding house rent increase", "PickMe commission cut reduces income", "real wages still below 2019 levels"],
                "middle_class": ["savings destroyed in 2022 crisis — not recovered", "VAT increased to 18% — household budget crushed", "school fees doubled since crisis", "medical emergency — insurance inadequate", "colleagues emigrated — left behind feeling", "government salary stagnant while prices doubled"],
                "corporate": ["IT colleagues emigrating to Australia/Singapore — team depleted", "Trump tariffs threaten export sector", "company restructuring post-crisis", "brain drain making Sri Lanka uncompetitive", "currency instability risk returns"],
                "migration_workers": ["Gulf employer confiscated passport — trapped", "domestic worker abuse — no consular help", "family back home struggling despite remittance", "contract fraud — paid agency fee but no job", "cannot return — debt to recruitment agent", "health emergency abroad — no insurance"],
                "students": ["19.8% youth unemployment — no job after degree", "A/L exam — family sacrificed everything for tuition", "2022 crisis closed school — lost academic year", "friends emigrated — feeling left behind", "educated unemployment paradox — degree worth nothing"],
                "women": ["tea estate wage Rs 1,350 — cannot feed family (Malaiyaha)", "daughter working in FTZ boarding house — family worries about safety", "husband disappeared in war — still searching 16 years later (Tamil north)", "food prices doubled — children eating less", "Gulf housemaid job — terrified but no other option"],
                "elderly": ["pension destroyed by 2022 inflation", "children emigrated after crisis — alone now", "medicine costs tripled — rationing pills", "JVP in power — memories of 1987-89 insurrection killings", "war memories — 1983 July riots haunting"],
            }
            primary_fear = random.choice(sl_fears.get(segment, sl_fears["urban_working"]))
            # Sri Lanka post-2022: trust low across board, varies by ethnicity
            trust_gov = random.randint(3, 6) if segment in {"corporate", "middle_class"} else random.randint(2, 5)
        elif country == "Nepal":
            np_fears = {
                "rural": ["husband dies in Qatar construction accident", "monsoon destroys terraced crop", "recruitment agent cheated — Rs 300,000 loan unpaid", "remittance stops coming — husband took second wife abroad", "earthquake damage repairs still unpaid", "children's school fees impossible without remittance"],
                "urban_working": ["Pathao reduces driver commission", "rent increase in Kathmandu", "construction work dries up — tourist season ends", "fuel price spike hits transport income", "earthquake-damaged building still unsafe", "tourist arrivals drop — hotel cuts staff"],
                "middle_class": ["Lok Sewa exam — 10th attempt — age bar approaching", "government salary stagnant while prices rise", "colleagues emigrated to Australia — left behind feeling", "school fees for children exceed government salary", "brain drain — best students all leaving Nepal"],
                "corporate": ["IT colleagues emigrating to Singapore/Australia — team depleted", "startup ecosystem too small — limited growth", "Nepal's market too small for ambition", "political instability disrupts business"],
                "migration_workers": ["Gulf employer confiscated passport — kafala — trapped", "recruitment agent took Rs 500,000 — job doesn't exist", "heat stroke risk in Qatar summer — coworker died last month", "family taking loans against remittance — debt spiral", "domestic worker abuse — Kuwait — cannot leave", "contract fraud — Romania job paid half what promised"],
                "students": ["76 friends killed in September 2025 uprising — trauma", "no job after degree — unemployment despite education", "Lok Sewa exam impossible without coaching — family cannot afford", "Japan/Korea EPS application rejected — wasted money", "want to leave Nepal but family cannot afford recruitment fees"],
                "women": ["husband abroad 3 years — hasn't sent money in 2 months", "managing farm, livestock, children, elderly alone — exhausted", "daughter's marriage — no money for dowry", "FCHV work 12 hours but government says I'm a volunteer", "monsoon destroyed maize crop — no food until next harvest", "brick kiln debt — Kamaiya legacy — family still trapped (Tharu)"],
                "elderly": ["children all abroad — alone in village", "Maoist war memories (1996-2006) — lost family", "September 2025 uprising — grandchildren at risk", "earthquake destroyed ancestral home — rebuilt but not same", "pension barely covers medicine", "Gurkha pension enough but loneliness of village life"],
            }
            primary_fear = random.choice(np_fears.get(segment, np_fears["rural"]))
            # Nepal post-March 2026: RSP supporters hopeful, old-guard low, Dalit/Madhesi cautious
            trust_gov = random.randint(4, 7) if segment in {"corporate", "students"} else random.randint(2, 5)
        else:
            primary_fear = random.choice(["price shock", "job loss", "family embarrassment", "rent and food costs", "remittance disruption"])
            trust_gov = random.randint(2, 7)

        bio = f"{job.title()} from {location}. Trying to keep family stability and dignity intact during uncertain times."
        persona = (
            f"{name} is a {job} from {location}. This person watches prices, family obligations, and public reputation closely. "
            f"They speak in a style shaped by {dialect_default} and react to social pressure quickly when household stability is threatened. "
            f"Their fear is practical rather than abstract, and their online behavior reflects class position, local rumor exposure, and everyday survival concerns."
        )
        return {
            "name": name,
            "age": random.randint(20, 55) if segment not in {"students", "elderly"} else (random.randint(18, 26) if segment == "students" else random.randint(60, 78)),
            "gender": gender,
            "occupation": job,
            "location": location,
            "trust_government": trust_gov,
            "shame_sensitivity": random.randint(4, 9 if segment in {"rural", "women", "elderly"} else 7),
            "primary_fear": primary_fear,
            "influence_radius": random.randint(8, 120),
            "fb_intensity": random.randint(2, 9 if segment in {"students", "urban_working"} else 6),
            "dialect": dialect_default,
            "income_stability": "stable salary" if segment in {"corporate", "middle_class"} else "fragile and month-to-month",
            "rumour_amplifier": segment in {"students", "urban_working"} and random.random() > 0.45,
            "baseline_anxiety": round(random.uniform(4.0, 8.2), 1),
            "interested_topics": ["family costs", "local news", "social issues"],
            "mbti": random.choice(self.profile_helper.MBTI_TYPES),
            "bio": bio,
            "persona": persona,
            "migration_worker_flag": segment == "migration_workers" or bool(diaspora_region),
            "remittance_dependency_flag": segment == "migration_workers" or bool(diaspora_region),
        }

    def _generate_institutional_fallback_profile(
        self,
        country: str,
        role_type: str,
        region: str,
        diaspora_region: Optional[str],
    ) -> Dict[str, Any]:
        priors = COUNTRY_INSTITUTIONAL_PRIORS.get(country, COUNTRY_INSTITUTIONAL_PRIORS["Bangladesh"])
        defaults = INSTITUTIONAL_ROLE_DEFAULTS[role_type]
        name = random.choice(priors.get(role_type, [f"{country} Public Voice"]))
        location = diaspora_region or f"{country} ({region})"
        role_occupation = {
            "GovernmentAgency": "public information desk",
            "MediaOutlet": "news desk editor",
            "Organization": "community advocacy coordinator",
            "Expert": "public policy researcher",
        }[role_type]
        bio = f"{name} covers or shapes public discussion from {location}. It speaks in a visible, agenda-setting voice during high-attention events."
        persona = (
            f"{name} operates as a {role_occupation} rooted in {location}. This voice watches how the scenario changes trust, panic, rumor spread, and "
            f"reputational pressure across the public. It prefers concise, public-facing language and weighs whether to calm, frame, or sharpen discussion. "
            f"Its incentives are shaped by institutional legitimacy, audience reach, and the risk of appearing absent when households are already anxious."
        )
        return {
            "name": name,
            "age": defaults["age"],
            "gender": defaults["gender"],
            "occupation": role_occupation,
            "location": location,
            "trust_government": defaults["trust_government"],
            "shame_sensitivity": defaults["shame_sensitivity"],
            "primary_fear": {
                "GovernmentAgency": "loss of public credibility",
                "MediaOutlet": "being outrun by rumor or losing audience trust",
                "Organization": "failing vulnerable households during a visible shock",
                "Expert": "publicly misreading the scale of the crisis",
            }[role_type],
            "influence_radius": defaults["influence_radius"],
            "fb_intensity": defaults["fb_intensity"],
            "dialect": COUNTRY_SETTINGS.get(country, COUNTRY_SETTINGS["Bangladesh"])["dialects"].split(" such as ")[-1].split(",")[0],
            "income_stability": defaults["income_stability"],
            "rumour_amplifier": defaults["rumour_amplifier"],
            "baseline_anxiety": defaults["baseline_anxiety"],
            "interested_topics": ["public reaction", "household pressure", "institutional credibility"],
            "mbti": "ISTJ" if role_type == "GovernmentAgency" else ("ENTJ" if role_type == "MediaOutlet" else "INFJ"),
            "bio": bio,
            "persona": persona,
        }

    def _build_segment_assignments(
        self,
        n_agents: int,
        segments: List[str],
        weights: Dict[str, float],
    ) -> List[str]:
        normalized_segments = [segment for segment in (SEGMENT_ALIASES.get(str(item).strip().lower()) for item in segments) if segment in weights]
        normalized_segments = list(dict.fromkeys(normalized_segments))
        if not normalized_segments:
            normalized_segments = ["rural", "urban_working"]

        selected_weights = self._normalize_weight_subset({segment: weights[segment] for segment in normalized_segments})
        allocations = self._allocate_weighted_counts(n_agents, selected_weights)

        assignments: List[str] = []
        for segment, count in allocations.items():
            assignments.extend([segment] * count)
        random.shuffle(assignments)
        return assignments

    def _normalize_weight_subset(self, weights: Dict[str, float]) -> Dict[str, float]:
        total = sum(max(weight, 0.0) for weight in weights.values())
        if total <= 0:
            even = 1.0 / max(1, len(weights))
            return {key: even for key in weights}
        return {key: max(weight, 0.0) / total for key, weight in weights.items()}

    def _allocate_weighted_counts(self, total_count: int, weights: Dict[str, float]) -> Dict[str, int]:
        allocations: Dict[str, int] = {}
        remainders = []
        assigned = 0
        for key, weight in weights.items():
            raw = total_count * weight
            count = math.floor(raw)
            allocations[key] = count
            assigned += count
            remainders.append((raw - count, key))

        remaining = total_count - assigned
        for _, key in sorted(remainders, reverse=True)[:remaining]:
            allocations[key] += 1
        return allocations

    def _normalize_region(self, region_map: Dict[str, str], region: str) -> str:
        key = str(region or "mixed").strip().lower()
        return key if key in region_map else "mixed"

    def _segment_to_entity_type(self, segment: Optional[str]) -> str:
        normalized = SEGMENT_ALIASES.get(str(segment or "").strip().lower(), str(segment or "").strip().lower())
        if normalized in INSTITUTIONAL_SEED_TYPES:
            return INSTITUTIONAL_SEED_TYPES[normalized]
        return OPS_SEGMENT_ENTITY_TYPES.get(normalized, "Person")

    def _segment_to_entity_labels(self, segment: Optional[str]) -> List[str]:
        primary_type = self._segment_to_entity_type(segment)
        labels = ["Entity", primary_type]
        if primary_type not in {"Person", *INSTITUTIONAL_SEED_TYPES.values()}:
            labels.append("Person")
        deduped: List[str] = []
        for label in labels:
            if label not in deduped:
                deduped.append(label)
        return deduped

    def _select_institutional_seed_roles(self, n_agents: int) -> List[str]:
        if n_agents <= 6:
            return ["GovernmentAgency"]
        if n_agents <= 20:
            return ["GovernmentAgency", "MediaOutlet"]
        if n_agents <= 50:
            return ["GovernmentAgency", "MediaOutlet", "Organization"]
        return ["GovernmentAgency", "MediaOutlet", "Organization", "Expert"]

    def _is_institutional_segment(self, segment: Optional[str]) -> bool:
        normalized = str(segment or "").strip().lower()
        return normalized in INSTITUTIONAL_SEED_TYPES

    def _generate_username(self, name: str, agent_index: int) -> str:
        return f"{_slugify(name)}_{agent_index:03d}"

    def _coerce_topics(self, value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [part.strip() for part in value.split(",") if part.strip()]
        return []

    def _coerce_bool(self, value: Any, default: Optional[bool] = None) -> Optional[bool]:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "1", "yes"}:
                return True
            if lowered in {"false", "0", "no"}:
                return False
        return default

    def _reindex_profiles(self, profiles: List[OasisAgentProfile]) -> List[OasisAgentProfile]:
        for idx, profile in enumerate(profiles):
            profile.user_id = idx
            profile.user_name = self._generate_username(profile.name, idx)
            profile.source_entity_uuid = f"ops_population_{(profile.country or 'south_asia').lower().replace(' ', '_')}_{idx}"
        return profiles
