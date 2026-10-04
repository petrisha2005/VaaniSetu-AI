import os
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

client = SarvamAI(
    api_subscription_key=os.environ["SARVAM_API_KEY"]
)

audio_file = "question.wav"

with open(audio_file, "rb") as f:
    response = client.speech_to_text.transcribe(
        file=f,
        model="saaras:v4",
        language_code="kn-IN",
    )

print("\nTranscription:")
print(response.transcript)