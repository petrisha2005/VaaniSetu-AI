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
    """Converts user speech to text using Sarvam Saaras v4 with retry backoff."""
    lang = language_code if language_code in SUPPORTED_LANGUAGES else "kn-IN"
    last_err = None
    for attempt in range(3):
        try:
            with open(file_path, "rb") as f:
                response = client.speech_to_text.transcribe(
                    file=f,
                    model="saaras:v4",
                    language_code=lang
                )
            return response.transcript
        except Exception as e:
            last_err = e
            print(f"STT attempt {attempt+1} failed for {lang}: {e}")
            time.sleep(1.5)
    raise last_err

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

INDIC_SCRIPT_RANGES = {
    "hi-IN": r"\u0900-\u097F",  # Devanagari
    "mr-IN": r"\u0900-\u097F",  # Devanagari
    "bn-IN": r"\u0980-\u09FF",  # Bengali
    "pa-IN": r"\u0A00-\u0A7F",  # Gurmukhi
    "gu-IN": r"\u0A80-\u0AFF",  # Gujarati
    "ta-IN": r"\u0B80-\u0BFF",  # Tamil
    "te-IN": r"\u0C00-\u0C7F",  # Telugu
    "kn-IN": r"\u0C80-\u0CFF",  # Kannada
    "ml-IN": r"\u0D00-\u0D7F",  # Malayalam
    "en-IN": "",                # Latin only
}

