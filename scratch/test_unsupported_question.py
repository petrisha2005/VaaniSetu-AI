import os
import re
import json
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])

with open("output/ocr/kannada.png/kannada.md", "r") as f:
    text = f.read()

text = re.sub(r'!\[.*?\]\(data:image\/.*?;base64,.*?\)', '', text, flags=re.DOTALL)
text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
text = re.sub(r'\[\^\d+\]:.*', '', text)
text = re.sub(r'\[\^\d+\]', '', text)
cleaned = re.sub(r'\n{3,}', '\n\n', text).strip()

system_prompt = """You are VaaniSetu, a strictly document-grounded AI assistant.
Answer strictly based ONLY on the provided document.
Target Language: Hindi (hi-IN).

RULES:
1. If the requested information is not present in the document, you MUST set answer to "आई एम सॉरी, लेकिन यह जानकारी अपलोड किए गए दस्तावेज़ में नहीं मिली।" (or in target language), grounded to false, and confidence to "low".
2. Do NOT invent missing information.

Return ONLY a valid JSON object matching this schema:
{
  "answer": "Answer in Hindi",
  "action": null,
  "deadline": null,
  "evidence": "N/A",
  "grounded": false,
  "confidence": "low"
}"""

user_prompt = f"""DOCUMENT CONTENT:
{cleaned}

QUESTION:
फ्रांस की राजधानी क्या है?"""

res = client.chat.completions(
    model="sarvam-105b",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.1,
    max_tokens=2048
)

content = res.choices[0].message.content or ""
content_cleaned = re.sub(r'^```(?:json)?\s*', '', content.strip(), flags=re.MULTILINE)
content_cleaned = re.sub(r'\s*```$', '', content_cleaned, flags=re.MULTILINE).strip()
print("--- REFUSAL OUTPUT ---")
print(content_cleaned)
