import os
import requests
import json
import base64
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])

print("Testing Sarvam Saaras v4 with WebM vs WAV audio formats...")

# 1. Synthesize audio in Tamil using TTS
tts_res = client.text_to_speech.convert(
    text="இந்த அறிவிப்பில் நான் என்ன செய்ய வேண்டும்?",
    language_code="ta-IN",
    output_audio_codec="wav"
)
wav_bytes = base64.b64decode(tts_res.audios[0])

# Save as .wav file
with open("scratch/temp_test.wav", "wb") as f:
    f.write(wav_bytes)

# Test STT with .wav file
with open("scratch/temp_test.wav", "rb") as f:
    wav_stt = client.speech_to_text.transcribe(file=f, model="saaras:v4", language_code="ta-IN")
print(f"WAV STT Result: '{wav_stt.transcript}'")

# Clean up temp file
if os.path.exists("scratch/temp_test.wav"):
    os.remove("scratch/temp_test.wav")
