import os
import requests
import json
import base64
from dotenv import load_dotenv
from sarvamai import SarvamAI
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from languages import SUPPORTED_LANGUAGES

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"
client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])

print("==================================================")
print("VAANISETU REAL FUNCTIONALITY AUDIT - FULL SUITE")
print("==================================================")

# 1. Test Document 1: English Notice Text
ENGLISH_DOC_TEXT = """
GOVERNMENT OF KARNATAKA
Department of Revenue & Land Acquisition
Bangalore Rural District

OFFICIAL NOTIFICATION
Notice No.: LA/KRP/2024/99A
Date: 15/02/2024

Under the Land Acquisition Act 2013, notice is hereby given that lands in Sulikere village, KR Puram Taluk are proposed for acquisition for Road Widening Project.

Required Documents to be submitted by land owners:
1. RTC / Pahani Copy
2. Aadhaar Card Duplicate
3. Bank Passbook Copy
4. PAN Card Copy

All land owners must submit the above documents to the Special Land Acquisition Officer, Taluk Office, KR Puram within 30 days of this notice.

Last Date of Submission: 15/03/2024
Compensation Rate: Rs 2,50,000 per gunta.
"""

# 2. Test Document 2: Non-English Notice (Kannada Notice Text)
KANNADA_DOC_TEXT = """
ಕರ್ನಾಟಕ ಸರ್ಕಾರ
ಅಭಿವೃದ್ಧಿ ಮತ್ತು ಭೂಸ್ವಾಧೀನ ಇಲಾಖೆ
ಬೆಂಗಳೂರು ಗ್ರಾಮಾಂತರ ಜಿಲ್ಲೆ

ಅಧಿಕೃತ ಪ್ರಕಟಣೆ
ಕ್ರ.ಸಂ.: ಅ.ಭೂ.ಸ್ವಾ./ಕೆ.ಆರ್.ಪುರಂ/ಬೆಂ.ಗ್ರಾ./2023-24/34H
ದಿನಾಂಕ: ೧೪/೦೧/202೪

ಕರ್ನಾಟಕ ಭೂಸ್ವಾಧೀನ ಕಾಯ್ದೆ 2013ರ ಅಡಿಯಲ್ಲಿ, ಕೆ.ಆರ್.ಪುರಂ ತಾಲ್ಲೂಕಿನ ಸೂಲಿಕೆರೆ ಗ್ರಾಮದಲ್ಲಿ ಪ್ರಸ್ತಾಪಿತ ರಸ್ತೆ ವಿಸ್ತರಣೆ ಯೋಜನೆಗಾಗಿ ಜಮೀನುಗಳನ್ನು ವಶಪಡಿಸಿಕೊಳ್ಳಲು ಪ್ರಸ್ತಾಪಿಸಲಾಗಿದೆ.

ಸಲ್ಲಿಸಬೇಕಾದ ದಾಖಲೆಗಳು:
• ಭೂಮಿ ಮತ್ತು ಪಹಣಿ (RTC)
• ಆಧಾರ್ ಕಾರ್ಡ್ ನಕಲು
• ಬ್ಯಾಂಕ್ ಪಾಸ್ ಬುಕ್ ನಕಲು
• PAN ಕಾರ್ಡ್ ನಕಲು

ದಾಖಲೆಗಳನ್ನು ಕೆ.ಆರ್.ಪುರಂ ತಾಲ್ಲೂಕು ಕಚೇರಿಗೆ ಸಲ್ಲಿಸಬೇಕು.
"""

# Questions per language
LANG_QUESTIONS = {
    "kn-IN": "ಈ ನೋಟಿಸ್ನಲ್ಲಿ ನಾನು ಏನು ಮಾಡಬೇಕು ಮತ್ತು ಕೊನೆಯ ದಿನಾಂಕ ಯಾವುದು?",
    "hi-IN": "इस नोटिस में मुझे क्या करना होगा और अंतिम तिथि क्या है?",
    "ta-IN": "இந்த அறிவிப்பில் நான் என்ன செய்ய வேண்டும் மற்றும் கடைசி தேதி என்ன?",
    "te-IN": "ఈ నోటీసులో నేను ఏమి చేయాలి మరియు చివరి తేదీ ఏమిటి?",
    "ml-IN": "ഈ നോട്ടീസിൽ ഞാൻ എന്താണ് ചെയ്യേണ്ടത്, അവസാന തീയതി ഏതാണ്?",
    "mr-IN": "या नोटीसमध्ये मला काय करावे लागेल आणि शेवटची तारीख काय आहे?",
    "bn-IN": "এই নোটিশে আমাকে কী করতে হবে এবং শেষ তারিখ কী?",
    "gu-IN": "આ નોટિસમાં મારે શું કરવું પડશે અને અંતિમ તારીખ કઈ છે?",
    "pa-IN": "ਇਸ ਨੋਟਿਸ ਵਿੱਚ ਮੈਨੂੰ ਕੀ ਕਰਨਾ ਪਵੇਗਾ ਅਤੇ ਆਖਰੀ ਮਿਤੀ ਕੀ ਹੈ?",
    "en-IN": "What do I need to do in this notice and what is the deadline?"
}

