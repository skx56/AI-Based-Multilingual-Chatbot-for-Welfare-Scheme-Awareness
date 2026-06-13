# User Flow Diagrams — Welfare Scheme Chatbot
## 3 Persona Journeys

---

## Persona 1: Raju — Farmer 🌾
**Profile:** 45-year-old male farmer, lives in rural Uttar Pradesh, annual income ~₹80,000, owns 2 acres of land, has a daughter aged 7.

```
[Raju sends "Hi" on WhatsApp]
          │
          ▼
[BOT: Greeting + Q1 — What is your occupation?]
[Raju: "1" (Farmer)]
          │
          ▼
[BOT: Q2 — Rural or Urban area?]
[Raju: "1" (Rural/Village)]
          │
          ▼
[BOT: Q3 — Gender?]
[Raju: "1" (Male)]
          │
          ▼
[BOT: Q4 — Annual income?]
[Raju: "1" (Below ₹1 lakh)]
          │
          ▼
[BOT: Q5 — Family situation? (girl child, pregnant, no house, no LPG, none)]
[Raju: "1" (Girl child below 10)]
          │
          ▼
[RAG RETRIEVAL: farmer + rural + low income + girl child]
          │
          ▼
[BOT RECOMMENDS:]
  ✅ PM-KISAN — ₹6,000/year (direct to bank)
  ✅ Kisan Credit Card — cheap farm loan up to ₹3 lakh
  ✅ Sukanya Samriddhi Yojana — savings for daughter
  📋 Document checklist provided inline
          │
          ▼
[Raju: "checklist"] → SMS-ready list downloaded
          │
          ▼
[Raju: "How do I apply for PM-KISAN?"] → RAG Q&A mode
          │
          ▼
[END OF FLOW — Raju knows 3 schemes + has document list]
```

**Key Decision Points:**
- Occupation = farmer → triggers PM-KISAN + KCC retrieval
- Girl child = Sukanya Samriddhi Yojana
- Low income = prioritizes income support schemes

---

## Persona 2: Suresh — Gig Worker / Daily Wage Laborer 🔨
**Profile:** 32-year-old male, migrant construction worker, currently in urban Surat, income ~₹1.5 lakh/year, no stable housing.

```
[Suresh sends "मेरा naam Suresh hai, kya scheme milegi mujhe?" (Hinglish)]
          │
          ▼
[LANGUAGE DETECTION: Hinglish → Hindi response mode]
          │
          ▼
[BOT: Hindi greeting + Q1 — आपका मुख्य पेशा?]
[Suresh: "2" (दिहाड़ी मजदूर)]
          │
          ▼
[BOT: Q2 — ग्रामीण या शहरी?]
[Suresh: "2" (शहरी — Surat)]
          │
          ▼
[BOT: Q3 — लिंग?]
[Suresh: "1" (पुरुष)]
          │
          ▼
[BOT: Q4 — वार्षिक आय?]
[Suresh: "2" (₹1-3 लाख)]
          │
          ▼
[BOT: Q5 — परिवार की स्थिति?]
[Suresh: "5" (इनमें से कोई नहीं)]
          │
          ▼
[RAG RETRIEVAL: daily_wage + urban + male + 1-3 lakh]
          │
          ▼
[BOT RECOMMENDS (in Hindi):]
  ✅ PM SVANidhi — ₹10,000 working capital loan (if street vendor)
  ✅ MGNREGA — 100 days guaranteed work (if returns to village)
  ✅ Ayushman Bharat — ₹5 lakh health cover (if below SECC list)
  📋 हिंदी में दस्तावेज़ सूची दी गई
          │
          ▼
[Suresh: "MGNREGA ke liye kya chahiye?"] → Hindi Q&A continues
          │
          ▼
[END — Suresh has actionable scheme info in his language]
```

**Key Decision Points:**
- Hinglish detection → Hindi response mode throughout
- Urban gig worker → PM SVANidhi + Ayushman Bharat prioritized
- Code-mixing handled naturally ("kya scheme milegi mujhe?")

---

## Persona 3: Lakshmi — Woman Head-of-Household 👩‍👧
**Profile:** 38-year-old widow from rural Tamil Nadu, two daughters (ages 4 and 8), no LPG connection, living in kutcha house, income below ₹1 lakh.

