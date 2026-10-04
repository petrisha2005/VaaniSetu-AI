import os
import re
import json
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

# Initialize SarvamAI client using environment variable
client = SarvamAI(
    api_subscription_key=os.environ["SARVAM_API_KEY"]
)

# 1. Read input document
doc_path = "output/ocr/kannada.png/kannada.md"

with open(doc_path, "r", encoding="utf-8") as f:
    raw_markdown = f.read()

# 2. Minimal OCR cleaning
def clean_ocr_markdown(text: str) -> str:
    # Remove base64 embedded images
    text = re.sub(r'!\[.*?\]\(data:image\/.*?;base64,.*?\)', '', text, flags=re.DOTALL)
    # Remove image markdown tags
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove footnote definitions and references
    text = re.sub(r'\[\^\d+\]:.*', '', text)
    text = re.sub(r'\[\^\d+\]', '', text)
    # Clean excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

cleaned_markdown = clean_ocr_markdown(raw_markdown)

# 3. Question definition
question = "ಈ ನೋಟಿಸ್ನಲ್ಲಿ ನಾನು ಏನು ಮಾಡಬೇಕು ಮತ್ತು ಕೊನೆಯ ದಿನಾಂಕ ಯಾವುದು?"

# 4. Prompts with strict grounding and JSON schema requirement
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
{question}"""

# 5. Call Sarvam LLM
request_succeeded = False
res_json = {}

try:
    response = client.chat.completions(
        model="sarvam-105b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        max_tokens=8192
    )
    
    raw_content = response.choices[0].message.content or ""
    
    # Clean code fences if present in output
    raw_content_cleaned = re.sub(r'^```(?:json)?\s*', '', raw_content.strip(), flags=re.MULTILINE)
    raw_content_cleaned = re.sub(r'\s*```$', '', raw_content_cleaned, flags=re.MULTILINE).strip()
    
    res_json = json.loads(raw_content_cleaned)
    request_succeeded = True

except Exception as e:
    print(f"Error calling Sarvam LLM API or parsing JSON: {e}")
    request_succeeded = False

# 6. Format and Print Output
print("========================================")
print("VAANISETU — 105B GROUNDING TEST")
print("========================================")
print()
print("Question:")
print(question)
print()
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
print("========================================")
print(f"LLM Request Succeeded: {request_succeeded}")
