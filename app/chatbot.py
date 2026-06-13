import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

persist_directory = "./chroma_db"

# Initialize Embeddings and LLM
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

# Initialize Chroma Vector Store
try:
    vector_store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})
except Exception as e:
    print(f"Warning: Could not initialize ChromaDB. Run populate_db.py first. Error: {e}")
    retriever = None

# ─────────────────────────────────────────────
# ELIGIBILITY STATE MACHINE
# States: greeting → q_occupation → q_location → q_gender → q_income → q_family → recommend → done
# ─────────────────────────────────────────────

ELIGIBILITY_QUESTIONS = {
    "greeting": {
        "en": "Hello! I'm your Welfare Scheme Assistant 🙏\nI'll ask you 5 quick questions to find government schemes YOU qualify for.\n\nFirst: *What is your main occupation?*\nReply with: 1) Farmer 🌾  2) Daily wage/Gig worker  3) Business/Street vendor  4) Housewife/No income  5) Other",
        "hi": "नमस्ते! मैं आपका कल्याण योजना सहायक हूँ 🙏\nमैं आपसे 5 सरल प्रश्न पूछूँगा ताकि आपके लिए सही सरकारी योजनाएं ढूंढ सकूं।\n\nपहला प्रश्न: *आपका मुख्य पेशा क्या है?*\nजवाब दें: 1) किसान 🌾  2) दिहाड़ी मजदूर/गिग वर्कर  3) व्यापार/रेहड़ी वाला  4) गृहिणी/कोई आय नहीं  5) अन्य",
        "ta": "வணக்கம்! நான் உங்கள் நலத் திட்ட உதவியாளர் 🙏\nநான் உங்களிடம் 5 எளிய கேள்விகள் கேட்பேன்.\n\nமுதல் கேள்வி: *உங்கள் தொழில் என்ன?*\nபதில் தரவும்: 1) விவசாயி 🌾  2) தினக்கூலி  3) வியாபாரி  4) இல்லத்தரசி  5) மற்றவை",
        "bn": "নমস্কার! আমি আপনার কল্যাণ প্রকল্প সহকারী 🙏\nআমি আপনাকে ৫টি সহজ প্রশ্ন করব।\n\nপ্রথম প্রশ্ন: *আপনার প্রধান পেশা কী?*\nউত্তর দিন: 1) কৃষক 🌾  2) দৈনিক মজুর  3) ব্যবসায়ী/হকার  4) গৃহিণী  5) অন্যান্য",
        "mr": "नमस्कार! मी तुमचा कल्याण योजना सहाय्यक आहे 🙏\nमी तुम्हाला ५ साध्या प्रश्न विचारेन.\n\nपहिला प्रश्न: *तुमचा मुख्य व्यवसाय काय आहे?*\nउत्तर द्या: 1) शेतकरी 🌾  2) रोजंदारी कामगार  3) व्यापारी/फेरीवाला  4) गृहिणी  5) इतर",
        "next_state": "q_location"
    },
    "q_location": {
        "en": "Do you live in a *rural* (village/gram panchayat) or *urban* (city/town) area?\nReply: 1) Rural/Village  2) Urban/City",
        "hi": "क्या आप *ग्रामीण* (गाँव/ग्राम पंचायत) या *शहरी* (शहर/कस्बा) क्षेत्र में रहते हैं?\nजवाब दें: 1) ग्रामीण/गाँव  2) शहरी/शहर",
        "ta": "நீங்கள் *கிராமப்புறம்* (கிராமம்) அல்லது *நகரப்புறம்* (நகரம்) வசிக்கிறீர்களா?\nபதில்: 1) கிராமம்  2) நகரம்",
        "bn": "আপনি কি *গ্রামীণ* (গ্রাম/পঞ্চায়েত) নাকি *শহরে* থাকেন?\nউত্তর: 1) গ্রামীণ  2) শহর",
        "mr": "तुम्ही *ग्रामीण* (गाव/ग्राम पंचायत) किंवा *शहरी* (शहर) भागात राहता?\nउत्तर: 1) ग्रामीण/गाव  2) शहरी/शहर",
        "next_state": "q_gender"
    },
    "q_gender": {
        "en": "What is your gender?\nReply: 1) Male  2) Female  3) Prefer not to say",
        "hi": "आपका लिंग क्या है?\nजवाब दें: 1) पुरुष  2) महिला  3) बताना नहीं चाहता/चाहती",
        "ta": "உங்கள் பாலினம் என்ன?\nபதில்: 1) ஆண்  2) பெண்  3) சொல்ல விரும்பவில்லை",
        "bn": "আপনার লিঙ্গ কী?\nউত্তর: 1) পুরুষ  2) মহিলা  3) বলতে চাই না",
        "mr": "तुमचे लिंग काय आहे?\nउत्तर: 1) पुरुष  2) महिला  3) सांगायचे नाही",
        "next_state": "q_income"
    },
    "q_income": {
        "en": "What is your approximate *annual household income*?\nReply: 1) Below ₹1 lakh (very low)  2) ₹1-3 lakh  3) Above ₹3 lakh",
        "hi": "आपकी अनुमानित *वार्षिक पारिवारिक आय* क्या है?\nजवाब दें: 1) ₹1 लाख से कम (बहुत कम)  2) ₹1-3 लाख  3) ₹3 लाख से अधिक",
        "ta": "உங்கள் *வருடாந்திர குடும்ப வருமானம்* என்ன?\nபதில்: 1) ₹1 லட்சத்திற்கு கீழ்  2) ₹1-3 லட்சம்  3) ₹3 லட்சத்திற்கு மேல்",
        "bn": "আপনার আনুমানিক *বার্ষিক পারিবারিক আয়* কত?\nউত্তর: 1) ₹১ লাখের নিচে  2) ₹১-৩ লাখ  3) ₹৩ লাখের বেশি",
        "mr": "तुमचे अंदाजे *वार्षिक कौटुंबिक उत्पन्न* किती आहे?\nउत्तर: 1) ₹1 लाखापेक्षा कमी  2) ₹1-3 लाख  3) ₹3 लाखापेक्षा जास्त",
        "next_state": "q_family"
    },
    "q_family": {
        "en": "Last question! Do you have any of these?\nReply (you can pick multiple, e.g. '1,3'):\n1) Girl child below 10 years\n2) Pregnant woman in household\n3) No pucca house (kutcha/dilapidated)\n4) No LPG gas connection\n5) None of these",
        "hi": "आखिरी सवाल! क्या आपके घर में इनमें से कोई है?\nजवाब दें (एक से अधिक चुन सकते हैं, जैसे '1,3'):\n1) 10 साल से कम उम्र की बच्ची\n2) घर में गर्भवती महिला\n3) पक्का घर नहीं है (कच्चा/जर्जर)\n4) LPG गैस कनेक्शन नहीं है\n5) इनमें से कोई नहीं",
        "ta": "கடைசி கேள்வி! உங்கள் வீட்டில் இவை ஏதாவது உள்ளதா?\nபதில் (பல தேர்வு சாத்தியம், உதா. '1,3'):\n1) 10 வயதிற்கு கீழ் பெண் குழந்தை\n2) கர்ப்பிணி பெண்\n3) பக்கா வீடு இல்லை\n4) LPG இணைப்பு இல்லை\n5) இவை எதுவும் இல்லை",
        "bn": "শেষ প্রশ্ন! আপনার পরিবারে কি এগুলোর কোনোটি আছে?\nউত্তর (একাধিক বেছে নিতে পারেন, যেমন '1,3'):\n1) ১০ বছরের কম বয়সী মেয়ে\n2) পরিবারে গর্ভবতী মহিলা\n3) পাকা বাড়ি নেই\n4) LPG সংযোগ নেই\n5) এগুলোর কোনোটিই নেই",
        "mr": "शेवटचा प्रश्न! तुमच्या घरात यापैकी काही आहे का?\nउत्तर (एकापेक्षा जास्त निवडू शकता, उदा. '1,3'):\n1) 10 वर्षाखालील मुलगी\n2) घरात गर्भवती महिला\n3) पक्के घर नाही\n4) LPG गॅस कनेक्शन नाही\n5) यापैकी काहीही नाही",
        "next_state": "recommend"
    }
}