```
[Lakshmi sends "வணக்கம்" (Tamil for Hello) via WhatsApp]
          │
          ▼
[LANGUAGE DETECTION: Tamil script detected → Tamil response mode]
          │
          ▼
[BOT: Tamil greeting + Q1 — உங்கள் தொழில் என்ன?]
[Lakshmi: "4" (இல்லத்தரசி — Homemaker/No income)]
          │
          ▼
[BOT: Q2 — கிராமம் அல்லது நகரம்?]
[Lakshmi: "1" (கிராமம் — Rural)]
          │
          ▼
[BOT: Q3 — பாலினம்?]
[Lakshmi: "2" (பெண் — Female)]
          │
          ▼
[BOT: Q4 — வருடாந்திர வருமானம்?]
[Lakshmi: "1" (₹1 லட்சத்திற்கு கீழ்)]
          │
          ▼
[BOT: Q5 — குடும்ப நிலை?]
[Lakshmi: "1,3,4" (பெண் குழந்தை + பக்கா வீடு இல்லை + LPG இல்லை)]
          │
          ▼
[RAG RETRIEVAL: woman + rural + female + below_1_lakh + girl_child + no_pucca_house + no_lpg]
          │
          ▼
[BOT RECOMMENDS (in Tamil):]
  ✅ PMUY (Ujjwala) — இலவச LPG இணைப்பு
  ✅ PMAY-G — பக்கா வீடு கட்ட நிதி (₹1.20 lakh)
  ✅ Sukanya Samriddhi — மகளுக்கு சேமிப்பு திட்டம்
  ✅ Ayushman Bharat — ₹5 லட்சம் சுகாதார காப்பீடு
  ✅ Janani Suraksha Yojana — (if pregnant) பிரசவ உதவி
  📋 தமிழில் ஆவண பட்டியல் வழங்கப்பட்டது
          │
          ▼
[Lakshmi: "checklist"] → SMS-ready Tamil document list
          │
          ▼
[END — Lakshmi has 4-5 schemes matched + document list in Tamil]
```

**Key Decision Points:**
- Tamil script detection → full Tamil response throughout
- Female + no LPG → Ujjwala Yojana (highest priority)
- No pucca house → PMAY-G
- Girl children → Sukanya Samriddhi
- Low income female → Ayushman Bharat

---

## State Machine Overview

```
┌─────────────────────────────────────────────────────┐
│                  CHATBOT STATE MACHINE              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [User sends first message]                         │
│         │                                           │
│         ▼                                           │
│  ┌─────────────┐   Language Detection               │
│  │  GREETING   │   (EN/HI/TA/BN/MR)                │
│  └──────┬──────┘                                    │
│         │ Q1: Occupation?                           │
│         ▼                                           │
│  ┌─────────────┐                                    │
│  │ Q_LOCATION  │   Q2: Rural or Urban?              │
│  └──────┬──────┘                                    │
│         │ Q3: Gender?                               │
│         ▼                                           │
│  ┌─────────────┐                                    │
│  │  Q_GENDER   │   Q3: Male/Female/Other?           │
│  └──────┬──────┘                                    │
│         │ Q4: Income?                               │
│         ▼                                           │
│  ┌─────────────┐                                    │
│  │  Q_INCOME   │   Q4: Annual income bracket?       │
│  └──────┬──────┘                                    │
│         │ Q5: Family?                               │
│         ▼                                           │
│  ┌─────────────┐                                    │
│  │  Q_FAMILY   │   Q5: Girl child/pregnant/house?   │
│  └──────┬──────┘                                    │
│         │ RAG Retrieval + LLM                       │
│         ▼                                           │
│  ┌─────────────┐                                    │
│  │  RECOMMEND  │   Personalized scheme shortlist    │
│  │             │   + Document checklist             │
│  └──────┬──────┘                                    │
│         │ Free-form Q&A continues                   │
│         ▼                                           │
│  ┌─────────────┐                                    │
│  │    DONE     │   RAG-based follow-up questions    │
│  └─────────────┘                                    │
│                                                     │
│  Special Commands (any state):                      │
│  • "checklist" / "list" → SMS-ready document list  │
│  • "restart" / "hi" → Reset and start over         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Channel Support

| Channel | Endpoint | Format | Audio? | Languages |
|---------|----------|--------|--------|-----------|
| WhatsApp | POST /webhook | WhatsApp markdown + TwiML | ✅ Voice notes | EN, HI, TA, BN, MR |
| SMS | POST /sms | Plain text + TwiML | ❌ | EN, HI, TA, BN, MR |
| API | GET /checklist/{id} | Plain text | N/A | EN, HI, TA, BN, MR |

---

## Code-Mixing Examples

| User Input | Detection | Response Language |
|-----------|-----------|------------------|
| "Hi" | English | English |
| "नमस्ते" | Hindi (Devanagari script) | Hindi |
| "வணக்கம்" | Tamil (Tamil script) | Tamil |
| "main kisan hu" | Hinglish → Hindi | Hindi |
| "mera aadhaar kho gaya" | Hinglish → Hindi | Hindi |
| "নমস্কার" | Bengali | Bengali |
| "मेरा naam Suresh hai" | Code-mixed → Hindi | Hindi |
