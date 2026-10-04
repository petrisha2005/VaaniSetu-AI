import os
import re
import json
import base64
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

# Initialize SarvamAI client using environment variable
client = SarvamAI(
    api_subscription_key=os.environ["SARVAM_API_KEY"]
)

os.makedirs("output", exist_ok=True)

# Helper function for OCR cleaning
def clean_ocr_markdown(text: str) -> str:
    text = re.sub(r'!\[.*?\]\(data:image\/.*?;base64,.*?\)', '', text, flags=re.DOTALL)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[\^\d+\]:.*', '', text)
    text = re.sub(r'\[\^\d+\]', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

failed_stage = None
error_message = None

# Step 1: Document OCR loading
ocr_doc_path = "output/ocr/kannada.png/kannada.md"
cleaned_markdown = ""
try:
    with open(ocr_doc_path, "r", encoding="utf-8") as f:
        raw_markdown = f.read()
    cleaned_markdown = clean_ocr_markdown(raw_markdown)
except Exception as e:
    failed_stage = "[1] DOCUMENT"
    error_message = str(e)

# Step 2: Speech-to-Text
transcription = ""
if not failed_stage:
    audio_file = "question.wav"
    try:
        with open(audio_file, "rb") as f:
            stt_response = client.speech_to_text.transcribe(
                file=f,
                model="saaras:v4",
                language_code="kn-IN"
            )
        transcription = stt_response.transcript
    except Exception as e:
        failed_stage = "[2] VOICE INPUT — SAARAS v4"
        error_message = str(e)

# Step 3: Sarvam 105B LLM
res_json = {}
if not failed_stage:
    system_prompt = """You are VaaniSetu, a strictly document-grounded AI assistant for Indian languages.
You must answer questions strictly based ONLY on the provided document.

RULES:
1. Use ONLY information present in the document. Do NOT invent information.
2. Do NOT provide legal advice.
3. If the document does not contain enough information to answer a question or identify an action/deadline, clearly state so in the answer and set missing fields to null.
4. Never fabricate page numbers.
5. You MUST return ONLY a single valid JSON object (no markdown code blocks, no extra text) matching this schema:
{
  "answer": "Detailed answer in Kannada strictly grounded in the document",
  "action": "Explicit action the user needs to take in Kannada, or null if not stated",
  "deadline": "Explicit deadline/last date in Kannada, or null if not stated",
  "evidence": "Exact text excerpt or supporting evidence from the document",
  "grounded": true/false,
  "confidence": "high" | "medium" | "low"
}"""

    user_prompt = f"""DOCUMENT CONTENT:
---
{cleaned_markdown}
---

QUESTION:
{transcription}"""

    try:
        llm_response = client.chat.completions(
            model="sarvam-105b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=8192
        )
        raw_content = llm_response.choices[0].message.content or ""
        raw_content_cleaned = re.sub(r'^```(?:json)?\s*', '', raw_content.strip(), flags=re.MULTILINE)
        raw_content_cleaned = re.sub(r'\s*```$', '', raw_content_cleaned, flags=re.MULTILINE).strip()
        res_json = json.loads(raw_content_cleaned)
    except Exception as e:
        failed_stage = "[3] AI ANSWER — SARVAM 105B"
        error_message = str(e)

# Step 4: Text-to-Speech
output_audio_path = "output/vaanisetu_answer.wav"
if not failed_stage:
    try:
        answer_text = res_json.get("answer", "")
        if not answer_text:
            raise ValueError("LLM did not return an 'answer' string for TTS.")
        
        tts_response = client.text_to_speech.convert(
            text=answer_text,
            language_code="kn-IN",
            output_audio_codec="wav"
        )
        audio_bytes = base64.b64decode(tts_response.audios[0])
        with open(output_audio_path, "wb") as f:
            f.write(audio_bytes)
    except Exception as e:
        failed_stage = "[4] VOICE OUTPUT — BULBUL"
        error_message = str(e)

# Step 5: Report Output
if failed_stage:
    print("END-TO-END RESULT: FAIL")
    print(f"Failed stage: {failed_stage}")
    print(f"Error: {error_message}")
else:
    print("========================================")
    print("VAANISETU — END-TO-END TEST")
    print("========================================")
    print()
    print("[1] DOCUMENT")
    print("OCR source: PASS")
    print()
    print("[2] VOICE INPUT — SAARAS v4")
    print("Transcription:")
    print(transcription)
    print()
    print("STT: PASS")
    print()
    print("[3] AI ANSWER — SARVAM 105B")
    print("Answer:")
    print(res_json.get("answer", "N/A"))
    print()
    print("Action:")
    print(res_json.get("action", "N/A"))
    print()
    print("Deadline:")
    print(res_json.get("deadline", "N/A"))
    print()
    print("Evidence:")
    print(res_json.get("evidence", "N/A"))
    print()
    print("Grounded:")
    print(res_json.get("grounded", "N/A"))
    print()
    print("Confidence:")
    print(res_json.get("confidence", "N/A"))
    print()
    print("LLM: PASS")
    print()
    print("[4] VOICE OUTPUT — BULBUL")
    print("Audio output:")
    print(output_audio_path)
    print()
    print("TTS: PASS")
    print()
    print("========================================")
    print("END-TO-END RESULT: PASS")
    print("========================================")
