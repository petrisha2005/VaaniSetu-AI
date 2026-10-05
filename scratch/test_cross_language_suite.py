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
print("VAANISETU CROSS-LANGUAGE & MULTILINGUAL VERIFICATION")
print("==================================================")

# Sample document texts in different scripts
DOC_ENGLISH = """
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

DOC_KANNADA = """
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
ಕೊನೆಯ ದಿನಾಂಕ: ೧೫/೦೩/೨೦೨೪
"""

DOC_HINDI = """
कर्नाटक सरकार
राजस्व एवं भूमि अधिग्रहण विभाग
बेंगलुरु ग्रामीण जिला

आधिकारिक अधिसूचना
सूचना संख्या: LA/KRP/2024/99A
दिनांक: 15/02/2024

भूमि अधिग्रहण अधिनियम 2013 के तहत, सड़क चौड़ीकरण परियोजना के लिए सुलिकेरे गांव, केआर पुरम तालुक में भूमि अधिग्रहण की सूचना दी जाती है।

आवश्यक दस्तावेज:
1. आरटीसी / पहानी प्रति
2. आधार कार्ड प्रति
3. बैंक पासबुक प्रति
4. पैन कार्ड प्रति

जमा करने की अंतिम तिथि: 15/03/2024
"""

DOC_TAMIL = """
கர்நாடக அரசு
வருவாய் மற்றும் நிலம் கையகப்படுத்தும் துறை
பெங்களூரு ஊரக மாவட்டம்

அதிகாரப்பூர்வ அறிவிப்பு
அறிவிப்பு எண்: LA/KRP/2024/99A
தேதி: 15/02/2024

நிலம் கையகப்படுத்தும் சட்டம் 2013 இன் கீழ், சாலை விரிவாக்கத் திட்டத்திற்காக நிலங்கள் கையகப்படுத்தப்படுகின்றன.

சமர்ப்பிக்க வேண்டிய ஆவணங்கள்:
1. ஆர்டிசி / பஹானி நகல்
2. ஆதார் கார்டு நகல்
3. வங்கி பாஸ்புக் நகல்
4. பான் கார்டு நகல்

