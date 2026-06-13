from fastapi import FastAPI, Form, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict
import os
import requests
from dotenv import load_dotenv

from app.chatbot import (
    get_chatbot_response,
    ELIGIBILITY_QUESTIONS,
    detect_language,
    generate_document_checklist
)
from app.audio_handler import handle_audio_message

load_dotenv()

app = FastAPI(
    title="Welfare Scheme Chatbot",
    description="AI-Based Multilingual Chatbot for Welfare Scheme Awareness — supports WhatsApp, SMS. Languages: English, Hindi, Tamil, Bengali, Marathi.",
    version="2.0.0"
)

# ─────────────────────────────────────────────
# In-memory session store
# Format: { "sender_id": { "history": [], "state": "greeting", "user_profile": {}, "lang": "en", "last_recommendation": "" } }
# ─────────────────────────────────────────────
sessions: Dict[str, dict] = {}


def get_or_create_session(sender: str) -> dict:
    """Get or create a session for a given sender."""
    if sender not in sessions:
        sessions[sender] = {
            "history": [],
            "state": "greeting",
            "user_profile": {},
            "lang": "en",
            "last_recommendation": "",
            "last_answer": ""
        }
    return sessions[sender]


# ─────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────
@app.get("/")
def read_root():
    return {
        "status": "✅ Welfare Scheme Chatbot API is running.",
        "version": "2.0.0",
        "features": [
            "RAG-based scheme information (10 schemes)",
            "Multilingual: English, Hindi, Tamil, Bengali, Marathi",
            "Code-mixing (Hinglish) support",
            "Eligibility state machine (5-question flow)",
            "Document checklist generation",
            "WhatsApp (Twilio) + SMS channels",
            "Audio/voice note transcription"
        ],
        "endpoints": {
            "whatsapp": "POST /webhook",
            "sms": "POST /sms",
            "checklist": "GET /checklist/{session_id}",
            "health": "GET /health"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "active_sessions": len(sessions)}


# ─────────────────────────────────────────────
# WhatsApp Webhook (Twilio)
# ─────────────────────────────────────────────
@app.post("/webhook")
async def twilio_whatsapp_webhook(request: Request):
    form_data = await request.form()
    
    sender = form_data.get("From", "").strip()
    body = form_data.get("Body", "").strip()
    num_media = int(form_data.get("NumMedia", 0))
    media_content_type = form_data.get("MediaContentType0", "")
    media_url = form_data.get("MediaUrl0", "")
    
    if not sender:
        raise HTTPException(status_code=400, detail="Sender not found in request.")

    session = get_or_create_session(sender)
    
    # ── Handle Audio/Voice Notes ──
    if num_media > 0 and "audio" in media_content_type:
        try:
            transcribed_text = handle_audio_message(media_url)
            body = f"[Voice note transcribed]: {transcribed_text}"
            # Use transcribed text for processing
        except Exception as e:
            print(f"Audio handling error: {e}")
            return _twilio_response("Sorry, I could not process your voice note. Please send a text message. / कृपया टेक्स्ट संदेश भेजें।")
    
    if not body:
        return _twilio_response("Please send a text or voice message. / कृपया टेक्स्ट या वॉइस संदेश भेजें।")
    
    # Store last answer for state parsing
    session["last_answer"] = body
    
    # Add to history
    session["history"].append({"role": "user", "content": body})
    
    # ── Handle "greeting" state: show first question ──
    if session["state"] == "greeting" and len(session["history"]) == 1:
        # First message — detect language and send greeting
        lang = detect_language(body)
        session["lang"] = lang
        greeting = ELIGIBILITY_QUESTIONS["greeting"].get(lang, ELIGIBILITY_QUESTIONS["greeting"]["en"])
        session["state"] = "q_location"
        session["history"].append({"role": "assistant", "content": greeting})
        return _twilio_response(greeting)
    
    # ── Process through chatbot ──
    try:
        reply_text = get_chatbot_response(
            session_id=sender,
            message=body,
            session_state=session
        )
        session["history"].append({"role": "assistant", "content": reply_text})
    except Exception as e:
        print(f"Chatbot error: {e}")
        reply_text = "I am facing technical issues. Please try again. / तकनीकी समस्या है, कृपया पुनः प्रयास करें।"
    
    return _twilio_response(reply_text)


# ─────────────────────────────────────────────
# SMS Endpoint (Twilio SMS)
# ─────────────────────────────────────────────
@app.post("/sms")
async def twilio_sms_webhook(request: Request):
    """
    SMS channel endpoint — works with Twilio SMS webhooks.
    Returns simple TwiML (no WhatsApp-specific formatting).
    """
    form_data = await request.form()
    
    sender = form_data.get("From", "").strip()
    body = form_data.get("Body", "").strip()
    
    if not sender:
        raise HTTPException(status_code=400, detail="Sender not found.")
    
    session = get_or_create_session(f"sms:{sender}")
    session["last_answer"] = body
    session["history"].append({"role": "user", "content": body})
    
    # First message via SMS: send greeting
    if session["state"] == "greeting" and len(session["history"]) == 1:
        lang = detect_language(body)
        session["lang"] = lang
        greeting = ELIGIBILITY_QUESTIONS["greeting"].get(lang, ELIGIBILITY_QUESTIONS["greeting"]["en"])
        # Strip emojis and markdown for SMS compatibility
        greeting_sms = _strip_markdown_for_sms(greeting)
        session["state"] = "q_location"
        session["history"].append({"role": "assistant", "content": greeting_sms})
        return _sms_response(greeting_sms)
    
    try:
        reply_text = get_chatbot_response(
            session_id=f"sms:{sender}",
            message=body,
            session_state=session
        )
        reply_sms = _strip_markdown_for_sms(reply_text)
        session["history"].append({"role": "assistant", "content": reply_sms})
    except Exception as e:
        print(f"SMS chatbot error: {e}")
        reply_sms = "Technical issue. Please try again."
    
    return _sms_response(reply_sms)


# ─────────────────────────────────────────────
# Checklist Endpoint
# ─────────────────────────────────────────────
@app.get("/checklist/{session_id}")
def get_checklist(session_id: str):
    """
    Returns the downloadable/SMS-able document checklist for a session.
    session_id should be URL-encoded (e.g., whatsapp:+91XXXXXXXXXX → whatsapp%3A%2B91XXXXXXXXXX)
    """
    session = sessions.get(session_id)
    if not session:
        return JSONResponse(
            status_code=404,
            content={"error": "Session not found. Please complete the eligibility flow first."}
        )
    
    last_rec = session.get('last_recommendation', '')
    lang = session.get('lang', 'en')
    
    if not last_rec:
        return JSONResponse(
            status_code=400,
            content={"error": "No recommendation generated yet. Please complete the eligibility questions."}
        )
    
    checklist = generate_document_checklist(last_rec, lang)
    return PlainTextResponse(content=checklist, media_type="text/plain; charset=utf-8")


# ─────────────────────────────────────────────
# Session Debug Endpoint (for testing)
# ─────────────────────────────────────────────
@app.get("/session/{session_id}")
def get_session_info(session_id: str):
    """Debug endpoint to inspect session state."""
    session = sessions.get(session_id)
    if not session:
        return JSONResponse(status_code=404, content={"error": "Session not found"})
    return {
        "session_id": session_id,
        "state": session.get("state"),
        "language": session.get("lang"),
        "user_profile": session.get("user_profile"),
        "message_count": len(session.get("history", []))
    }


# ─────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────
def _twilio_response(message: str) -> PlainTextResponse:
    """Wrap a message in Twilio TwiML for WhatsApp."""
    # Escape XML special characters
    message = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{message}</Message>
</Response>"""
    return PlainTextResponse(content=twiml, media_type="application/xml")


def _sms_response(message: str) -> PlainTextResponse:
    """Wrap a message in Twilio TwiML for SMS (max 160 chars per segment)."""
    message = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{message}</Message>
</Response>"""
    return PlainTextResponse(content=twiml, media_type="application/xml")


def _strip_markdown_for_sms(text: str) -> str:
    """Remove WhatsApp markdown formatting for SMS compatibility."""
    import re
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # bold
    text = re.sub(r'_([^_]+)_', r'\1', text)    # italic
    text = re.sub(r'~([^~]+)~', r'\1', text)    # strikethrough
    # Remove common emojis (keep text clean for SMS)
    # Keep the text otherwise readable
    return text.strip()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