SYSTEM_PROMPT = """You are a helpful, multilingual government welfare scheme assistant for rural Indian citizens.
You are named "Sahayak" (meaning Helper).

LANGUAGE RULES (CRITICAL):
- Detect the user's language from their message. Respond in the SAME language.
- Supported languages: English, Hindi (हिंदी), Tamil (தமிழ்), Bengali (বাংলা), Marathi (मराठी).
- Handle code-mixed text naturally (e.g., "मेरा aadhaar खो गया", "I am ek farmer hu").
- If user writes in Roman Hindi/Hinglish (e.g., "main kisan hu"), respond in Hindi or Hinglish accordingly.

STRICT ANTI-HALLUCINATION RULES:
1. ONLY use information from the CONTEXT below. NEVER invent eligibility rules or benefits.
2. If the context doesn't have info, say: "मुझे इस योजना की जानकारी नहीं है / I don't have info on that specific scheme."
3. Always cite the scheme name when giving eligibility or document info.

CONVERSATION RULES:
- Keep responses SHORT and CONCISE (WhatsApp/SMS friendly, low bandwidth).
- Maximum 4-6 questions to determine eligibility.
- After collecting user profile, recommend 1-3 most relevant schemes with their document checklist.
- When providing a document checklist, format it clearly with numbered items.
- Always end recommendations with: "Type 'checklist' to get a downloadable document list for your schemes."

CONTEXT FROM SCHEMES DATABASE:
{context}

User Profile Collected So Far: {user_profile}
Current Conversation State: {state}
"""

