# 🌉 VaaniSetu AI

### Understand. Ask. Act. — In Your Language.

**VaaniSetu AI** is a multilingual document and voice understanding assistant designed to help people understand important documents in their own Indian language.

Instead of forcing users to understand complex English or formal documents, VaaniSetu allows them to:

> 📄 Upload a document → 🎙️ Ask a question in their language → 🤖 Get a document-grounded answer → 🔊 Listen to the answer in the same language.

Built using **Sarvam AI's language and speech capabilities**.

---
**🚀 Live Demo**

Try VaaniSetu AI: https://vaani-setu-ai.vercel.app/

Upload a document, ask a question in your preferred Indian language, and get a grounded answer with Sarvam Vision + Saaras STT + Sarvam 105B + Bulbul TTS.



-----
## 🚀 Why VaaniSetu?

Important documents can contain information that directly affects people's lives:

- Government notices
- Property documents
- Tax notices
- College/education notices
- Application documents
- Bills and official letters
- Business documents
- Public-service communications

The problem isn't always access to the document.

The problem is **understanding it**.

Many documents use:

- Formal terminology
- Complex language
- English-heavy content
- Long paragraphs
- Important deadlines hidden inside text
- Instructions that are difficult for non-English-first users

VaaniSetu aims to remove this **language and understanding barrier**.

---

# 🎯 Problem Statement

India has a large and diverse population with many people more comfortable communicating in regional languages than English.

When users receive an important document, they may struggle to understand:

- What the document is about
- What action they need to take
- What the deadline is
- Which documents are required
- What specific section of the document answers their question

Existing document AI tools often focus primarily on summarization or English-first interaction.

### The core question:

> **What if people could simply ask their document a question in their own language and hear the answer?**

That's what VaaniSetu is designed to enable.

---

# 💡 Solution

VaaniSetu is a **multilingual, document-grounded voice assistant**.

Users can upload an important document and interact with it using **voice or text**.

### Core workflow

```text
        📄 DOCUMENT
             │
             ▼
   ┌─────────────────────┐
   │ Document Intelligence│
   │      / OCR           │
   └──────────┬──────────┘
              │
              ▼
      📚 Document Context
              │
              │
       🎙️ Voice Question
              │
              ▼
       Saaras Speech-to-Text
              │
              ▼
       🧠 Sarvam Reasoning
              │
              ▼
     📌 Grounded Answer
              │
              ▼
       🌐 Target Language
              │
              ▼
        🔊 Bulbul TTS
              │
              ▼
       🎧 Spoken Answer
```

### In one line:

**Document → Understand → Ask → Answer → Translate → Speak**

---

# ✨ Key Features

## 📄 1. Document Understanding

Upload an important document and extract useful information from it.

VaaniSetu can help identify:

* Document type
* Main purpose
* Important information
* Required actions
* Deadlines
* Relevant entities
* Supporting content

---

## 🎙️ 2. Voice Questions

Users can ask questions naturally instead of typing long queries.

Example:

> "இந்த அறிவிப்பில் நான் என்ன செய்ய வேண்டும்?"

or

> "इस नोटिस में मुझे क्या करना होगा?"

or

> "ಈ ನೋಟಿಸ್‌ನಲ್ಲಿ ನಾನು ಏನು ಮಾಡಬೇಕು?"

The voice input is converted into text using **Sarvam Saaras**.

---

## 🌐 3. Indian Language Support

VaaniSetu is designed for multilingual interaction.

Current supported language configuration:

| Language  | Code    |
| --------- | ------- |
| English   | `en-IN` |
| Hindi     | `hi-IN` |
| Kannada   | `kn-IN` |
| Tamil     | `ta-IN` |
| Telugu    | `te-IN` |
| Malayalam | `ml-IN` |
| Marathi   | `mr-IN` |
| Bengali   | `bn-IN` |
| Gujarati  | `gu-IN` |
| Punjabi   | `pa-IN` |

The selected language is used throughout the interaction wherever supported.

---

## 🧠 4. Document-Grounded Answers