கடைசி தேதி: 15/03/2024
"""

CROSS_TEST_CASES = [
    {
        "name": "1. Kannada Doc + Tamil Voice + Tamil TTS",
        "doc": DOC_KANNADA,
        "doc_lang": "kn-IN",
        "user_lang": "ta-IN",
        "question": "இந்த அறிவிப்பில் நான் என்ன செய்ய வேண்டும் மற்றும் கடைசி தேதி என்ன?"
    },
    {
        "name": "2. Kannada Doc + Hindi Voice + Hindi TTS",
        "doc": DOC_KANNADA,
        "doc_lang": "kn-IN",
        "user_lang": "hi-IN",
        "question": "इस नोटिस में मुझे क्या करना होगा और अंतिम तिथि क्या है?"
    },
    {
        "name": "3. Hindi Doc + Kannada Voice + Kannada TTS",
        "doc": DOC_HINDI,
        "doc_lang": "hi-IN",
        "user_lang": "kn-IN",
        "question": "ಈ ನೋಟಿಸ್ನಲ್ಲಿ ನಾನು ಏನು ಮಾಡಬೇಕು ಮತ್ತು ಕೊನೆಯ ದಿನಾಂಕ ಯಾವುದು?"
    },
    {
        "name": "4. English Doc + Tamil Voice + Tamil TTS",
        "doc": DOC_ENGLISH,
        "doc_lang": "en-IN",
        "user_lang": "ta-IN",
        "question": "இந்த அறிவிப்பில் நான் என்ன செய்ய வேண்டும் மற்றும் கடைசி தேதி என்ன?"
    },
    {
        "name": "5. English Doc + Kannada Voice + Kannada TTS",
        "doc": DOC_ENGLISH,
        "doc_lang": "en-IN",
        "user_lang": "kn-IN",
        "question": "ಈ ನೋಟಿಸ್ನಲ್ಲಿ ನಾನು ಏನು ಮಾಡಬೇಕು ಮತ್ತು ಕೊನೆಯ ದಿನಾಂಕ ಯಾವುದು?"
    },
    {
        "name": "6. Tamil Doc + Hindi Voice + Hindi TTS",
        "doc": DOC_TAMIL,
        "doc_lang": "ta-IN",
        "user_lang": "hi-IN",
        "question": "इस नोटिस में मुझे क्या करना होगा और अंतिम तिथि क्या है?"
    },
    {
        "name": "7. English Doc + English Voice + English TTS",
        "doc": DOC_ENGLISH,
        "doc_lang": "en-IN",
        "user_lang": "en-IN",
        "question": "What do I need to do in this notice and what is the last date?"
    }
]

cross_results = []

for tc in CROSS_TEST_CASES:
    print(f"\nRunning: {tc['name']}")
    user_lang = tc["user_lang"]
    question = tc["question"]
    
    # 1. Synthesize voice audio in user's language & run STT endpoint
    stt_pass = False
    try:
        tts_res = client.text_to_speech.convert(text=question[:80], language_code=user_lang, output_audio_codec="wav")
        audio_bytes = base64.b64decode(tts_res.audios[0])
        files = {"audio": ("sample_q.wav", audio_bytes, "audio/wav")}
        stt_resp = requests.post(f"{BASE_URL}/api/stt", files=files, data={"language": user_lang})
        if stt_resp.status_code == 200 and stt_resp.json().get("transcript"):
            stt_pass = True
    except Exception as e:
        print(f"  STT Exception: {e}")

    # 2. Call /api/analyze with cross-language document + question
    analyze_pass = False
    tts_pass = False
    audio_fetch_pass = False
    ans_text = ""
    audio_url = None
    
    try:
        payload = {
            "raw_text": tc["doc"],
            "question": question,
            "language": user_lang
        }
        resp = requests.post(f"{BASE_URL}/api/analyze", data=payload)
        if resp.status_code == 200:
            data = resp.json()
            ans_text = data.get("answer", "")
            audio_url = data.get("audio_url")
            evidence = data.get("evidence", "")
            grounded = data.get("grounded", False)
            
            if ans_text:
                analyze_pass = True
            
            if audio_url:
                tts_pass = True
                # Fetch audio file bytes
                a_resp = requests.get(f"{BASE_URL}{audio_url}")
                if a_resp.status_code == 200 and len(a_resp.content) > 1000:
                    audio_fetch_pass = True

            print(f"  [LLM] Grounded: {grounded} | Answer Excerpt: {ans_text[:70]}...")
            print(f"  [TTS] Audio URL: {audio_url} | Fetch Pass: {audio_fetch_pass}")
            print(f"  [Evidence] {evidence[:60]}...")
        else:
            print(f"  Analyze API error: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"  Analyze Exception: {e}")

    case_status = "PASS" if (stt_pass and analyze_pass and tts_pass and audio_fetch_pass) else "FAIL"
    cross_results.append({
        "case": tc["name"],
        "status": case_status,
        "stt": stt_pass,
        "llm": analyze_pass,
        "tts": tts_pass,
        "audio_fetch": audio_fetch_pass,
        "audio_url": audio_url,
        "answer_excerpt": ans_text[:100]
    })

print("\n==================================================")
print("CROSS-LANGUAGE AUDIT RESULTS SUMMARY")
print("==================================================")
for r in cross_results:
    print(f"[{r['status']}] {r['case']} -> STT:{r['stt']} | LLM:{r['llm']} | TTS:{r['tts']} | AudioFetch:{r['audio_fetch']}")

with open("scratch/cross_language_results.json", "w") as f:
    json.dump(cross_results, f, indent=2)

print("\nSaved cross-language results to scratch/cross_language_results.json")
