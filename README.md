# SAHAY AI: A Neural Telephony Bridge for Digital Inclusion

SAHAY AI is an end-to-end voice-intelligence platform that leverages the global telephone network to provide AI access to marginalized communities. By bridging the Public Switched Telephone Network (PSTN) with a modern neural stack, SAHAY AI enables users to interact with Large Language Models (LLMs) using any standard telephone - no internet, smartphone, or literacy required.

## The Problem: The "Digital Intelligence" Divide

Despite the rapid evolution of Artificial Intelligence, a significant portion of the global population remains excluded from its benefits. This exclusion is driven by three primary barriers:

* Hardware & Infrastructure Poverty: Advanced AI interfaces (apps/web) require smartphones and high-speed data plans, which are inaccessible to millions of "feature phone" or "button phone" users.

* The Literacy Barrier: Traditional AI interaction is text-centric (chatbots). This creates an insurmountable wall for non-literate individuals or those who find typing in regional scripts difficult.

* Linguistic Centralization: Most state-of-the-art AI is optimized for English, offering poor performance or zero support for regional dialects like Malayalam or rural Hindi.

## The Solution: Voice-as-an-Interface

SAHAY AI transforms a humble phone call into a high-speed portal for generative reasoning. It meets users exactly where they are on a standard voice call and handles all the complex neural heavy lifting on the backend.

### What SAHAY AI Accomplishes:

* Accessibility: Any user with a basic ₹1,000 phone can access the same intelligence as someone with a flagship smartphone.

* Vernacular First: Native support for Malayalam and Hindi, allowing users to speak naturally rather than struggling with a second language.

* Simplification Engine: It doesn't just provide answers; it distills complex information into simplified, digestible verbal summaries (maximum 500 characters) suited for spoken-word delivery.

## Technical Architecture & Neural Pipeline

The system is built as a synchronous Neural Orchestrator that manages the lifecycle of a voice signal across four distinct stages:

### 1. Secure PSTN Ingestion

* The Entry Point: The system utilizes Twilio as a carrier-grade gateway. When a call arrives, the backend generates TwiML (Twilio Markup Language) instructions to greet the user and trigger a cloud-based recording of their query.

* Authenticated Media Fetch: To maintain security, the backend performs an HTTP Basic Auth binary download. This ensures that the system securely retrieves the recording from Twilio’s cloud storage directly into the local processing buffer.

### 2. Neural Signal Conditioning (The DSP Engine)

* The Challenge: Telephony audio is "narrow-band" (8kHz), which is too low-quality for modern neural engines to transcribe accurately.

* The Fix: SAHAY AI implements a custom Digital Signal Processing (DSP) layer using FFmpeg and pydub. This engine transcodes the raw 8kHz stream into an AI-optimized 16kHz/Mono/Linear16 WAV format in real-time. This conditioning step is critical to preventing the "Unsupported Format" errors common in AI-telephony integrations.

### 3. The Multi-Model Intelligence Core

* Acoustic Modeling (STT): The system utilizes Sarvam AI (Saaras:v3) for regional language Speech-to-Text. This model is specifically fine-tuned for Indian accents and dialects, ensuring high transcription accuracy even over noisy phone lines.

* Generative Reasoning (LLM): Google Gemini 2.5 Flash acts as the system's "brain". A specialized reasoning.py module performs Dynamic Model Discovery, automatically identifying and selecting the most capable model available for the API key to ensure zero-latency response generation.

### 4. Neural Synthesis & ngrok Tunneling

* Neural TTS: Sarvam AI (Bulbul:v2) performs the final synthesis, converting the AI’s text back into a natural, human-like voice response.

* ngrok Protocol Bypass: Since Twilio must fetch the final audio file from a local server, we implemented custom headers (ngrok-skip-browser-warning) in the Flask static file server. This bypasses the ngrok "interception" page, allowing the carrier to immediately play the audio to the caller.

## Example Call Flow

1. User dials the SAHAY AI number using any phone.
2. The system records the user's question.
3. Speech is transcribed using Sarvam AI.
4. Gemini processes and simplifies the response.
5. The response is converted to speech.
6. The caller hears the AI-generated answer instantly.

## System Architecture

```bash
User Phone Call  
      │  
      ▼  
   Twilio PSTN Gateway  
      │  
      ▼  
   Flask Backend  
      │  
      ├── FFmpeg DSP Conditioning  
      │  
      ├── Sarvam STT  
      │  
      ├── Gemini 2.5 Flash  
      │  
      └── Sarvam TTS  
      │  
      ▼  
  Voice Response Back to Caller  
```

## Real World Use Cases

- Farmers asking crop price updates  
- Rural citizens asking government scheme information  
- Health guidance in local languages  
- Education assistance for non-literate users  
- Disaster information access without internet  

## System Components & Files

* app.py: The central engine managing the Flask server, security protocols, and the FFmpeg-powered audio conditioning layer.

* core/stt_engine.py: Handles binary file transmission to Sarvam AI for multilingual transcription.

* core/reasoning.py: Manages the prompt engineering and logic simplification via the Gemini API.

* core/tts_engine.py: Decodes base64 neural audio codes into carrier-ready WAV binaries.

* temp_audio/ & static/: Buffers used for the internal processing and external serving of audio assets.

## Performance & Safety Features

* Neural Buffer: Includes a 2-second cloud-sync delay to ensure the system doesn't try to download a file before the telephony carrier has finished writing it.

* Signal Fallback: If the high-fidelity DSP conditioning fails, the system automatically attempts to process the raw audio to maintain call continuity.

* Latency Mitigation: Uses Gemini 2.5 Flash—the fastest model in its class—to minimize the "silence window" while the user is on the line.

## Requirements

- Python 3.10+
- FFmpeg
- Twilio account
- ngrok
- Sarvam AI API key
- Google Gemini API key

## Environment Variables

Create a `.env` file

```bash
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
SARVAM_API_KEY=
GEMINI_API_KEY=
```

## How to Run

* Install FFmpeg (System requirement for audio conditioning).

```bash
pip install -r requirements.txt.
```

* python app.py and start an ngrok tunnel.

* Configure your Twilio Webhook to point to your tunnel URL.

## License

MIT License
