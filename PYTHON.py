
import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
import tkinter as tk
from tkinter import scrolledtext
import threading
import time

# Initialize the Gemini API
genai.configure(api_key="AIzaSyBkhF9_HJhrFgOIHKQwEJPXjK6mYg-Yxa4")

# Text-to-Speech engine setup
engine = pyttsx3.init('nsss')
engine.setProperty('voice', engine.getProperty('voices')[132].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to process audio input
def listen_to_command():
    """Speech to Text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        conversation_area.insert(tk.END, "Listening...\n\n")
        recognizer.pause_threshold = 1
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            query = recognizer.recognize_google(audio, language='en-in').lower()
            conversation_area.insert(tk.END, f"You: {query}\n")
            return query
        except sr.UnknownValueError:
            conversation_area.insert(tk.END, "Chameli: Sorry, I didn't catch that. Please repeat.\n")
            speak("Sorry, I didn't catch that. Please repeat.")
            return "none"
        except sr.RequestError:
            conversation_area.insert(tk.END, "Chameli: Network error. Please check your connection.\n")
            speak("Network error. Please check your connection.")
            return "none"
        except Exception as e:
            conversation_area.insert(tk.END, f"Chameli: Error: {e}\n")
            speak("Sorry, I encountered an error.")
            return "none"

# Function to generate a response using Gemini API
def generate_response(query):
    """Generate a response using Gemini API."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(query, generation_config=genai.GenerationConfig(
            max_output_tokens=75,
            temperature=0.1,
        ))
        return response.text if response.text else "I'm not sure how to respond."
    except Exception as e:
        print(f"Error in AI response: {e}")
        return "Sorry, I encountered an error while processing your request."

# Function to handle conversation (both text and audio)
def handle_conversation():
    """Continuously handle user input and respond."""
    while True:
        if text_input.get() != "":  # If there's text input, handle it
            query = text_input.get().lower()
            text_input.delete(0, tk.END)  # Clear the text box after processing

            if query in ["bye", "goodbye", "exit", "quit"]:
                conversation_area.insert(tk.END, "Chameli: Goodbye! Have a great day!\n")
                speak("Goodbye! Have a great day!")
                break  # Exit the loop cleanly

            response = generate_response(query)
            conversation_area.insert(tk.END, f"Chameli: {response}\n\n")
            conversation_area.see(tk.END)  # Auto-scroll down
            speak(response)
        
        time.sleep(0.1)  # Small delay to allow UI updates and avoid 100% CPU usage

# Start the conversation
def start_conversation():
    """Start the conversation."""
    conversation_area.insert(tk.END, "Hi, I am Chameli. How can I help you?\n\n")
    conversation_area.see(tk.END)
    speak("Hi, I am Chameli. How can I help you?")

    # Start the conversation in a new thread for text input handling
    conversation_thread = threading.Thread(target=handle_conversation, daemon=True)
    conversation_thread.start()

# Function to handle audio input from a button click
def start_audio_input():
    """Start listening to audio input."""
    query = listen_to_command()
    if query != "none":
        response = generate_response(query)
        conversation_area.insert(tk.END, f"Chameli: {response}\n\n")
        conversation_area.see(tk.END)  # Auto-scroll down
        speak(response)

# Set up the GUI
root = tk.Tk()
root.title("C-H-A-M-E-L-I")

# Conversation arSea (display area)
conversation_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20, font=("Arial", 12))
conversation_area.pack(padx=10, pady=10)

# Text input field
text_input = tk.Entry(root, font=("Arial", 12), width=50)
text_input.pack(pady=5)

# Button to submit text input
text_submit_button = tk.Button(root, text="Send Text", font=("Arial", 12), command=start_conversation)
text_submit_button.pack(pady=5)

# Button to trigger audio input
audio_input_button = tk.Button(root, text="Speak to Me", font=("Arial", 12), command=start_audio_input)
audio_input_button.pack(pady=5)

# Run the Tkinter event loop
root.mainloop()