RECOMMENDATION_PROMPT = """Based on the following user profile, recommend the most relevant government welfare schemes from the context provided.
Give a personalized, concise recommendation in the user's language.

User Profile:
- Occupation: {occupation}
- Location: {location}  
- Gender: {gender}
- Annual Income: {income}
- Family Situation: {family}

After recommending schemes, provide the FULL document checklist for each recommended scheme, formatted clearly.
End with: "Type 'checklist' to receive this list as an SMS-ready text."

CONTEXT FROM SCHEMES DATABASE:
{context}

Respond in: {language}
Keep it WhatsApp-friendly and concise. Use emojis sparingly.
"""

def detect_language(text: str) -> str:
    """
    Simple language detection based on script presence.
    Returns language code: 'hi', 'ta', 'bn', 'mr', 'en'
    """
    # Check for Devanagari script (Hindi/Marathi)
    devanagari = sum(1 for ch in text if '\u0900' <= ch <= '\u097F')
    # Tamil script
    tamil = sum(1 for ch in text if '\u0B80' <= ch <= '\u0BFF')
    # Bengali script
    bengali = sum(1 for ch in text if '\u0980' <= ch <= '\u09FF')
    
    if tamil > 0:
        return 'ta'
    if bengali > 0:
        return 'bn'
    if devanagari > 0:
        # Marathi and Hindi share Devanagari — use Hindi as default
        # Could be improved with a Marathi-specific dictionary check
        return 'hi'
    
    # Check for common Hindi/Hinglish words in Roman script
    hinglish_words = ['kisan', 'gaon', 'main', 'mera', 'meri', 'hai', 'hoon', 'hu', 'aur', 
                      'nahi', 'kya', 'kaun', 'kaise', 'kyun', 'thik', 'haan', 'nahin',
                      'namaste', 'bhai', 'didi', 'aadhaar', 'adhaar', 'ghar', 'paisa']
    text_lower = text.lower()
    if any(word in text_lower for word in hinglish_words):
        return 'hi'
    
    return 'en'

