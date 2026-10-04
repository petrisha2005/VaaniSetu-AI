import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Health Check
res = requests.get(f"{BASE_URL}/api/health")
print("Health Check:", res.json())

# Languages Check
res_lang = requests.get(f"{BASE_URL}/api/languages")
languages = res_lang.json().get("languages", [])
print(f"Supported Languages Count: {len(languages)}")

# Test cases for Multilingual Grounding
test_cases = [
    {
        "lang": "kn-IN",
        "name": "Kannada",
        "question": "ಈ ನೋಟಿಸ್ನಲ್ಲಿ ನಾನು ಏನು ಮಾಡಬೇಕು ಮತ್ತು ಕೊನೆಯ ದಿನಾಂಕ ಯಾವುದು?"
    },
    {
        "lang": "hi-IN",
        "name": "Hindi",
        "question": "इस नोटिस में मुझे क्या करना होगा और अंतिम तिथि क्या है?"
    },
    {
        "lang": "ta-IN",
        "name": "Tamil",
        "question": "இந்த அறிவிப்பில் நான் என்ன செய்ய வேண்டும் மற்றும் கடைசி தேதி என்ன?"
    },
    {
        "lang": "te-IN",
        "name": "Telugu",
        "question": "ఈ నోటీసులో నేను ఏమి చేయాలి మరియు చివరి తేదీ ఏమిటి?"
    },
    {
        "lang": "en-IN",
        "name": "English",
        "question": "What do I need to do in this notice and what is the deadline?"
    },
    {
        "lang": "hi-IN",
        "name": "Out-of-Bounds Refusal (Hindi)",
        "question": "फ्रांस की राजधानी क्या है?"
    }
]

print("\n========================================")
print("MULTILINGUAL PIPELINE VERIFICATION")
print("========================================")

for test in test_cases:
    payload = {
        "raw_text": "ಕರ್ನಾಟಕ ಸರ್ಕಾರ, ಕೆ.ಆರ್.ಪುರಂ ತಾಲ್ಲೂಕಿನ ಸೂಲಿಕೆರೆ ಗ್ರಾಮದಲ್ಲಿ ರಸ್ತೆ ವಿಸ್ತರಣೆ ಮತ್ತು ಅಭಿವೃದ್ಧಿ ಯೋಜನೆಗಾಗಿ ಭೂಸ್ವಾಧೀನ ಕಾಯ್ದೆ 2013ರ ಅಡಿಯಲ್ಲಿ ಜಮೀನುಗಳನ್ನು ವಶಪಡಿಸಿಕೊಳ್ಳಲು ಪ್ರಸ್ತಾಪಿಸಲಾಗಿದೆ. ದಾಖಲೆಗಳು: ಭೂಮಿ ಮತ್ತು ಪಹಣಿ (RTC), ಆಧಾರ್ ಕಾರ್ಡ್ ನಕಲು, ಬ್ಯಾಂಕ್ ಪಾಸ್ ಬುಕ್ ನಕಲು, PAN ಕಾರ್ಡ್ ನಕಲು. ದಿನಾಂಕ: ೧೪/೦೧/೨೦೨೪.",
        "question": test["question"],
        "language": test["lang"]
    }
    
    response = requests.post(f"{BASE_URL}/api/analyze", data=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"\n[{test['name']} ({test['lang']})]")
        print(f"Question : {test['question']}")
        print(f"Answer   : {data.get('answer')[:120]}...")
        print(f"Grounded : {data.get('grounded')}")
        print(f"Audio URL: {data.get('audio_url')}")
    else:
        print(f"\n[{test['name']}] FAILED: {response.status_code} - {response.text}")

print("\n========================================")
print("TEST COMPLETED SUCCESSFULLY!")
print("========================================")