VaaniSetu is not intended to behave like a generic chatbot.

Answers are generated using the uploaded document as the primary context.

This helps users understand:

* What the document says
* What action is required
* Where the information appears
* Which deadline is mentioned

The system is designed to avoid answering unrelated questions without relevant document context.

---

## 📌 5. Action-Oriented Answers

Instead of simply producing a long summary, VaaniSetu focuses on helping the user **act**.

For example:

### User asks:

> "What do I need to do before the deadline?"

### VaaniSetu:

> **You need to submit the required documents before 30 October 2026.**

The goal is to surface the information that matters most to the user.

---

## 🔊 6. Text-to-Speech

Users can listen to the answer instead of reading it.

The answer is converted into speech using **Sarvam Bulbul**.

This makes the interaction more accessible for users who prefer listening over reading.

---

## 🔍 7. Source-Aware Responses

Where possible, the system can associate answers with relevant document content.

Example:

```text
Answer:
You need to submit your response before 30 October 2026.

Source:
Page 3
```

This improves transparency and helps users verify the information.

---

# 🧩 Why Sarvam?

VaaniSetu is built around the idea that **Indian-language interaction should be a first-class experience**.

Sarvam provides multiple capabilities that fit directly into this workflow.

### VaaniSetu + Sarvam

| Requirement            | Sarvam Capability               |
| ---------------------- | ------------------------------- |
| Document understanding | Sarvam Document Intelligence    |
| Voice input            | Saaras Speech-to-Text           |
| Language processing    | Sarvam language models          |
| Translation            | Sarvam Translation capabilities |
| Voice output           | Bulbul Text-to-Speech           |

This creates a complete multilingual interaction pipeline:

```text
Document
   ↓
Sarvam Document Intelligence
   ↓
Document Context
   ↓
Saaras STT
   ↓
Sarvam Reasoning
   ↓
Target Language Answer
   ↓
Bulbul TTS
   ↓
Voice Response
```

### Why this matters

The goal isn't simply:

> "Summarize my document."

The goal is:

> **"Let me understand and interact with my document in the language I am comfortable speaking."**

---

# 🏗️ System Architecture

```text
                         ┌──────────────────┐
                         │      USER        │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
             📄 Upload Document            🎙️ Voice Question
                    │                           │
                    ▼                           ▼
       ┌──────────────────────┐       ┌──────────────────────┐
       │ Sarvam Document AI   │       │   Saaras STT         │
       │       / OCR          │       │ Speech → Text        │
       └──────────┬───────────┘       └──────────┬───────────┘
                  │                              │
                  ▼                              ▼
           Document Context              User Question
                  │                              │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                     ┌─────────────────────┐
                     │  Sarvam Reasoning   │
                     │   + Grounding       │
                     └──────────┬──────────┘
                                │
                                ▼
                        Grounded Answer
                                │
                                ▼
                     ┌─────────────────────┐
                     │ Language Processing │
                     │ / Translation       │
                     └──────────┬──────────┘
                                │
                                ▼
                       Target Language
                                │
                                ▼
                     ┌─────────────────────┐
                     │     Bulbul TTS      │
                     │ Text → Speech       │
                     └──────────┬──────────┘
                                │
                                ▼
                         🔊 Voice Answer
```

---

# 🔄 Data Flow

```text
USER
 │
 │ Upload document
 ▼
DOCUMENT PROCESSING
 │
 │ OCR / Document Intelligence
 ▼
EXTRACTED DOCUMENT CONTENT
 │
 ▼
DOCUMENT CONTEXT
 │
 │
 │ User asks question
 ▼
VOICE INPUT
 │
 │ Saaras STT
 ▼
TRANSCRIBED QUESTION
 │
 ▼
AI REASONING
 │
 │ Uses document context
 ▼
GROUNDED ANSWER
 │
 ▼
TARGET LANGUAGE
 │
 │ Bulbul TTS
 ▼
SPOKEN RESPONSE
 │
 ▼
USER
```

### Grounding principle