def parse_occupation(answer: str) -> str:
    """Parse occupation from user's answer."""
    answer = answer.strip()
    if '1' in answer or any(w in answer.lower() for w in ['farm', 'kisan', 'kisaan', 'farmer', 'krishak', 'vivasayi', 'sheti']):
        return 'farmer'
    elif '2' in answer or any(w in answer.lower() for w in ['daily', 'wage', 'labour', 'laborer', 'gig', 'worker', 'majdoor', 'din', 'kuli']):
        return 'gig_worker'
    elif '3' in answer or any(w in answer.lower() for w in ['business', 'vendor', 'shop', 'street', 'hawker', 'rehri', 'thela', 'vyapari', 'dukan']):
        return 'vendor'
    elif '4' in answer or any(w in answer.lower() for w in ['house', 'home', 'grih', 'gharelu', 'wife', 'woman', 'mahila', 'griha']):
        return 'homemaker'
    else:
        return 'other'

def parse_location(answer: str) -> str:
    if '1' in answer or any(w in answer.lower() for w in ['rural', 'village', 'gaon', 'gram', 'grama', 'kirami', 'kiraam']):
        return 'rural'
    return 'urban'

def parse_gender(answer: str) -> str:
    if '2' in answer or any(w in answer.lower() for w in ['female', 'woman', 'mahila', 'aurat', 'lady', 'pen', 'stri']):
        return 'female'
    elif '1' in answer or any(w in answer.lower() for w in ['male', 'man', 'purush', 'aadmi', 'pur']):
        return 'male'
    return 'not_specified'

def parse_income(answer: str) -> str:
    if '1' in answer:
        return 'below_1_lakh'
    elif '2' in answer:
        return '1_to_3_lakh'
    else:
        return 'above_3_lakh'

def parse_family(answer: str) -> list:
    situations = []
    if '1' in answer:
        situations.append('girl_child')
    if '2' in answer:
        situations.append('pregnant_woman')
    if '3' in answer:
        situations.append('no_pucca_house')
    if '4' in answer:
        situations.append('no_lpg')
    if '5' in answer or not situations:
        situations = ['none']
    return situations

def generate_scheme_recommendations(user_profile: dict, lang: str) -> str:
    """Build a recommendation query based on collected profile."""
    occupation = user_profile.get('occupation', 'other')
    location = user_profile.get('location', 'rural')
    gender = user_profile.get('gender', 'not_specified')
    income = user_profile.get('income', 'below_1_lakh')
    family = user_profile.get('family', ['none'])
    
    # Build a rich query for RAG retrieval
    query_parts = []
    if occupation == 'farmer':
        query_parts.append("farmer landholding agriculture kisan PM-KISAN Kisan Credit Card")
    if occupation == 'gig_worker':
        query_parts.append("daily wage worker rural employment MGNREGA guaranteed work job card")
    if occupation == 'vendor':
        query_parts.append("street vendor hawker micro credit loan SVANidhi urban")
    if location == 'rural':
        query_parts.append("rural housing kutcha house PMAY-G gram panchayat")
    if gender == 'female':
        query_parts.append("woman female LPG Ujjwala Yojana PMUY")
    if income in ['below_1_lakh', '1_to_3_lakh']:
        query_parts.append("BPL below poverty line low income poor family Ayushman health cover insurance")
    if 'girl_child' in family:
        query_parts.append("girl child savings scheme Sukanya Samriddhi SSY education")
    if 'pregnant_woman' in family:
        query_parts.append("pregnant woman maternity safe delivery Janani Suraksha JSY")
    if 'no_lpg' in family:
        query_parts.append("LPG gas connection free Ujjwala PMUY women BPL")
    if 'no_pucca_house' in family:
        query_parts.append("kutcha house no home housing rural PMAY-G pucca")
    
    query = " ".join(query_parts) if query_parts else "general welfare scheme low income rural India"
    return query

