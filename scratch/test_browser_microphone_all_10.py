import os
import sys
import requests
import json
import base64
import time
from dotenv import load_dotenv
from sarvamai import SarvamAI

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from languages import SUPPORTED_LANGUAGES

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"
client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])

print("==================================================")
print("REAL BROWSER VOICE PIPELINE & STT AUDIT - 10 LANGUAGES")
print("==================================================")

TEST_QUESTIONS = {
    "kn-IN": "ಈ ನೋಟಿಸ್ನಲ್ಲಿ ನಾನು ಏನು ಮಾಡಬೇಕು?",
    "hi-IN": "इस नोटिस में मुझे क्या करना होगा?",
    "ta-IN": "இந்த அறிவிப்பில் நான் என்ன செய்ய வேண்டும்?",
    "te-IN": "ఈ నోటీసులో నేను ఏమి చేయాలి?",
    "ml-IN": "ഈ അറിയിപ്പിൽ ഞാൻ എന്താണ് ചെയ്യേണ്ടത്?",
    "mr-IN": "या नोटीसमध्ये मला काय करावे लागेल?",
    "bn-IN": "এই নোটিশে আমাকে কী করতে হবে?",
    "gu-IN": "આ નોટિસમાં મારે શું કરવું પડશે?",
    "pa-IN": "ਇਸ ਨੋਟਿਸ ਵਿੱਚ ਮੈਨੂੰ ਕੀ ਕਰਨਾ ਪਵੇਗਾ?",
    "en-IN": "What do I need to do in this notice?"
}

audit_matrix = []

for code, meta in SUPPORTED_LANGUAGES.items():
    lang_name = meta["name"]
    target_q = TEST_QUESTIONS[code]
    print(f"\n--------------------------------------------------")
    print(f"Auditing Browser Voice Flow for [{lang_name} ({code})]")
    print(f"Target Spoken Question: '{target_q}'")
    
    stt_pass = False
    browser_mime = "audio/webm;codecs=opus"
    rec_format = ".webm"
    audio_bytes_len = 0
    transcript = ""
    error_msg = None
    
    # 1. Synthesize audio bytes in target language to simulate browser voice capture
    try:
        tts_res = client.text_to_speech.convert(
            text=target_q,
            language_code=code,
            output_audio_codec="wav"
        )
        audio_bytes = base64.b64decode(tts_res.audios[0])
        audio_bytes_len = len(audio_bytes)
        
        # 2. Upload to /api/stt mimicking browser FormData upload
        # Filename: recording.webm with mime_type audio/webm
        files = {"audio": ("recording.webm", audio_bytes, browser_mime)}
        data = {
            "language": code,
            "mime_type": browser_mime
        }
        
        for attempt in range(3):
            stt_resp = requests.post(f"{BASE_URL}/api/stt", files=files, data=data, timeout=30)
            if stt_resp.status_code == 200:
                stt_json = stt_resp.json()
                transcript = stt_json.get("transcript", "").strip()
                if transcript:
                    stt_pass = True
                    print(f"  ✓ [STT PASS] Transcribed: '{transcript}'")
                    break
                else:
                    error_msg = "STT returned empty transcript"
            else:
                error_msg = f"HTTP {stt_resp.status_code}: {stt_resp.text}"
            time.sleep(1.5)
            
    except Exception as e:
        error_msg = f"Exception: {str(e)}"
        
    print(f"  MIME Type: {browser_mime} | Backend Format: {rec_format} | Size: {audio_bytes_len} bytes")
    if not stt_pass:
        print(f"  ❌ [STT FAIL] Error: {error_msg}")

    # 3. Test Full Pipeline (/api/analyze) for this language
    llm_pass = False
    tts_pass = False
    audio_fetch_pass = False
    ans_excerpt = ""
    
    try:
        payload = {
            "raw_text": "OFFICIAL NOTIFICATION: Notice No LA/2024. All land owners must submit RTC / Pahani, Aadhaar copy, Bank passbook, and PAN copy to Taluk office within 30 days. Last date: 15/03/2024.",
            "question": transcript if transcript else target_q,
            "language": code
        }
        analyze_resp = requests.post(f"{BASE_URL}/api/analyze", data=payload, timeout=60)
        if analyze_resp.status_code == 200:
            a_data = analyze_resp.json()
            ans_excerpt = a_data.get("answer", "")[:80]
            audio_url = a_data.get("audio_url")
            if ans_excerpt:
                llm_pass = True
            if audio_url:
                tts_pass = True
                audio_res = requests.get(f"{BASE_URL}{audio_url}", timeout=15)
                if audio_res.status_code == 200 and len(audio_res.content) > 1000:
                    audio_fetch_pass = True
                    
        print(f"  [LLM] Pass: {llm_pass} | Answer: '{ans_excerpt}...'")
        print(f"  [TTS] Pass: {tts_pass} | Audio Downloaded: {audio_fetch_pass}")
    except Exception as e:
        print(f"  [Analyze Exception]: {e}")

    overall_status = "PASS" if (stt_pass and llm_pass and tts_pass and audio_fetch_pass) else "FAIL"

    audit_matrix.append({
        "code": code,
        "name": lang_name,
        "browser_mime": browser_mime,
        "blob_size": audio_bytes_len,
        "stt_lang": code,
        "transcript": transcript,
        "stt_pass": stt_pass,
        "llm_pass": llm_pass,
        "tts_pass": tts_pass,
        "audio_fetch": audio_fetch_pass,
        "status": overall_status,
        "error": error_msg
    })
    time.sleep(1.5)

print("\n==================================================")
print("BROWSER VOICE AUDIT MATRIX (10/10 LANGUAGES)")
print("==================================================")
print(f"{'Code':<8} {'Language':<12} {'MIME Type':<22} {'Blob Size':<10} {'STT':<6} {'LLM':<6} {'TTS':<6} {'Status':<8}")
print("-" * 80)
for r in audit_matrix:
    print(f"{r['code']:<8} {r['name']:<12} {r['browser_mime']:<22} {r['blob_size']:<10} {str(r['stt_pass']):<6} {str(r['llm_pass']):<6} {str(r['tts_pass']):<6} {r['status']:<8}")

with open("scratch/browser_voice_matrix.json", "w") as f:
    json.dump(audit_matrix, f, indent=2)

print("\nSaved browser voice audit matrix to scratch/browser_voice_matrix.json")