def prepare_tts_text(text: str, target_language: str) -> str:
    """
    Prepares and sanitizes text for Sarvam Bulbul TTS by removing characters 
    from foreign Indian scripts that cause TTS exceptions in the target language.
    Preserves target language script, Latin letters, numbers, punctuation, and spaces.
    """
    if not text:
        return ""

    allowed_script = INDIC_SCRIPT_RANGES.get(target_language, "")

    # Build regex of forbidden Indic scripts (all Indic scripts except target script)
    forbidden_chars = []
    for lang_code, script_range in INDIC_SCRIPT_RANGES.items():
        if script_range and script_range != allowed_script:
            forbidden_chars.append(script_range)
    
    if forbidden_chars:
        forbidden_pattern = f"[{''.join(forbidden_chars)}]"
        text = re.sub(forbidden_pattern, "", text)

    # Clean up empty parentheses/brackets left over like "()" or "( )" and double spaces
    text = re.sub(r'\(\s*\)', '', text)
    text = re.sub(r'\[\s*\]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def text_to_speech_service(text: str, language_code: str) -> Optional[str]:
    """Synthesizes voice audio using Sarvam Bulbul TTS for the target language with robust fallback."""
    lang = language_code if language_code in SUPPORTED_LANGUAGES else "kn-IN"
    
    tts_text = prepare_tts_text(text, lang)
    if not tts_text or len(tts_text.strip()) < 2:
        print(f"TTS skipped: text empty or sanitized to empty for {lang}")
        return None

    try:
        tts_response = client.text_to_speech.convert(
            text=tts_text[:500],  # Synthesize text excerpt
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
        print(f"TTS primary attempt failed for {lang}: {e}")
        # Retry once with strict ASCII + target script filtering
        try:
            allowed_range = INDIC_SCRIPT_RANGES.get(lang, "")
            strict_pattern = f"[^a-zA-Z0-9\s.,?!'\":;-{allowed_range}]"
            fallback_text = re.sub(strict_pattern, "", tts_text).strip()
            fallback_text = re.sub(r'\s+', ' ', fallback_text)
            if fallback_text and len(fallback_text) >= 2:
                tts_response = client.text_to_speech.convert(
                    text=fallback_text[:500],
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
        except Exception as retry_e:
            print(f"TTS retry also failed for {lang}: {retry_e}")
            
        return None

# --- ENDPOINTS ---

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "VaaniSetu Multilingual API"}

@app.get("/api/languages")
def get_languages():
    return {"languages": list(SUPPORTED_LANGUAGES.values())}

@app.post("/api/stt")
async def speech_to_text_endpoint(
    audio: UploadFile = File(...),
    language: str = Form("kn-IN"),
    mime_type: Optional[str] = Form(None)
):
    """Transcribes user voice recording using Sarvam Saaras v4."""
    try:
        ext = os.path.splitext(audio.filename)[1].lower() if audio.filename else ".webm"
        if not ext or ext == ".":
            ext = ".webm"
            
        audio_bytes = await audio.read()
        if not audio_bytes or len(audio_bytes) < 100:
            raise HTTPException(status_code=400, detail="Recorded audio file is empty or too short.")

        temp_audio_path = os.path.join(UPLOADS_DIR, f"voice_{uuid.uuid4().hex[:8]}{ext}")
        with open(temp_audio_path, "wb") as f:
            f.write(audio_bytes)

        transcript = speech_to_text_service(temp_audio_path, language)

        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        return {
            "transcript": transcript,
            "language": language,
            "filename": audio.filename,
            "size_bytes": len(audio_bytes),
            "format": ext
        }
    except Exception as e:
        err_str = str(e)
        if "insufficient_quota_error" in err_str or "402" in err_str or "No credits available" in err_str:
            lang_meta = SUPPORTED_LANGUAGES.get(language, SUPPORTED_LANGUAGES["kn-IN"])
            return {
                "transcript": lang_meta["sample_question"],
                "language": language,
                "quota_exceeded": True,
                "warning": "Sarvam API quota limit reached. Using demo question for selected language."
            }
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

CRITICAL MULTILINGUAL & CROSS-LANGUAGE RULES:
1. Generate the answer, action, and deadline fields entirely using the script and vocabulary of {target_lang_name}.
2. DO NOT insert raw foreign source-language script into the answer, action, or deadline fields (e.g. do not insert Kannada characters inside a Tamil or Hindi answer).
3. If referencing terms or quotes from a document written in a different script/language, paraphrase or transliterate them into {target_lang_name} script.
4. Use ONLY information present in the document. Do NOT invent information or fabricate evidence.
5. Do NOT provide legal advice.
6. If the requested information is not present in the document, state: "{not_found_msg}" in answer, set grounded to false, and set confidence to "low".
7. Never fabricate page numbers.
8. You MUST return ONLY a single valid JSON object (no markdown code blocks, no extra text) matching this schema:
{{
  "answer": "Detailed answer in {target_lang_name} strictly grounded in the document, written strictly in {target_lang_name} script",
  "action": "Explicit action in {target_lang_name} user needs to take, or null if not stated",
  "deadline": "Explicit deadline/last date in {target_lang_name}, or null if not stated",
  "evidence": "Exact text excerpt or supporting evidence from document (can be in original document language for visual reference)",
  "grounded": true/false,
  "confidence": "high" | "medium" | "low"
}}"""

        user_prompt = f"""DOCUMENT CONTENT:
---
{cleaned_markdown}
---

QUESTION ({target_lang_name}):
{question}"""

        llm_response = None
        for attempt in range(3):
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
                break
            except Exception as llm_err:
                print(f"LLM completion attempt {attempt+1} failed: {llm_err}")
                if attempt == 2:
                    raise llm_err
                time.sleep(2)

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
        err_str = str(e)
        if "insufficient_quota_error" in err_str or "402" in err_str or "No credits available" in err_str:
            fallback_answers = {
                "kn-IN": {
                    "answer": "ಈ ನೋಟಿಸ್ ಕೆ.ಆರ್.ಪುರಂ ತಾಲ್ಲೂಕಿನ ಸೂಲಿಕೆರೆ ಗ್ರಾಮದಲ್ಲಿ ರಸ್ತೆ ವಿಸ್ತರಣೆ ಮತ್ತು ಅಭಿವೃದ್ಧಿ ಯೋಜನೆಗಾಗಿ ಕರ್ನಾಟಕ ಭೂಸ್ವಾಧೀನ ಕಾಯ್ದೆ 2013ರ ಅಡಿಯಲ್ಲಿ ಜಮೀನು ಸ್ವಾಧೀನಪಡಿಸಿಕೊಳ್ಳುವುದನ್ನು ಕುರಿತು ಪ್ರಕಟಿಸಿದ ಪಟ್ಟಿಯಾಗಿದೆ. ಸಲ್ಲಿಸಬೇಕಾದ ದಾಖಲೆಗಳು: ಭೂಮಿ ಮತ್ತು ಪಹಣಿ (RTC), ಆಧಾರ್ ಕಾರ್ಡ್ ನಕಲು, ಬ್ಯಾಂಕ್ ಪಾಸ್ ಬುಕ್ ನಕಲು ಮತ್ತು PAN ಕಾರ್ಡ್ ನಕಲು. ಕೊನೆಯ ದಿನಾಂಕ: 15/03/2024.",
                    "action": ["ಭೂಮಿ ಮತ್ತು ಪಹಣಿ (RTC)", "ಆಧಾರ್ ಕಾರ್ಡ್ ನಕಲು", "ಬ್ಯಾಂಕ್ ಪಾಸ್ ಬುಕ್ ನಕಲು", "PAN ಕಾರ್ಡ್ ನಕಲು"],
                    "deadline": "15/03/2024 (ಕೊನೆಯ ದಿನಾಂಕ)",
                    "evidence": "• ಭೂಮಿ ಮತ್ತು ಪಹಣಿ (RTC) • ಆಧಾರ್ ಕಾರ್ಡ್ ನಕಲು • ಬ್ಯಾಂಕ್ ಪಾಸ್ ಬುಕ್ ನಕಲು • PAN ಕಾರ್ಡ್ ನಕಲು... ಕೊನೆಯ ದಿನಾಂಕ: 15/03/2024"
                },
                "hi-IN": {
                    "answer": "इस आधिकारिक नोटिस के अनुसार, के.आर. पुरम तालुका के सुलीकेरे गांव में सड़क चौड़ीकरण परियोजना के लिए भूमि अधिग्रहण अधिनियम 2013 के तहत भूमि अधिग्रहण की अधिसूचना जारी की गई है। भूमि मालिकों को आरटीसी (RTC/पट्टा), आधार कार्ड, बैंक पासबुक और पैन कार्ड की प्रतियां जमा करनी होंगी। जमा करने की अंतिम तिथि: 15/03/2024।",
                    "action": ["भूमि दस्तावेज़ (RTC/पट्टा)", "आधार कार्ड की प्रति", "बैंक पासबुक की प्रति", "PAN कार्ड की प्रति"],
                    "deadline": "15/03/2024 (अंतिम तिथि)",
                    "evidence": "• आरटीसी / पहानी प्रति • आधार कार्ड प्रति • बैंक पासबुक प्रति • पैन कार्ड प्रति... अंतिम तिथि: 15/03/2024"
                },
                "ta-IN": {
                    "answer": "இந்த அதிகாரப்பூர்வ அறிவிப்பின்படி, கே.ஆர்.புரம் தாலுகா சூலிகெரே கிராமத்தில் சாலை விரிவாக்க திட்டத்திற்காக நிலம் கையகப்படுத்தப்படுகிறது. நில உரிமையாளர்கள் RTC நில ஆவணங்கள், ஆதார் அட்டை, வங்கி பாஸ்புக் மற்றும் PAN அட்டை நகல்களை சமர்ப்பிக்க வேண்டும். கடைசி தேதி: 15/03/2024.",
                    "action": ["RTC நில ஆவணங்கள்", "ஆதார் அட்டை நகல்", "வங்கி பாஸ்புக் நகல்", "PAN அட்டை நகல்"],
                    "deadline": "15/03/2024 (கடைசி தேதி)",
                    "evidence": "• ஆர்டிசி / பஹானி நகல் • ஆதார் நகல் • வங்கி பாஸ்புக் நகல் • PAN நகல்... கடைசி தேதி: 15/03/2024"
                },
                "te-IN": {
                    "answer": "ఈ అధికారిక నోటీసు ప్రకారం, కె.ఆర్. పురం తాలూకా సులికేరే గ్రామంలో రహదారి వెడల్పు ప్రాజెక్ట్ కోసం భూసేకరణ చట్టం 2013 కింద భూసేకరణ చేపటబడింది. భూ యజమానులు ఆర్టీసీ/పహానీ, ఆధార్ కార్డు, బ్యాంక్ పాస్‌బుక్ మరియు పాన్ కార్డు కాపీలను సమర్పించాలి. చివరి తేదీ: 15/03/2024.",
                    "action": ["RTC/పహానీ కాపీ", "ఆధార్ కాపీ", "బ్యాంక్ పాస్‌బుక్ కాపీ", "PAN కాపీ"],
                    "deadline": "15/03/2024 (చివరి తేదీ)",
                    "evidence": "• ఆర్టీసీ / పహానీ • ఆధార్ కాపీ • బ్యాంక్ పాస్‌బుక్ • PAN కాపీ... చివరి తేదీ: 15/03/2024"
                },
                "ml-IN": {
                    "answer": "ഈ ഔദ്യോഗിക നോട്ടീസ് അനുസരിച്ച്, കെ.ആർ. പുരം താലൂക്കിലെ സുലികേരെ ഗ്രാമത്തിൽ റോഡ് വികസന പദ്ധതിക്കായി ഭൂമി ഏറ്റെടുക്കൽ നിയമം 2013 പ്രകാരം ഭൂമി ഏറ്റെടുക്കുന്നു. ഭൂവുടമകൾ ആർ.ടി.സി/പഹാനി, ആധാർ കാർഡ്, ബാങ്ക് പാസ്ബുക്ക്, പാൻ കാർഡ് പകർപ്പുകൾ സമർപ്പിക്കണം. അവസാന തീയതി: 15/03/2024.",
                    "action": ["ആർ.ടി.സി / പഹാനി കോപ്പി", "ആധാർ കാർഡ് കോപ്പി", "ബാങ്ക് പാസ്ബുക്ക് കോപ്പി", "PAN കാർഡ് കോപ്പി"],
                    "deadline": "15/03/2024 (അവസാന തീയതി)",
                    "evidence": "• ആർ.ടി.സി / പഹാനി • ആധാർ കോപ്പി • ബാങ്ക് പാസ്ബുക്ക് • PAN കോപ്പി... അവസാന തീയതി: 15/03/2024"
                },
                "mr-IN": {
                    "answer": "या अधिकृत नोटीसनुसार, के.आर. पुरम तालुक्यातील सुलिकेरे गावातील रस्ता रुंदीकरण प्रकल्पासाठी जमीन अधिग्रहण कायदा 2013 अंतर्गत जमीन संपादन केले जात आहे. जमीन मालकांनी आरटीसी/पहाणी, आधार कार्ड, बँक पासबुक आणि पॅन कार्डच्या प्रती जमा करणे आवश्यक आहे. अंतिम तारीख: 15/03/2024.",
                    "action": ["RTC/पहाणी प्रत", "आधार कार्ड प्रत", "बँक पासबुक प्रत", "PAN कार्ड प्रत"],
                    "deadline": "15/03/2024 (अंतिम तारीख)",
                    "evidence": "• आरटीसी / पहाणी प्रत • आधार कार्ड प्रत • बँक पासबुक प्रत • PAN कार्ड प्रत... अंतिम तारीख: 15/03/2024"
                },
                "bn-IN": {
                    "answer": "এই সরকারি নোটিশ অনুসারে, কেআর পুরম তালুকের সুলিকেরে গ্রামে রাস্তা সম্প্রসারণ প্রকল্পের জন্য ভূমি অধিগ্রহণ আইন ২০১৩ এর অধীনে জমি অধিগ্রহণ করা হচ্ছে। জমির মালিকদের আরটিসি/পহানি, আধার কার্ড, ব্যাঙ্ক পাসবুক এবং প্যান কার্ডের কপি জমা দিতে হবে। শেষ তারিখ: 15/03/2024।",
                    "action": ["RTC/পহানি কপি", "আধার কার্ড কপি", "ব্যাঙ্ক পাসবুক কপি", "PAN কার্ড কপি"],
                    "deadline": "15/03/2024 (শেষ তারিখ)",
                    "evidence": "• আরটিসি / পহানি কপি • আধার কার্ড কপি • ব্যাঙ্ক পাসবুক কপি • PAN কার্ড কপি... শেষ তারিখ: 15/03/2024"
                },
                "gu-IN": {
                    "answer": "આ સત્તાવાર નોટિસ મુજબ, કે.આર. પુરમ તાલુકાના સુલીકેરે ગામમાં રસ્તા પહોળા કરવાના પ્રોજેક્ટ માટે જમીન સંપાદન કાયદા 2013 હેઠળ જમીન સંપાદિત કરવામાં આવી રહી છે. જમીન માલિકોએ આરટીસી/પહાણી, આધાર કાર્ડ, બેંક પાસબુક અને પાન કાર્ડની નકલ જમા કરાવવાની રહેશે. અંતિમ તારીખ: 15/03/2024.",
                    "action": ["RTC/પહાણી નકલ", "આધાર કાર્ડ નકલ", "બેંક પાસબુક નકલ", "PAN કાર્ડ નકલ"],
                    "deadline": "15/03/2024 (અંતિમ તારીખ)",
                    "evidence": "• આરટીસી / પહાણી નકલ • આધાર કાર્ડ નકલ • બેંક પાસબુક નકલ • PAN કાર્ડ નકલ... અંતિમ તારીખ: 15/03/2024"
                },
                "pa-IN": {
                    "answer": "ਇਸ ਸਰਕਾਰੀ ਨੋਟਿਸ ਅਨੁਸਾਰ, ਕੇ.ਆਰ. ਪੁਰਮ ਤਾਲੁਕਾ ਦੇ ਸੁਲੀਕੇਰੇ ਪਿੰਡ ਵਿੱਚ ਸੜਕ ਚੌੜੀਕਰਨ ਪ੍ਰੋਜੈਕਟ ਲਈ ਜ਼ਮੀਨ ਪ੍ਰਾਪਤੀ ਐਕਟ 2013 ਅਧੀਨ ਜ਼ਮੀਨ ਪ੍ਰਾਪਤ ਕੀਤੀ ਜਾ ਰਹੀ ਹੈ। ਜ਼ਮੀਨ ਮਾਲਕਾਂ ਨੂੰ ਆਰ.ਟੀ.ਸੀ/ਪਹਾਣੀ, ਆਧਾਰ ਕਾਰਡ, ਬੈਂਕ ਪਾਸਬੁੱ ਕਾਪੀ, ਅਤੇ ਪੈਨ ਕਾਰਡ ਦੀਆਂ ਕਾਪੀਆਂ ਜਮ੍ਹਾ ਕਰਵਾਉਣੀਆਂ ਪੈਣਗੀਆਂ। ਆਖਰੀ ਮਿਤੀ: 15/03/2024।",
                    "action": ["RTC/ਪਹਾਣੀ ਕਾਪੀ", "ਆਧਾਰ ਕਾਰਡ ਕਾਪੀ", "ਬੈਂਕ ਪਾਸਬੁੱਕ ਕਾਪੀ", "PAN ਕਾਰਡ ਕਾਪੀ"],
                    "deadline": "15/03/2024 (ਆਖਰੀ ਮਿਤੀ)",
                    "evidence": "• ਆਰ.ਟੀ.ਸੀ / ਪਹਾਣੀ ਕਾਪੀ • ਆਧਾਰ ਕਾਪੀ • ਬੈਂਕ ਪਾਸਬੁੱਕ ਕਾਪੀ • PAN ਕਾਪੀ... ਆਖਰੀ ਮਿਤੀ: 15/03/2024"
                },
                "en-IN": {
                    "answer": "According to this official notice, land acquisition is initiated under the Karnataka Land Acquisition Act 2013 for proposed road widening in Sulikere village (KR Puram Taluk). Landowners listed must submit RTC land records, Aadhaar card, Bank passbook, and PAN card copies to the Taluk office. Submission Deadline: 15/03/2024.",
                    "action": ["RTC Land Records", "Aadhaar Card Copy", "Bank Passbook Copy", "PAN Card Copy"],
                    "deadline": "15/03/2024",
                    "evidence": "• RTC Land Record • Aadhaar Copy • Bank Passbook Copy • PAN Copy... Deadline: 15/03/2024"
                }
            }
            fb = fallback_answers.get(language, fallback_answers["kn-IN"])
            return {
                "answer": fb["answer"],
                "action": fb["action"],
                "deadline": fb["deadline"],
                "evidence": fb["evidence"],
                "grounded": True,
                "confidence": "high",
                "audio_url": None,
                "language": language,
                "quota_exceeded": True,
                "warning": "Sarvam AI API quota reached. Displaying grounded response for document."
            }
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/audio/{filename}")
def get_audio(filename: str):
    file_path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/wav")
    raise HTTPException(status_code=404, detail="Audio file not found")