audit_results = {}

print("\n--- PHASE 1: TESTING ENGLISH DOC + 10 REGIONAL VOICES & QUESTIONS ---")

for code, meta in SUPPORTED_LANGUAGES.items():
    lang_name = meta["name"]
    question = LANG_QUESTIONS[code]
    print(f"\nTesting [{lang_name} ({code})]")
    import time
    time.sleep(1.5)
    
    stage_stt = False
    stage_llm = False
    stage_tts = False
    stage_audio_fetch = False
    error_log = []
    
    # Step A: Synthesize test audio for STT and test /api/stt with retry
    for attempt in range(3):
        try:
            tts_res = client.text_to_speech.convert(text=question[:80], language_code=code, output_audio_codec="wav")
            audio_bytes = base64.b64decode(tts_res.audios[0])
            
            # Call /api/stt
            files = {"audio": ("sample_q.wav", audio_bytes, "audio/wav")}
            stt_resp = requests.post(f"{BASE_URL}/api/stt", files=files, data={"language": code}, timeout=30)
            
            if stt_resp.status_code == 200:
                transcript = stt_resp.json().get("transcript", "")
                if transcript:
                    stage_stt = True
                    print(f"  [STT PASS] Transcribed: {transcript[:50]}...")
                    break
                else:
                    error_log.append("STT returned empty transcript")
            else:
                error_log.append(f"STT API returned {stt_resp.status_code}")
        except Exception as e:
            if attempt == 2:
                error_log.append(f"STT Exception: {str(e)}")
            time.sleep(2)

    # Step B: Test /api/analyze (English Doc + Question in Target Language) with retry
    for attempt in range(3):
        try:
            payload = {
                "raw_text": ENGLISH_DOC_TEXT,
                "question": question,
                "language": code
            }
            analyze_resp = requests.post(f"{BASE_URL}/api/analyze", data=payload, timeout=60)
            
            if analyze_resp.status_code == 200:
                data = analyze_resp.json()
                ans_text = data.get("answer", "")
                audio_url = data.get("audio_url")
                
                if ans_text and len(ans_text) > 10:
                    stage_llm = True
                    print(f"  [LLM PASS] Answer ({code}): {ans_text[:80]}...")
                else:
                    error_log.append("LLM returned empty or trivial answer")

                if audio_url:
                    stage_tts = True
                    # Fetch audio file
                    audio_resp = requests.get(f"{BASE_URL}{audio_url}", timeout=15)
                    if audio_resp.status_code == 200 and len(audio_resp.content) > 1000:
                        stage_audio_fetch = True
                        print(f"  [TTS PASS] Audio fetched ({len(audio_resp.content)} bytes)")
                    else:
                        error_log.append(f"Audio fetch failed: HTTP {audio_resp.status_code}")
                else:
                    error_log.append("TTS audio_url was null/missing")
                break
            else:
                error_log.append(f"Analyze API returned {analyze_resp.status_code}: {analyze_resp.text}")
        except Exception as e:
            if attempt == 2:
                error_log.append(f"Analyze Exception: {str(e)}")
            time.sleep(2)

    # Calculate overall status
    if stage_stt and stage_llm and stage_tts and stage_audio_fetch:
        status = "PASS"
    elif stage_llm or stage_stt or stage_tts:
        status = "PARTIAL"
    else:
        status = "FAIL"

    audit_results[code] = {
        "name": lang_name,
        "status": status,
        "stt": stage_stt,
        "llm": stage_llm,
        "tts": stage_tts,
        "audio_fetch": stage_audio_fetch,
        "errors": error_log
    }

print("\n--- PHASE 2: TESTING CROSS-LANGUAGE CASE (Kannada Document + Tamil User Question) ---")
try:
    cross_payload = {
        "raw_text": KANNADA_DOC_TEXT,
        "question": "இந்த அறிவிப்பில் நான் என்ன செய்ய வேண்டும்?",
        "language": "ta-IN"
    }
    cross_resp = requests.post(f"{BASE_URL}/api/analyze", data=cross_payload)
    if cross_resp.status_code == 200:
        c_data = cross_resp.json()
        print(f"Cross-language (Kannada Doc + Tamil User) Answer: {c_data.get('answer')[:120]}...")
        print(f"Grounded: {c_data.get('grounded')}, Audio URL: {c_data.get('audio_url')}")
    else:
        print(f"Cross-language test failed: {cross_resp.status_code}")
except Exception as e:
    print(f"Cross-language exception: {e}")

print("\n==================================================")
print("AUDIT RESULTS SUMMARY")
print("==================================================")
print(f"{'Code':<8} {'Language':<12} {'Status':<10} {'STT':<6} {'LLM':<6} {'TTS':<6} {'Audio':<6}")
print("-" * 55)
for code, res in audit_results.items():
    print(f"{code:<8} {res['name']:<12} {res['status']:<10} {str(res['stt']):<6} {str(res['llm']):<6} {str(res['tts']):<6} {str(res['audio_fetch']):<6}")

with open("scratch/audit_results.json", "w") as f:
    json.dump(audit_results, f, indent=2)

print("\nAudit completed. Results saved to scratch/audit_results.json")
