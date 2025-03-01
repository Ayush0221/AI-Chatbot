
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
from flask_socketio import SocketIO

# Initialize Flask app
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure Gemini AI API
genai.configure(api_key="AIzaSyBkhF9_HJhrFgOIHKQwEJPXjK6mYg-Yxa4")  # Replace with your actual API key

def generate_response(query):
    """Generate a response using Gemini AI."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(query)
        return response.text if response else "I'm not sure how to respond."
    except Exception as e:
        return f"Error: {e}"

# Speech Recognition
def listen():
    """Convert speech to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "I couldn't understand that."
        except sr.RequestError:
            return "Speech recognition service is unavailable."
        except Exception as e:
            return f"Error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/listen', methods=['GET'])
def listen_route():
    """API to handle speech recognition."""
    transcription = listen()
    return jsonify({"transcription": transcription})

@socketio.on('message')
def handle_message(data):
    """Handle incoming WebSocket messages."""
    if isinstance(data, dict) and "data" in data:
        user_input = data["data"]
    else:
        user_input = str(data)  # Ensure string format

    response = generate_response(user_input)
    
    # Emit response as JSON
    socketio.emit("message", {"response": response})

if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=8888, allow_unsafe_werkzeug=True)