import os
import re
import json
import uuid
import time
import zipfile
import requests
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sarvamai import SarvamAI
from languages import SUPPORTED_LANGUAGES

load_dotenv()

api_key = os.environ.get("SARVAM_API_KEY")
if not api_key:
    raise ValueError("SARVAM_API_KEY environment variable is missing in .env")

client = SarvamAI(api_subscription_key=api_key)

app = FastAPI(title="VaaniSetu Multilingual AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "output"
UPLOADS_DIR = os.path.join(OUTPUT_DIR, "uploads")
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

def clean_ocr_markdown(text: str) -> str:
    """Removes base64 embedded images, markdown image tags, and footnotes."""
    text = re.sub(r'!\[.*?\]\(data:image\/.*?;base64,.*?\)', '', text, flags=re.DOTALL)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[\^\d+\]:.*', '', text)
    text = re.sub(r'\[\^\d+\]', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# --- REUSABLE SERVICE FUNCTIONS ---

def speech_to_text_service(file_path: str, language_code: str) -> str:
    """Converts user speech to text using Sarvam Saaras v4."""
    lang = language_code if language_code in SUPPORTED_LANGUAGES else "kn-IN"
    with open(file_path, "rb") as f:
        response = client.speech_to_text.transcribe(
            file=f,
            model="saaras:v4",
            language_code=lang
        )
    return response.transcript

def translate_service(text: str, source_lang: str, target_lang: str) -> str:
    """Translates text between languages using Sarvam Translation API."""
    try:
        res = client.text.translate(
            input=text,
            source_language_code=source_lang,
            target_language_code=target_lang
        )
        return res.translated_text
    except Exception as e:
        print(f"Sarvam translate fallback for {source_lang}->{target_lang}: {e}")
        return text

def text_to_speech_service(text: str, language_code: str) -> Optional[str]:
    """Synthesizes voice audio using Sarvam Bulbul TTS for the target language."""
    try:
        lang = language_code if language_code in SUPPORTED_LANGUAGES else "kn-IN"
        tts_response = client.text_to_speech.convert(
            text=text[:500],  # Synthesize text excerpt
            language_code=lang,
            output_audio_codec="wav"
        )
        import base64
        audio_bytes = base64.b64decode(tts_response.audios[0])
        audio_filename = f"answer_{uuid.uuid4().hex[:8]}.wav"
        audio_path = os.path.join(AUDIO_DIR, audio_filename)
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)
        return f"/api/audio/{audio_filename}"
    except Exception as e:
        print(f"TTS generation exception for {language_code}: {e}")
        return None

# --- ENDPOINTS ---

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "VaaniSetu Multilingual API"}

@app.get("/api/languages")
def get_languages():
    return {"languages": list(SUPPORTED_LANGUAGES.values())}

@app.post("/api/stt")
async def speech_to_text_endpoint(audio: UploadFile = File(...), language: str = Form("kn-IN")):
    """Transcribes user voice recording using Sarvam Saaras v4."""
    try:
        audio_bytes = await audio.read()
        temp_audio_path = os.path.join(UPLOADS_DIR, f"voice_{uuid.uuid4().hex[:8]}.wav")
        with open(temp_audio_path, "wb") as f:
            f.write(audio_bytes)

        transcript = speech_to_text_service(temp_audio_path, language)

        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        return {"transcript": transcript, "language": language}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech-to-text failed: {str(e)}")

@app.post("/api/translate")
async def translate_endpoint(
    text: str = Form(...),
    source_language: str = Form("kn-IN"),
    target_language: str = Form("hi-IN")
):
    """Translates text between supported Indian languages."""
    try:
        translated = translate_service(text, source_language, target_language)
        return {"translated_text": translated, "source": source_language, "target": target_language}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@app.post("/api/analyze")
