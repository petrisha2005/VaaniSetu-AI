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
Output your entire JSON response in Hindi (hi-IN).

Return ONLY a valid JSON object matching this schema:
{
  "answer": "Detailed answer in Hindi",
  "action": "Actions in Hindi, or null",
  "deadline": "Deadline in Hindi, or null",
  "evidence": "Excerpt from document",
  "grounded": true,
  "confidence": "high"
}"""

user_prompt = f"""DOCUMENT CONTENT:
{cleaned}

QUESTION:
इस नोटिस में मुझे क्या करना होगा और अंतिम तिथि क्या है?"""

res = client.chat.completions(
    model="sarvam-105b",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.1,
    max_tokens=8192
)

content = res.choices[0].message.content or ""
content_cleaned = re.sub(r'^```(?:json)?\s*', '', content.strip(), flags=re.MULTILINE)
content_cleaned = re.sub(r'\s*```$', '', content_cleaned, flags=re.MULTILINE).strip()
print("--- HINDI OUTPUT ---")
print(content_cleaned)
