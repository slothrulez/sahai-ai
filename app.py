import os
import time
import requests
from flask import Flask, request, send_file, render_template, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Signal Processing & Telephony
from pydub import AudioSegment  # Requires FFmpeg
from twilio.twiml.voice_response import VoiceResponse

# Neural Pipeline Modules
from core.stt_engine import transcribe_audio
from core.reasoning import simplify_query
from core.tts_engine import synthesize_speech

# Initialize Environment & Credentials
load_dotenv()
app = Flask(__name__)
CORS(app)

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")

# --- SYSTEM INITIALIZATION ---
for folder in ['temp_audio', 'static']:
    if not os.path.exists(folder):
        os.makedirs(folder)

def condition_audio(input_path):
    """Normalizes 8kHz PSTN audio to AI-Standard 16kHz Mono WAV"""
    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        conditioned_path = os.path.join('temp_audio', 'conditioned_telephony.wav')
        audio.export(conditioned_path, format="wav")
        print(f"DEBUG: Signal Conditioned at {conditioned_path}")
        return conditioned_path
    except Exception as e:
        print(f"DSP Error: {e}")
        return input_path

# --- TELEPHONY PATHWAY (TWILIO) ---

@app.route("/voice", methods=['POST'])
def voice_entry():
    response = VoiceResponse()
    response.say("Namaste. Sahay AI mein aapka swagat hai. Kripya apna sawal puche.", language='hi-IN')
    response.record(action="/process-voice", method="POST", maxLength=10)
    return str(response)

@app.route("/process-voice", methods=['POST'])
def telephony_pipeline():
    try:
        audio_url = request.form.get('RecordingUrl')
        if not audio_url:
            return str(VoiceResponse().say("Audio not detected."))

        # 1. THE NEURAL BUFFER: Wait for Cloud Finalization
        time.sleep(2) 
        if not audio_url.endswith(".wav"):
            audio_url += ".wav"

        # 2. SECURE INGESTION
        raw_path = os.path.join('temp_audio', 'raw_telephony_input.wav')
        download_res = requests.get(audio_url, auth=(TWILIO_SID, TWILIO_AUTH), stream=True)
        
        if download_res.status_code == 200:
            with open(raw_path, 'wb') as f:
                f.write(download_res.content)
            print(f"DEBUG: Secure Download successful. Size: {os.path.getsize(raw_path)} bytes")
        else:
            return str(VoiceResponse().say("Cloud authentication failed."))

        # 3. DSP & NEURAL PIPELINE
        clean_path = condition_audio(raw_path)
        user_text = transcribe_audio(clean_path)
        
        if not user_text or "error" in str(user_text).lower():
            res = VoiceResponse()
            res.say("Maaf kijiye, awaaz samajh nahi aayi.", language='hi-IN')
            return str(res)

        simplified_response = simplify_query(user_text)
        raw_out_path = synthesize_speech(simplified_response)
        final_out_path = os.path.join('static', 'telephony_output.wav')
        
        if os.path.exists(raw_out_path):
            os.replace(raw_out_path, final_out_path)

        # 4. RESPONSE SERIALIZATION
        response = VoiceResponse()
        
        # Safety Buffer: Give a small verbal cue while Twilio fetches the file
        response.say("Jawaab suniye.", language='hi-IN')
        
        # !! RE-CHECK YOUR NGROK URL !!
        ngrok_url = "https://felice-tendinous-blakely.ngrok-free.dev" 
        response.play(f"{ngrok_url}/static/telephony_output.wav")
        
        return str(response)

    except Exception as e:
        print(f"System Failure: {e}")
        return str(VoiceResponse().say("System error."))

# --- STATIC ASSET SERVING (NGROK BYPASS) ---

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serves audio binaries and forces ngrok to skip the warning page"""
    try:
        response = send_from_directory('static', filename)
        # CRITICAL: This header prevents the 'Application Error' by bypassing ngrok's UI
        response.headers['ngrok-skip-browser-warning'] = 'true'
        return response
    except Exception as e:
        return str(e), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)