def generate_document_checklist(schemes_text: str, lang: str) -> str:
    """Generate a formatted, SMS-able document checklist."""
    lang_headers = {
        'en': "📋 *DOCUMENT CHECKLIST*\n(Save this or screenshot it)\n",
        'hi': "📋 *दस्तावेज़ सूची*\n(इसे सेव करें या स्क्रीनशॉट लें)\n",
        'ta': "📋 *ஆவண பட்டியல்*\n(இதை சேமிக்கவும்)\n",
        'bn': "📋 *নথি চেকলিস্ট*\n(এটি সংরক্ষণ করুন)\n",
        'mr': "📋 *कागदपत्र यादी*\n(हे सेव्ह करा)\n"
    }
    header = lang_headers.get(lang, lang_headers['en'])
    return header + "\n" + schemes_text

def get_next_question(state: str, lang: str) -> str:
    """Get the next question in the eligibility flow in the right language."""
    q = ELIGIBILITY_QUESTIONS.get(state, {})
    return q.get(lang, q.get('en', ''))

def advance_state(current_state: str) -> str:
    """Return the next state in the flow."""
    state_order = ['greeting', 'q_location', 'q_gender', 'q_income', 'q_family', 'recommend', 'done']
    try:
        idx = state_order.index(current_state)
        return state_order[idx + 1] if idx + 1 < len(state_order) else 'done'
    except ValueError:
        return 'done'

def get_chatbot_response(session_id: str, message: str, session_state: dict) -> str:
    """
    Main chatbot response function with structured eligibility state machine.
    """
    state = session_state.get('state', 'greeting')
    user_profile = session_state.get('user_profile', {})
    lang = session_state.get('lang', detect_language(message))
    session_state['lang'] = lang
    
    # Update language detection on each message (user may switch)
    detected = detect_language(message)
    if detected != 'en':  # prefer non-english detection (more specific)
        lang = detected
        session_state['lang'] = lang

    # ── Handle special commands ──
    if message.strip().lower() in ['checklist', 'list', 'documents', 'दस्तावेज', 'பட்டியல்', 'তালিকা', 'यादी']:
        return _handle_checklist_command(session_state, lang)
    
    if message.strip().lower() in ['restart', 'शुरू', 'reset', 'new', 'start', 'hi', 'hello', 'नमस्ते', 'வணக்கம்', 'নমস্কার']:
        # Reset session
        session_state['state'] = 'greeting'
        session_state['user_profile'] = {}
        lang = detect_language(message)
        session_state['lang'] = lang
        return ELIGIBILITY_QUESTIONS['greeting'].get(lang, ELIGIBILITY_QUESTIONS['greeting']['en'])

    # ── State Machine ──
    if state == 'greeting':
        # Return greeting/first question
        next_q = get_next_question('q_location', lang)
        session_state['state'] = 'q_location'
        return next_q

    elif state == 'q_location':
        user_profile['occupation'] = parse_occupation(session_state.get('last_answer', message))
        user_profile['location'] = parse_location(message)
        session_state['user_profile'] = user_profile
        session_state['state'] = 'q_gender'
        return get_next_question('q_gender', lang)

    elif state == 'q_gender':
        user_profile['location'] = parse_location(session_state.get('last_answer', '1'))
        user_profile['gender'] = parse_gender(message)
        session_state['user_profile'] = user_profile
        session_state['state'] = 'q_income'
        return get_next_question('q_income', lang)

    elif state == 'q_income':
        user_profile['gender'] = parse_gender(session_state.get('last_answer', message))
        user_profile['income'] = parse_income(message)
        session_state['user_profile'] = user_profile
        session_state['state'] = 'q_family'
        return get_next_question('q_family', lang)

    elif state == 'q_family':
        user_profile['income'] = parse_income(session_state.get('last_answer', '1'))
        user_profile['family'] = parse_family(message)
        session_state['user_profile'] = user_profile
        session_state['state'] = 'recommend'
        return _generate_recommendation(session_state, lang)

    elif state == 'recommend' or state == 'done':
        # Free-form Q&A about schemes using RAG
        return _rag_chat(message, session_state, lang)

    else:
        # Fallback: start eligibility flow
        session_state['state'] = 'greeting'
        return ELIGIBILITY_QUESTIONS['greeting'].get(lang, ELIGIBILITY_QUESTIONS['greeting']['en'])