```text
No relevant document context
          ↓
   Don't fabricate an answer
          ↓
Ask the user to clarify / explain
```

---

# 🛠️ Tech Stack

## Frontend

* React
* Vite
* JavaScript / TypeScript
* Modern responsive UI
* Browser microphone APIs
* Audio playback

## Backend

* Python
* FastAPI
* REST APIs

## AI / Language

* Sarvam Document Intelligence
* Sarvam Saaras Speech-to-Text
* Sarvam language models
* Sarvam Translation capabilities
* Sarvam Bulbul Text-to-Speech

## Development

* Git
* GitHub
* VS Code
* Python virtual environment
* npm

---

# 📂 Project Structure

```text
VaaniSetu-AI/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── ...
│   │
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── server.py
│   ├── services/
│   ├── utils/
│   └── ...
│
├── scratch/
│   ├── audit_multilingual_all.py
│   ├── test_cross_language_suite.py
│   └── ...
│
├── .gitignore
├── README.md
└── ...
```

> The exact folder structure may evolve as the project develops.

---

# ⚙️ Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/petrisha2005/VaaniSetu-AI.git
cd VaaniSetu-AI
```

---

# 🔐 Environment Variables

Create a `.env` file for the backend.

Example:

```env
SARVAM_API_KEY=your_sarvam_api_key
```

### Important

Never commit your API key to GitHub.

Make sure `.env` is included in `.gitignore`.

---

# 🐍 Backend Setup

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the FastAPI server:

```bash
./.venv/bin/uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

Backend will be available at:

```text
http://127.0.0.1:8000
```

---

# ⚛️ Frontend Setup

Move into the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the URL shown by Vite, usually:

```text
http://localhost:5173
```

---

# 🎙️ Using Voice Input

For browser microphone access:

1. Open the application using `localhost` or HTTPS.
2. Select your preferred language.
3. Click the microphone button.
4. Allow microphone permission when prompted.
5. Speak naturally.
6. Stop recording.
7. The audio is sent to the backend.
8. Saaras converts speech to text.
9. The question is processed against the uploaded document.
10. The answer is returned in the selected language.
11. Bulbul generates the spoken response.

---

# 🧪 Testing

VaaniSetu includes multilingual pipeline testing for the major AI components.

The testing flow includes:

```text
Document
   ↓
Document Intelligence
   ↓
Speech-to-Text
   ↓
Reasoning
   ↓
Text-to-Speech
   ↓
Playable Audio
```

Example:

```bash
./.venv/bin/python scratch/audit_multilingual_all.py
```

Cross-language testing:

```bash
./.venv/bin/python scratch/test_cross_language_suite.py
```

---

# 🌍 Multilingual Testing

The system has been tested across the configured Indian-language pipeline.

Example cross-language scenarios include:

```text
Kannada Document
        +
Tamil Question
        ↓
Tamil Answer
        ↓
Tamil TTS
```

```text
Hindi Document
        +
Kannada Question
        ↓
Kannada Answer
        ↓
Kannada TTS
```

```text
English Document
        +
Tamil Question
        ↓
Tamil Answer
        ↓
Tamil TTS
```

The important principle is:

> **The document language and user's interaction language do not have to be the same.**

---

# 🎯 Example User Journey

### Step 1 — Upload

The user uploads an official notice.

```text
📄 Government Notice.pdf
```

### Step 2 — Understand

VaaniSetu processes the document and extracts useful information.

```text
Document Type:
Official Notice

Important Date:
30 October 2026

Required Action:
Submit response documents
```

### Step 3 — Ask

The user selects Kannada and speaks:

```text
"ಈ ನೋಟಿಸ್‌ನಲ್ಲಿ ನಾನು ಏನು ಮಾಡಬೇಕು?"
```

### Step 4 — Understand

Saaras converts the voice question into text.

### Step 5 — Reason

The AI uses the uploaded document as context.

### Step 6 — Answer

VaaniSetu provides an answer in Kannada.

### Step 7 — Listen

Bulbul converts the answer into Kannada speech.

---

