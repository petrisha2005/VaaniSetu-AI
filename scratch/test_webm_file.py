import os
import requests
import json
import base64
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])

# We test converting WAV bytes to WEBM or testing if Sarvam accepts audio/webm
# First let's check if Sarvam STT works with webm format
print("Checking Sarvam Saaras v4 webm format support...")
# Synthesize audio in wav
tts_res = client.text_to_speech.convert(
    text="ಈ ನೋಟಿಸ್ನಲ್ಲಿ ನಾನು ಏನು ಮಾಡಬೇಕು?",
    language_code="kn-IN",
    output_audio_codec="wav"
)
wav_bytes = base64.b64decode(tts_res.audios[0])

# Write as wav file
with open("scratch/sample_kn.wav", "wb") as f:
    f.write(wav_bytes)

# Test STT with wav
with open("scratch/sample_kn.wav", "rb") as f:
    stt1 = client.speech_to_text.transcribe(file=f, model="saaras:v4", language_code="kn-IN")
print(f"WAV Transcribed: '{stt1.transcript}'")

# Check if Sarvam API returns webm audio or accepts webm file upload
