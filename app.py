from flask import Flask, request, jsonify, render_template
import json
import requests
import os
from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO
from NetHyTech_Pyttsx3_Speak import speak

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Constants
API_URL = "https://pi.ai/api/chat"
VOICE_API_URL = "https://pi.ai/api/chat/voice"
HEADERS_TEMPLATE = {
    "Accept": "text/event-stream",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Content-Type": "application/json",
    "Dnt": "1",
    "Origin": "https://pi.ai",
    "Priority": "u=1, i",
    "Referer": "https://pi.ai/talk",
    "Sec-Ch-Ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "X-Api-Version": "3"
}

session_id = os.getenv("HOSTSESSION")
conversation_id = os.getenv("conv_id")

def get_new_session_cookie():
    response = requests.get("https://pi.ai")
    return list(response.cookies)[0].value if response.cookies else None

def generate_response(user_query, session_cookie="MINE"):
    headers = HEADERS_TEMPLATE.copy()
    headers["Cookie"] = f"__Host-session={session_id}; __cf_bm={session_cookie}"
    
    payload = {
        "text": user_query,
        "conversation": conversation_id
    }

    with requests.Session() as session:
        response = session.post(API_URL, json=payload, headers=headers, stream=True)
        
        if response.status_code in (401, 403):
            new_session_cookie = get_new_session_cookie()
            return generate_response(user_query, new_session_cookie)

        complete_response = {"text": "", "audio": None}
        
        if response.status_code == 200:
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    try:
                        json_data = json.loads(line.lstrip("data:"))
                        content = json_data.get("text", "")
                        with_emoji = content.encode("latin1").decode("utf-8")
                        complete_response["text"] += with_emoji
                        
                        audio_data = json_data.get("audio")
                        if audio_data:
                            complete_response["audio"] = audio_data
                    except json.JSONDecodeError:
                        continue

    return complete_response

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/api/chat', methods=['POST'])
# def chat():
#     user_input = request.json.get('query')
#     response = generate_response(user_input)
#     text_response = response["text"]
#     return jsonify({"response": text_response})

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.json.get('query')
    response = generate_response(user_input)
    text_response = response["text"]
    audio_response = response["audio"]
    return jsonify({"response": text_response, "audio": audio_response})

if __name__ == "__main__":
    app.run(debug=True)