async def analyze_document(
    document: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    question: str = Form(...),
    language: str = Form("kn-IN")
):
    """Multilingual Cross-Language Document Grounding & Answer Generation."""
    try:
        target_lang_meta = SUPPORTED_LANGUAGES.get(language, SUPPORTED_LANGUAGES["kn-IN"])
        target_lang_name = target_lang_meta["name"]
        not_found_msg = target_lang_meta["not_found_text"]

        cleaned_markdown = ""
        
        if document:
            file_ext = os.path.splitext(document.filename)[1].lower()
            if file_ext not in [".png", ".jpg", ".jpeg", ".pdf"]:
                raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PNG, JPG, or PDF.")
            
            doc_bytes = await document.read()
            if len(doc_bytes) > 15 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="File size exceeds 15MB limit.")

            file_id = uuid.uuid4().hex[:8]
            file_path = os.path.join(UPLOADS_DIR, f"{file_id}_{document.filename}")
            with open(file_path, "wb") as f:
                f.write(doc_bytes)

            content_type = document.content_type or "image/png"
            if file_ext == ".pdf":
                content_type = "application/pdf"
            elif file_ext in [".jpg", ".jpeg"]:
                content_type = "image/jpeg"

            # 1. Sarvam Document AI OCR
            with open(file_path, "rb") as f:
                job = client.doc_ai.digitise(
                    file=[(document.filename, f, content_type)],
                    language="auto",
                    output_format="md",
                )

            start_time = time.time()
            while time.time() - start_time < 120:
                status = client.doc_ai.get_status(job_id=job.job_id)
                if status.status.lower() in ["completed", "partially_completed"]:
                    break
                elif status.status.lower() in ["failed", "rejected"]:
                    raise HTTPException(status_code=500, detail=f"Document processing {status.status}")
                time.sleep(3)

            download_url = client.doc_ai.get_download_url(job_id=job.job_id)
            res = requests.get(download_url.url)
            res.raise_for_status()

            zip_path = os.path.join(UPLOADS_DIR, f"ocr_{file_id}.zip")
            with open(zip_path, "wb") as f:
                f.write(res.content)

            extract_dir = os.path.join(UPLOADS_DIR, f"ocr_{file_id}")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            md_content = ""
            for root, _, files in os.walk(extract_dir):
                for file in files:
                    if file.endswith(".md"):
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            md_content = f.read()
                        break

            if not md_content:
                raise HTTPException(status_code=500, detail="Could not extract text from document OCR.")

            cleaned_markdown = clean_ocr_markdown(md_content)

        elif raw_text:
            cleaned_markdown = clean_ocr_markdown(raw_text)
        else:
            raise HTTPException(status_code=400, detail="No document file or text provided.")

        # 2. Sarvam 105B Grounded Reasoning in User's Target Language
        system_prompt = f"""You are VaaniSetu, a strictly document-grounded AI assistant for Indian languages.
You must answer questions strictly based ONLY on the provided document.
Your response MUST be generated entirely in target language: {target_lang_name} ({language}).

RULES:
1. Use ONLY information present in the document. Do NOT invent information.
2. Do NOT provide legal advice.
3. If the requested information is not present in the document, state: "{not_found_msg}" in answer, set grounded to false, and set confidence to "low".
4. Never fabricate page numbers.
5. You MUST return ONLY a single valid JSON object (no markdown code blocks, no extra text) matching this schema:
{{
  "answer": "Detailed answer in {target_lang_name} strictly grounded in the document",
  "action": "Explicit action in {target_lang_name} user needs to take, or null if not stated",
  "deadline": "Explicit deadline/last date in {target_lang_name}, or null if not stated",
  "evidence": "Exact text excerpt or supporting evidence from document",
  "grounded": true/false,
  "confidence": "high" | "medium" | "low"
}}"""

        user_prompt = f"""DOCUMENT CONTENT:
---
{cleaned_markdown}
---

QUESTION ({target_lang_name}):
{question}"""

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
        
        try:
            res_json = json.loads(raw_content_cleaned)
        except Exception:
            res_json = {
                "answer": raw_content_cleaned,
                "action": None,
                "deadline": None,
                "evidence": "Document Analysis",
                "grounded": True,
                "confidence": "medium"
            }

        # 3. Generate Bulbul TTS Audio in User's Selected Language
        answer_text = res_json.get("answer", "")
        audio_url = None
        if answer_text:
            audio_url = text_to_speech_service(answer_text, language)

        return {
            "answer": res_json.get("answer"),
            "action": res_json.get("action"),
            "deadline": res_json.get("deadline"),
            "evidence": res_json.get("evidence"),
            "grounded": res_json.get("grounded", True),
            "confidence": res_json.get("confidence", "high"),
            "audio_url": audio_url,
            "language": language
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/audio/{filename}")
def get_audio(filename: str):
    file_path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/wav")
    raise HTTPException(status_code=404, detail="Audio file not found")