def _generate_recommendation(session_state: dict, lang: str) -> str:
    """Generate personalized scheme recommendations based on collected profile."""
    user_profile = session_state.get('user_profile', {})
    
    # Build RAG query from profile
    rag_query = generate_scheme_recommendations(user_profile, lang)
    
    context_text = ""
    if retriever:
        docs = retriever.invoke(rag_query)
        context_text = "\n\n---\n".join([doc.page_content for doc in docs])
    
    profile_summary = f"""
Occupation: {user_profile.get('occupation', 'unknown')}
Location: {user_profile.get('location', 'unknown')}
Gender: {user_profile.get('gender', 'unknown')}
Annual Income: {user_profile.get('income', 'unknown')}
Family Situation: {', '.join(user_profile.get('family', ['none']))}
"""
    lang_names = {'en': 'English', 'hi': 'Hindi', 'ta': 'Tamil', 'bn': 'Bengali', 'mr': 'Marathi'}
    
    prompt = RECOMMENDATION_PROMPT.format(
        occupation=user_profile.get('occupation', 'other'),
        location=user_profile.get('location', 'rural'),
        gender=user_profile.get('gender', 'not_specified'),
        income=user_profile.get('income', 'below_1_lakh'),
        family=', '.join(user_profile.get('family', ['none'])),
        context=context_text,
        language=lang_names.get(lang, 'English')
    )
    
    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    
    session_state['last_recommendation'] = response.content
    session_state['state'] = 'done'
    
    return response.content


def _rag_chat(message: str, session_state: dict, lang: str) -> str:
    """Free-form RAG-based chat after eligibility is done."""
    context_text = ""
    if retriever:
        docs = retriever.invoke(message)
        context_text = "\n\n".join([doc.page_content for doc in docs])
    
    user_profile = session_state.get('user_profile', {})
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(
            context=context_text,
            user_profile=str(user_profile),
            state=session_state.get('state', 'done')
        ))
    ]
    
    for msg in session_state.get("history", [])[:-1]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    
    messages.append(HumanMessage(content=message))
    response = llm.invoke(messages)
    return response.content


def _handle_checklist_command(session_state: dict, lang: str) -> str:
    """Return the last recommendation as a formatted, SMS-able checklist."""
    last_rec = session_state.get('last_recommendation', '')
    if last_rec:
        return generate_document_checklist(last_rec, lang)
    
    fallback = {
        'en': "Please complete the eligibility questions first. Type 'hi' to start.",
        'hi': "कृपया पहले पात्रता प्रश्नों को पूरा करें। शुरू करने के लिए 'hi' टाइप करें।",
        'ta': "முதலில் தகுதி கேள்விகளை முடிக்கவும். 'hi' என்று தட்டச்சு செய்யவும்.",
        'bn': "প্রথমে যোগ্যতার প্রশ্নগুলি সম্পূর্ণ করুন। শুরু করতে 'hi' টাইপ করুন।",
        'mr': "प्रथम पात्रता प्रश्न पूर्ण करा. सुरू करण्यासाठी 'hi' टाइप करा."
    }
    return fallback.get(lang, fallback['en'])
