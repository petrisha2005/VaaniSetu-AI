import os
import sys
import json
import time
import requests
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

api_key = os.environ.get("SARVAM_API_KEY", "")

print("==================================================")
print("SARVAM AI NEW KEY & PIPELINE DIAGNOSTIC SUITE")
print("==================================================")

# 1. API Key Masked Verification
if not api_key:
    print("❌ ERROR: SARVAM_API_KEY is missing or empty in .env!")
    sys.exit(1)

masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) >= 8 else "****"
print(f"Loaded API Key: {masked_key} (Length: {len(api_key)})")

client = SarvamAI(api_subscription_key=api_key)

diagnostics = {
    "Document AI": {"status": "UNTESTED", "http": "N/A", "error": "N/A", "root_cause": "N/A"},
    "Saaras STT": {"status": "UNTESTED", "http": "N/A", "error": "N/A", "root_cause": "N/A"},
    "Sarvam 105B": {"status": "UNTESTED", "http": "N/A", "error": "N/A", "root_cause": "N/A"},
    "Bulbul TTS": {"status": "UNTESTED", "http": "N/A", "error": "N/A", "root_cause": "N/A"},
    "Full Pipeline": {"status": "UNTESTED", "http": "N/A", "error": "N/A", "root_cause": "N/A"},
}

def parse_sarvam_error(e):
    err_str = str(e)
    http_code = 500
    err_code = "unknown_error"
    err_msg = err_str

    if "402" in err_str or "insufficient_quota_error" in err_str or "No credits available" in err_str:
        http_code = 402
        err_code = "insufficient_quota_error"
        err_msg = "No credits available in Sarvam account"
    elif "403" in err_str or "invalid_api_key_error" in err_str or "Forbidden" in err_str or "Unauthorized" in err_str:
        http_code = 403
        err_code = "invalid_api_key_error"
        err_msg = "Invalid API key or unauthorized access"
    elif "429" in err_str or "rate_limit_exceeded_error" in err_str:
        http_code = 429
        err_code = "rate_limit_exceeded_error"
        err_msg = "Rate limit exceeded"
    elif "400" in err_str or "invalid_request_error" in err_str:
        http_code = 400
        err_code = "invalid_request_error"
        err_msg = "Invalid request payload"
    elif "413" in err_str:
        http_code = 413
        err_code = "payload_too_large"
        err_msg = "Payload/file too large"
    elif "503" in err_str:
        http_code = 503
        err_code = "service_unavailable"
        err_msg = "Sarvam service unavailable"

    return http_code, err_code, err_msg

# --- TEST 1: SARVAM 105B LLM ---
print("\n[TEST 1] Sarvam 105B LLM Authentication & Completion...")
try:
    res = client.chat.completions(
        model="sarvam-105b",
        messages=[{"role": "user", "content": "Respond with single word: OK"}],
        max_tokens=10
    )
    content = res.choices[0].message.content or ""
    print(f"  ✓ Sarvam 105B PASS: Response = '{content.strip()}'")
    diagnostics["Sarvam 105B"] = {"status": "PASS", "http": "200", "error": "None", "root_cause": "Working normally"}
except Exception as e:
    code, err_code, err_msg = parse_sarvam_error(e)
    print(f"  ❌ Sarvam 105B FAIL (HTTP {code}): [{err_code}] {err_msg}")
    diagnostics["Sarvam 105B"] = {"status": "FAIL", "http": str(code), "error": f"{err_code}: {err_msg}", "root_cause": err_msg}

# --- TEST 2: SAARAS V4 STT ---
print("\n[TEST 2] Sarvam Saaras v4 STT...")
if os.path.exists("question.wav"):
    try:
        with open("question.wav", "rb") as f:
            stt_res = client.speech_to_text.transcribe(
                file=f,
                model="saaras:v4",
                language_code="kn-IN"
            )
        transcript = stt_res.transcript
        print(f"  ✓ Saaras v4 STT PASS: Transcript = '{transcript}'")
        diagnostics["Saaras STT"] = {"status": "PASS", "http": "200", "error": "None", "root_cause": "Working normally"}
    except Exception as e:
        code, err_code, err_msg = parse_sarvam_error(e)
        print(f"  ❌ Saaras STT FAIL (HTTP {code}): [{err_code}] {err_msg}")
        diagnostics["Saaras STT"] = {"status": "FAIL", "http": str(code), "error": f"{err_code}: {err_msg}", "root_cause": err_msg}
else:
    print("  ⚠️ question.wav not found, skipping standalone STT test.")

# --- TEST 3: BULBUL TTS ---
print("\n[TEST 3] Sarvam Bulbul TTS...")
try:
    tts_res = client.text_to_speech.convert(
        text="VaaniSetu AI voice test.",
        language_code="en-IN",
        output_audio_codec="wav"
    )
    if tts_res.audios and len(tts_res.audios[0]) > 100:
        print(f"  ✓ Bulbul TTS PASS: Audio generated successfully ({len(tts_res.audios[0])} base64 chars)")
        diagnostics["Bulbul TTS"] = {"status": "PASS", "http": "200", "error": "None", "root_cause": "Working normally"}
    else:
        print("  ❌ Bulbul TTS returned empty audio list")
        diagnostics["Bulbul TTS"] = {"status": "FAIL", "http": "500", "error": "empty_audio", "root_cause": "No audio returned"}
