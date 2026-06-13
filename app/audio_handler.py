import os
import requests
import base64
import tempfile
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Initialize the new google-genai client
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

def download_twilio_media(media_url: str) -> bytes:
    """Download the media from Twilio using account credentials."""
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    
    response = requests.get(media_url, auth=(account_sid, auth_token))
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to download media. Status code: {response.status_code}")

def handle_audio_message(media_url: str) -> str:
    """
    Downloads the audio from Twilio and uses Gemini to transcribe it.
    """
    audio_content = download_twilio_media(media_url)
    
    # Save temporarily to upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_audio:
        temp_audio.write(audio_content)
        temp_audio_path = temp_audio.name
        
    try:
        # Upload the file using the genai client
        audio_file = client.files.upload(file=temp_audio_path)
        
        # Transcribe using Gemini 2.5 Flash
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                audio_file,
                "Transcribe this audio message exactly as spoken. If it's in Hindi or code-mixed Hindi-English, transcribe it into text. Just return the text."
            ]
        )
        return response.text.strip()
        
    finally:
        # Cleanup
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