# 🧠 What Makes VaaniSetu Different?

### Traditional document AI

```text
Upload
  ↓
Summarize
  ↓
Read
```

### VaaniSetu

```text
Upload
   ↓
Understand
   ↓
Ask naturally
   ↓
Get grounded answer
   ↓
Listen in your language
   ↓
Act
```

The key difference is **interaction**.

VaaniSetu aims to turn a static document into an interactive multilingual knowledge source.

---

# 🔐 Safety & Responsible AI

VaaniSetu is designed as a **document understanding and information assistance tool**, not as a replacement for a lawyer, government officer, financial advisor, or other qualified professional.

### Safety principles

* Answers should be grounded in the uploaded document.
* The system should avoid inventing information not supported by the document.
* Important claims should be traceable to document content where possible.
* Users should be encouraged to verify critical information.
* The application should clearly communicate that it does not provide professional legal advice.
* Sensitive documents should be handled carefully.
* API keys and credentials must never be exposed in the frontend or repository.

### Disclaimer

> **VaaniSetu AI provides document-based information assistance and is not a substitute for professional legal, financial, governmental, or other expert advice.**

---

# 📈 Potential Impact

VaaniSetu can potentially help:

### 👨‍🌾 Citizens

Understand government notices and public-service documents.

### 🎓 Students

Understand academic and institutional documents.

### 🏪 Small Business Owners

Understand tax, compliance, and business-related documents.

### 👨‍👩‍👧 Families

Understand important official letters and notices.

### 🌏 Indian-language-first Users

Interact with important information without depending entirely on English.

---

# 🚀 Future Scope

## 1. More Indian Languages

Expand support across additional Indian languages and dialects.

---

## 2. Better Document Intelligence

Support more complex documents such as:

* Tables
* Scanned documents
* Multi-column layouts
* Forms
* Handwritten sections
* Multi-page government documents

---

## 3. Personalized Action Plans

Instead of only answering:

> "What does this document say?"

VaaniSetu could provide:

```text
What you need to do
        ↓
Documents required
        ↓
Deadline
        ↓
Where to submit
        ↓
Next step
```

---

## 4. Voice-First Interaction

A future version could become almost completely voice-driven:

```text
Upload
   ↓
Speak
   ↓
Understand
   ↓
Ask
   ↓
Listen
```

---

## 5. Accessibility

Potential support for:

* Elderly users
* Low-literacy users
* Voice-first users
* Users with reading difficulties
* Regional-language-first communities

---

## 6. Government & Public Service Use Cases

Potential applications include:

* Government notices
* Welfare scheme documents
* Property notices
* Tax communications
* Education documents
* Public-service information
* Application instructions

---

# 🏆 Hackathon Context

**HackSprint — Manipal Academy of Higher Education (MAHE), Bengaluru**

### Track

**PS41 — Sarvam API Challenge**

### Project

**VaaniSetu AI**

### Core Idea

> Build a meaningful application using Sarvam's APIs to make information more accessible through Indian-language interaction.

---

# 📌 Project Highlights

```text
🌐 Multilingual
🎙️ Voice-first interaction
📄 Document understanding
🧠 Document-grounded reasoning
🔊 Indian-language speech output
📌 Action-oriented responses
🔍 Source-aware answers
🇮🇳 Built for Indian-language accessibility
```

---

# 🔗 Links

### GitHub

[https://github.com/petrisha2005/VaaniSetu-AI](https://github.com/petrisha2005/VaaniSetu-AI)


---

# 👩‍💻 Team

### VaaniSetu AI

Built for **HackSprint — MAHE Bengaluru**

**Team Members:**

* Petrisha V.


---

# ⭐ Vision

> **Every important document should be understandable — regardless of the language you speak.**

VaaniSetu aims to bridge the gap between **documents and people** by making information conversational, multilingual, and accessible.

### Understand.

### Ask.

### Act.

### In Your Language. 🇮🇳

---

## 📄 License

This project is currently developed as a hackathon project.

Add an appropriate open-source license if the project is released for public use.