except Exception as e:
    code, err_code, err_msg = parse_sarvam_error(e)
    print(f"  ❌ Bulbul TTS FAIL (HTTP {code}): [{err_code}] {err_msg}")
    diagnostics["Bulbul TTS"] = {"status": "FAIL", "http": str(code), "error": f"{err_code}: {err_msg}", "root_cause": err_msg}

# --- TEST 4: DOCUMENT AI OCR (TATA DOCUMENT & KANNADA DOCUMENT) ---
print("\n[TEST 4] Sarvam Document AI OCR (Testing Tata Document: sample_notice.png)...")
target_doc = "sample_notice.png" if os.path.exists("sample_notice.png") else "kannada.png"
print(f"  Target Document: {target_doc}")

extracted_text = ""
if os.path.exists(target_doc):
    try:
        with open(target_doc, "rb") as f:
            job = client.doc_ai.digitise(
                file=[(os.path.basename(target_doc), f, "image/png")],
                language="auto",
                output_format="md"
            )
        job_id = job.job_id
        print(f"  Doc AI Job Created: ID {job_id}. Waiting for completion...")
        
        start_t = time.time()
        completed = False
        while time.time() - start_t < 90:
            status = client.doc_ai.get_status(job_id=job_id)
            status_str = status.status.lower()
            if status_str in ["completed", "partially_completed"]:
                completed = True
                break
            elif status_str in ["failed", "rejected"]:
                print(f"  ❌ Doc AI Job {status_str}")
                break
            time.sleep(3)

        if completed:
            download_url = client.doc_ai.get_download_url(job_id=job_id)
            res = requests.get(download_url.url)
            import zipfile, io
            with zipfile.ZipFile(io.BytesIO(res.content)) as z:
                for filename in z.namelist():
                    if filename.endswith(".md"):
                        extracted_text = z.read(filename).decode("utf-8")
                        break
            
            print(f"  ✓ Document AI PASS: Extracted {len(extracted_text)} characters")
            print("  --- Extracted Document Snippet (First 300 chars) ---")
            print(extracted_text[:300])
            print("  ---------------------------------------------------")
            
            # Check for Tata document content or land notice content
            is_tata = "tata" in extracted_text.lower() or "land" in extracted_text.lower() or "notice" in extracted_text.lower() or "ಸರ್ಕಾರ" in extracted_text
            print(f"  Document Content Verification: {'Target Content Confirmed' if is_tata else 'Unexpected Content'}")
            
            diagnostics["Document AI"] = {"status": "PASS", "http": "200", "error": "None", "root_cause": "Working normally"}
        else:
            diagnostics["Document AI"] = {"status": "FAIL", "http": "500", "error": "job_failed", "root_cause": "Doc AI job failed or timed out"}
    except Exception as e:
        code, err_code, err_msg = parse_sarvam_error(e)
        print(f"  ❌ Document AI FAIL (HTTP {code}): [{err_code}] {err_msg}")
        diagnostics["Document AI"] = {"status": "FAIL", "http": str(code), "error": f"{err_code}: {err_msg}", "root_cause": err_msg}

# --- TEST 5: COMPLETE FASTAPI PIPELINE TEST ---
print("\n[TEST 5] Testing Live FastAPI Backend Endpoint (/api/analyze)...")
try:
    files = {}
    if os.path.exists("sample_notice.png"):
        files = {"document": ("sample_notice.png", open("sample_notice.png", "rb"), "image/png")}
    
    data = {
        "question": "What is this notice about and what is the last date?",
        "language": "en-IN"
    }
    
    pipe_resp = requests.post("http://127.0.0.1:8000/api/analyze", files=files if files else None, data=data, timeout=120)
    if pipe_resp.status_code == 200:
        p_json = pipe_resp.json()
        ans = p_json.get("answer", "")
        aud = p_json.get("audio_url")
        quota_warn = p_json.get("quota_exceeded", False)
        
        print(f"  ✓ Full Pipeline PASS (HTTP 200)")
        print(f"  Answer: '{ans[:120]}...'")
        print(f"  Audio URL: {aud}")
        print(f"  Quota Warning Flag: {quota_warn}")
        
        if quota_warn:
            diagnostics["Full Pipeline"] = {"status": "PARTIAL", "http": "200", "error": "quota_fallback", "root_cause": "API Key out of credits, loaded fallback"}
        else:
            diagnostics["Full Pipeline"] = {"status": "PASS", "http": "200", "error": "None", "root_cause": "Complete end-to-end pipeline working with new key"}
    else:
        print(f"  ❌ Full Pipeline HTTP {pipe_resp.status_code}: {pipe_resp.text}")
        diagnostics["Full Pipeline"] = {"status": "FAIL", "http": str(pipe_resp.status_code), "error": pipe_resp.text[:100], "root_cause": "API endpoint returned non-200"}
except Exception as e:
    print(f"  ❌ Full Pipeline Exception: {e}")
    diagnostics["Full Pipeline"] = {"status": "FAIL", "http": "500", "error": str(e), "root_cause": str(e)}

print("\n==================================================")
print("DIAGNOSTIC SUMMARY TABLE")
print("==================================================")
print(f"{'Component':<16} | {'Status':<8} | {'HTTP':<6} | {'Error':<30} | {'Root Cause'}")
print("-" * 90)
for comp, d in diagnostics.items():
    print(f"{comp:<16} | {d['status']:<8} | {d['http']:<6} | {d['error'][:30]:<30} | {d['root_cause']}")

with open("scratch/key_diagnostics.json", "w") as f:
    json.dump({"masked_key": masked_key, "diagnostics": diagnostics, "extracted_text_snippet": extracted_text[:500]}, f, indent=2)
