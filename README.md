# AI-Based Multilingual Chatbot for Welfare Scheme Awareness

> **Challenge 1.1** — AI & Intelligent Systems Track  
> A low-bandwidth, multilingual conversational assistant deployable over WhatsApp and SMS to help rural users discover government welfare schemes they qualify for.

## Features

| Feature | Details |
|---------|---------|
| 🌐 **Languages** | English, Hindi, Tamil, Bengali, Marathi + Hinglish code-mixing |
| 📋 **Schemes Covered** | 10 high-impact schemes (PM-KISAN, Ayushman Bharat, PMAY-G, MGNREGA, PMUY, SSY, PM SVANidhi, PMJJBY, KCC, JSY) |
| 🧠 **AI Architecture** | RAG (Retrieval-Augmented Generation) with ChromaDB + Gemini 2.5 Flash |
| 📱 **Channels** | WhatsApp (Twilio) + SMS (Twilio) |
| 🎤 **Audio** | Voice note transcription via Gemini |
| 🔄 **State Machine** | 5-question eligibility flow → personalized scheme shortlist |
| 📄 **Checklist** | Downloadable/SMS-able document checklist in user's language |
| ✅ **Anti-hallucination** | Strict RAG grounding — never invents eligibility rules |

---

## Project Objectives (from Challenge Brief)

- [x] Chatbot supporting at least two regional languages (Hindi + Tamil + Bengali + Marathi)
- [x] Focused catalogue of 8–10 high-impact schemes (10 schemes implemented)
- [x] Eligibility-questioning flow asking 4–6 simple questions → personalized shortlist
- [x] Downloadable/SMS-able checklist of required documents in user's language
- [x] RAG architecture to prevent hallucinated entitlements
- [x] User-flow diagrams for 3 personas (farmer, gig worker, woman head-of-household)
- [x] Pilot test report with success metrics
- [x] 2-page impact projection
- [x] WhatsApp + SMS channel support
- [x] Code-mixing (Hinglish) support
- [x] Audio/voice note support

---

## Welfare Schemes Covered

| # | Scheme | Persona |
|---|--------|---------|
| 1 | PM-KISAN (₹6,000/year) | Farmer |
| 2 | Kisan Credit Card (KCC) | Farmer |
| 3 | MGNREGA (100 days employment) | Gig Worker |
| 4 | PM SVANidhi (micro-credit loan) | Street Vendor |
| 5 | Ayushman Bharat (₹5L health cover) | General/BPL |
| 6 | PMJJBY (₹2L life insurance) | General |
| 7 | PMUY/Ujjwala (free LPG) | Women |
| 8 | PMAY-G (housing assistance) | Rural poor |
| 9 | Sukanya Samriddhi Yojana | Parents of girl children |
| 10 | Janani Suraksha Yojana (JSY) | Pregnant women |

---

## Prerequisites

1. Python 3.9+
2. [Twilio Account](https://www.twilio.com/) (Free Trial works)
3. [Gemini API Key](https://aistudio.google.com/app/apikey)
4. `ngrok` (for local webhook testing)

---

## Setup Instructions

### 1. Install Dependencies
```bash
cd "AI Based Multilingual Chatbot for Welfare Scheme Awareness"
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Open `.env` and fill in:
```env
GOOGLE_API_KEY="your_gemini_api_key"
TWILIO_ACCOUNT_SID="your_twilio_account_sid"
TWILIO_AUTH_TOKEN="your_twilio_auth_token"
```

### 3. Populate the Vector Database
```bash
python populate_db.py
```
Expected output:
```
Loaded 10 schemes.
Database populated successfully at './chroma_db'.
```

### 4. Start the FastAPI Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Or:
```bash
python -m app.main
```

### 5. Expose Server via Ngrok (for local testing)
```bash
ngrok http 8000
```
Copy the `https://...` Forwarding URL.

### 6. Configure Twilio

**WhatsApp Sandbox:**
- Go to Twilio Console → Messaging → Try it out → Send a WhatsApp message
- Set **"WHEN A MESSAGE COMES IN"** to: `https://<your-ngrok-url>/webhook`
- Method: `POST`

**SMS (optional):**
- Go to Twilio Console → Phone Numbers → your number → Messaging
- Set webhook to: `https://<your-ngrok-url>/sms`

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and feature list |
| `/health` | GET | Health check + active session count |
| `/webhook` | POST | WhatsApp Twilio webhook |
| `/sms` | POST | SMS Twilio webhook |
| `/checklist/{session_id}` | GET | Get SMS-able document checklist |
| `/session/{session_id}` | GET | Debug: view session state |

---

## How the Eligibility Flow Works

```
User: "Hi" / "नमस्ते" / "வணக்கம்"
  └─► Language detected → greeting in user's language
  
Q1: Occupation? (Farmer / Daily wage / Vendor / Homemaker / Other)
Q2: Rural or Urban?
Q3: Gender? (Male / Female)
Q4: Annual income? (Below ₹1L / ₹1-3L / Above ₹3L)
Q5: Family? (Girl child / Pregnant / No pucca house / No LPG / None)
  └─► RAG retrieves top 4 relevant schemes
  └─► Gemini generates personalized recommendation + document checklist
  
Follow-up: Free-form Q&A ("How to apply?", "What documents?")
Anytime: Type "checklist" → SMS-ready document list
Anytime: Type "restart" / "hi" → Start over
```

---

## Testing

### Via curl (simulate WhatsApp):
```bash
# Test WhatsApp webhook
curl -X POST http://localhost:8000/webhook \
  -d "From=whatsapp:+919999999999&Body=Hi&NumMedia=0"

# Test SMS
curl -X POST http://localhost:8000/sms \
  -d "From=+919999999999&Body=Hi"

# Get checklist
curl http://localhost:8000/checklist/whatsapp%3A%2B919999999999

# Health check
curl http://localhost:8000/health
```

### Language testing:
- English: Send "Hi"
- Hindi: Send "नमस्ते" or "main kisan hu"
- Tamil: Send "வணக்கம்"
- Bengali: Send "নমস্কার"
- Code-mixed: Send "mera aadhaar kho gaya" or "main ek farmer hu"

---

## Documents & Reports

| File | Description |
|------|-------------|
| `USER_FLOW_DIAGRAM.md` | Flow diagrams for 3 personas (farmer, gig worker, woman head-of-household) |
| `Pilot_Test_and_Impact.md` | Pilot test report + 2-page impact projection |
| `data/schemes_data.json` | Welfare scheme data in JSON (multilingual names) |

---

## Architecture

```
User (WhatsApp/SMS)
      │
      ▼
Twilio → FastAPI (app/main.py)
      │
      ├── Audio? → Gemini transcription (audio_handler.py)
      │
      ├── State Machine (chatbot.py)
      │   ├── Language Detection (script + word-level)
      │   ├── 5-question eligibility flow
      │   └── Profile collection
      │
      ├── RAG Pipeline
      │   ├── ChromaDB vector store (10 schemes)
      │   ├── HuggingFace embeddings (all-MiniLM-L6-v2)
      │   └── Top-4 relevant documents retrieved
      │
      └── Gemini 2.5 Flash → Localized recommendation + checklist
```

---

## Success Metrics (from Challenge Brief)

| Metric | Target | Approach |
|--------|--------|---------|
| Eligibility flow completion | ≥ 80% | 5-question flow, concise messages |
| Comprehension score | ≥ 70% | Clear scheme summaries, document lists |
| Response latency | < 3 seconds | Lightweight embeddings, concise prompts |
| Code-mixing accuracy | High | Script detection + Hinglish word list |
