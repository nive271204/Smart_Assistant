import streamlit as st
from groq import Groq
import pyttsx3
import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import numpy as np
import av
import tempfile
import os
import threading
import time

# Initialize Groq client
client = Groq(api_key="USE_YOUR_APIKEY")

# Educational riddles data
riddles = [
    {"question": "I am tall when I am young, and short when I am old. What am I?", "answer": "candle"},
    {"question": "What has keys but no locks, space but no room, you can enter but not go inside?", "answer": "keyboard"},
    {"question": "I have cities, but no houses. I have mountains, but no trees. I have water, but no fish. What am I?", "answer": "map"},
    {"question": "The more you take, the more you leave behind. What am I?", "answer": "footsteps"},
    {"question": "What gets wet while drying?", "answer": "towel"},
    {"question": "I am light as a feather, yet the strongest person can't hold me for much longer than a minute. What am I?", "answer": "breath"},
    {"question": "What has one eye but cannot see?", "answer": "needle"},
    {"question": "I am always hungry and will die if not fed, but whatever I touch will soon turn red. What am I?", "answer": "fire"},
    {"question": "What comes once in a minute, twice in a moment, but never in a thousand years?", "answer": "m"},
    {"question": "I have a head and a tail, but no body. What am I?", "answer": "coin"}
]

# Initialize session state for riddle game
if 'current_riddle_index' not in st.session_state:
    st.session_state.current_riddle_index = 0
if 'riddle_answered' not in st.session_state:
    st.session_state.riddle_answered = False
if 'show_result' not in st.session_state:
    st.session_state.show_result = False
if 'answer_submitted' not in st.session_state:
    st.session_state.answer_submitted = False
if 'correct_answer' not in st.session_state:
    st.session_state.correct_answer = ""
if 'waiting_for_response' not in st.session_state:
    st.session_state.waiting_for_response = False
if 'user_acknowledged' not in st.session_state:
    st.session_state.user_acknowledged = False

# Text-to-speech with better control
def speak(text):
    try:
        engine = pyttsx3.init()
        # Set speech rate (slower for better understanding)
        engine.setProperty('rate', 150)
        # Set volume
        engine.setProperty('volume', 0.9)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        st.error(f"Text-to-speech error: {e}")
    finally:
        try:
            engine.stop()
        except:
            pass

# Simple voice interaction - one question, one answer
def simple_voice_interaction():
    # Initial greeting
    greeting = "Hello! I'm your Smart Learning Assistant. How can I help you today? Please ask me your question."
    st.info("🤖 Assistant: " + greeting)
    speak(greeting)
    
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening for your question...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=30, phrase_time_limit=20)
        
        st.info("🔄 Processing your speech...")
        text = recognizer.recognize_google(audio)
        
        if text and len(text.strip()) > 2:
            st.success(f"✅ You asked: {text}")
            
            # Get AI response
            st.info("🤖 Getting AI answer...")
            response = ask_ai(text)
            
            # Display response
            st.text_area("📝 AI Response:", response, height=200, key=f"response_{time.time()}")
            
            # Speak the response
            st.info("🔊 Speaking the answer...")
            speak(response)
            
            # End message
            st.success("✅ Answer completed! Session ended.")
            
        else:
            prompt = "I didn't catch that clearly. Please refresh the page to try again."
            st.warning("⚠ " + prompt)
            speak(prompt)
            
    except sr.UnknownValueError:
        prompt = "I couldn't understand that. Please refresh the page to try again."
        st.warning("⚠ " + prompt)
        speak(prompt)
    except sr.RequestError as e:
        st.error(f"Network error during recognition: {e}")
        speak("I'm having trouble with my speech recognition. Please refresh the page to try again.")
    except sr.WaitTimeoutError:
        prompt = "I didn't hear anything. Please refresh the page to try again."
        st.info("⏳ " + prompt)
        speak(prompt)
    except Exception as e:
        st.error(f"Error: {e}")
        speak("I encountered an error. Please refresh the page to try again.")

# Single voice interaction (alternative)
def single_voice_interaction():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... Speak your question now!")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=15, phrase_time_limit=20)
        
        st.info("🔄 Processing your speech...")
        text = recognizer.recognize_google(audio)
        
        if text and len(text.strip()) > 2:
            st.success(f"✅ You asked: {text}")
            
            # Get AI response
            st.info("🤖 Getting AI answer...")
            response = ask_ai(text)
            
            # Display response
            st.text_area("📝 AI Response:", response, height=200, key=f"response_{time.time()}")
            
            # Speak the response
            st.info("🔊 Speaking the answer...")
            speak(response)
            st.success("✅ Answer completed!")
            
            return True
        else:
            return False
            
    except sr.UnknownValueError:
        st.warning("⚠ Could not understand the audio. Please speak clearly.")
        speak("I couldn't understand that. Please repeat your question clearly.")
        return False
    except sr.RequestError as e:
        st.error(f"Network error during recognition: {e}")
        return False
    except sr.WaitTimeoutError:
        st.warning("⏳ No speech detected. Please try again.")
        speak("I didn't hear anything. Please ask your question.")
        return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# Voice interaction specifically for riddles
def riddle_voice_interaction(correct_answer):
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening for your answer... Speak now!")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=15, phrase_time_limit=10)
        
        st.info("🔄 Processing your speech...")
        text = recognizer.recognize_google(audio).strip().lower()
        
        if text:
            st.success(f"✅ You answered: {text}")
            
            if text == correct_answer.lower():
                success_msg = "🎉 Correct! Great job!"
                st.success(success_msg)
                speak("Correct! Great job!")
                st.session_state.riddle_answered = True
                st.session_state.show_result = True
                st.session_state.correct_answer = ""
            else:
                error_msg = f"❌ Oops! The correct answer is: {correct_answer}"
                st.error(error_msg)
                speak(f"Oops! The correct answer is {correct_answer}")
                st.session_state.riddle_answered = True
                st.session_state.show_result = True
                st.session_state.correct_answer = correct_answer
            
            return True
        else:
            return False
            
    except sr.UnknownValueError:
        st.warning("⚠ Could not understand the audio. Please speak clearly.")
        speak("I couldn't understand that. Please repeat your answer clearly.")
        return False
    except sr.RequestError as e:
        st.error(f"Network error during recognition: {e}")
        return False
    except sr.WaitTimeoutError:
        st.warning("⏳ No speech detected. Please try again.")
        speak("I didn't hear anything. Please say your answer.")
        return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# Speech recognition from microphone (alternative method)
def recognize_speech_alternative():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... Speak now!")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        
        st.info("🔄 Processing your speech...")
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, could not understand the audio."
    except sr.RequestError as e:
        return f"Network error during recognition: {e}"
    except sr.WaitTimeoutError:
        return "No speech detected. Please try again."
    except Exception as e:
        return f"Error: {e}"

# Improved AudioProcessor for webrtc
class AudioProcessor(AudioProcessorBase):
    def init(self):
        self.audio_frames = []
        self.is_recording = True
        
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        if self.is_recording:
            # Convert audio frame to numpy array
            audio_array = frame.to_ndarray().flatten()
            self.audio_frames.append(audio_array)
        return frame
    
    def get_audio_data(self):
        if self.audio_frames:
            # Concatenate all audio frames
            full_audio = np.concatenate(self.audio_frames)
            return full_audio.astype(np.int16)
        return None
    
    def clear_audio(self):
        self.audio_frames = []

# Ask Groq AI
def ask_ai(prompt):
    try:
        # Add context for educational assistance
        system_prompt = "You are a helpful educational assistant for students. Provide clear, concise, and educational answers. Keep responses under 100 words for speech clarity."
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            model="llama3-70b-8192",
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"I'm sorry, I encountered an error while processing your question. Please try again."

# Process audio data to text
def process_audio_to_text(audio_data):
    try:
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            # Write audio data as WAV file
            import wave
            with wave.open(temp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 2 bytes per sample
                wav_file.setframerate(16000)  # 16kHz sample rate
                wav_file.writeframes(audio_data.tobytes())
            
            temp_filename = temp_file.name
        
        # Recognize speech from file
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_filename) as source:
            audio = recognizer.record(source)
        
        # Clean up temp file
        os.unlink(temp_filename)
        
        # Recognize speech
        text = recognizer.recognize_google(audio)
        return text
        
    except Exception as e:
        return f"Error processing audio: {e}"

# Function to reset riddle game
def reset_riddle_game():
    st.session_state.current_riddle_index = 0
    st.session_state.riddle_answered = False
    st.session_state.show_result = False
    st.session_state.answer_submitted = False
    st.session_state.correct_answer = ""
    st.session_state.waiting_for_response = False
    st.session_state.user_acknowledged = False

# Function to go to next riddle
def next_riddle():
    # Clean up current riddle's options from session state
    if f'options_{st.session_state.current_riddle_index}' in st.session_state:
        del st.session_state[f'options_{st.session_state.current_riddle_index}']
    
    st.session_state.current_riddle_index = (st.session_state.current_riddle_index + 1) % len(riddles)
    st.session_state.riddle_answered = False
    st.session_state.show_result = False
    st.session_state.answer_submitted = False
    st.session_state.correct_answer = ""
    st.session_state.waiting_for_response = False
    st.session_state.user_acknowledged = False

# Streamlit UI
st.set_page_config(page_title="Smart Learning Assistant", layout="centered")
st.title("🎓 Smart Learning Assistant for Disabled Students")

choice = st.radio("Choose your accessibility support:", 
                 ["Visual Impairment", "Hearing Impairment", "Cognitive Impairment", "Educational Riddle"])

if choice == "Visual Impairment":
    st.subheader("🎤 Voice Learning Assistant")
    
    # Automatically start voice interaction without any buttons
    st.info("🔊 Voice Mode Activated - Ask one question and get one answer!")
    
    # Automatically start the simple voice interaction
    simple_voice_interaction()

elif choice == "Hearing Impairment":
    st.subheader("📝 Type your question")
    question = st.text_input("Ask your question here:")
    if st.button("Get Answer"):
        if question:
            with st.spinner("Getting AI response..."):
                answer = ask_ai(question)
            st.text_area("AI Response", answer, height=200)
        else:
            st.warning("Please enter a question first.")

elif choice == "Cognitive Impairment":
    st.subheader("🧠 Simplify Content")
    long_text = st.text_area("Paste content to summarize:", height=150)
    if st.button("Summarize"):
        if long_text:
            with st.spinner("Creating simple summary..."):
                summary = ask_ai(f"Summarize the following in simple terms for easy understanding:\n\n{long_text}")
            st.text_area("Simplified Summary", summary, height=300)
        else:
            st.warning("Please enter content to summarize first.")

elif choice == "Educational Riddle":
    st.subheader("🧩 Educational Riddle Time!")
    
    # Get current riddle
    current_riddle = riddles[st.session_state.current_riddle_index]
    
    # Display riddle progress
    st.info(f"Riddle {st.session_state.current_riddle_index + 1} of {len(riddles)}")
    
    riddle_mode = st.selectbox("Select your accessibility mode:", 
                               ["Visual Impairment", "Hearing Impairment", "Cognitive Impairment"])
    
    if riddle_mode == "Visual Impairment":
        st.info("🔊 Riddle will be automatically spoken to you. Answer using your voice.")
        
        # Automatically speak riddle and wait for voice response
        if not st.session_state.waiting_for_response:
            st.info("🤖 Riddle: " + current_riddle["question"])
            speak("Here's your riddle. " + current_riddle["question"])
            st.session_state.waiting_for_response = True
        
        # Wait for voice response
        st.info("🎤 Listening for your answer... Please speak now!")
        
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=30, phrase_time_limit=15)
            
            st.info("🔄 Processing your speech...")
            user_voice_answer = recognizer.recognize_google(audio).strip().lower()
            
            if user_voice_answer:
                st.success(f"✅ You answered: {user_voice_answer}")
                
                if user_voice_answer == current_riddle["answer"].lower():
                    success_msg = "🎉 Correct! Great job!"
                    st.success(success_msg)
                    speak("Correct! Great job! Moving to next riddle.")
                    time.sleep(2)
                    next_riddle()
                    st.rerun()
                else:
                    error_msg = f"❌ Wrong answer! The correct answer is: {current_riddle['answer']}"
                    st.error(error_msg)
                    speak(f"Wrong answer! The correct answer is {current_riddle['answer']}. Moving to next riddle.")
                    time.sleep(3)
                    next_riddle()
                    st.rerun()
            
        except sr.UnknownValueError:
            st.warning("⚠ Could not understand your answer. Moving to next riddle.")
            speak("I couldn't understand that. Moving to next riddle.")
            time.sleep(2)
            next_riddle()
            st.rerun()
        except sr.RequestError as e:
            st.error(f"Network error: {e}")
        except sr.WaitTimeoutError:
            st.warning("⏳ No answer heard. Moving to next riddle.")
            speak("I didn't hear an answer. Moving to next riddle.")
            time.sleep(2)
            next_riddle()
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
            
    elif riddle_mode == "Hearing Impairment":
        st.info("📝 Read the riddle and type your answer below.")
        st.markdown(f"🧠 *Riddle:* {current_riddle['question']}")
        
        # Show result if answered
        if st.session_state.riddle_answered:
            if st.session_state.show_result:
                if st.session_state.correct_answer == "":
                    st.success("🎉 Correct Answer!")
                else:
                    st.error(f"❌ Wrong! The correct answer is: {st.session_state.correct_answer}")
                
                # Button to continue to next riddle
                if st.button("Next Riddle ➡"):
                    next_riddle()
                    st.rerun()
        else:
            user_answer = st.text_input("Your answer:", key=f"answer_{st.session_state.current_riddle_index}")
            
            if st.button("Submit Answer"):
                if user_answer.strip():
                    if user_answer.strip().lower() == current_riddle["answer"].lower():
                        st.success("🎉 Correct Answer!")
                        st.session_state.riddle_answered = True
                        st.session_state.show_result = True
                        st.session_state.correct_answer = ""
                    else:
                        st.error(f"❌ Wrong! The correct answer is: {current_riddle['answer']}")
                        st.session_state.riddle_answered = True
                        st.session_state.show_result = True
                        st.session_state.correct_answer = current_riddle['answer']
                    
                    st.rerun()
                else:
                    st.warning("Please enter an answer first!")
                
    elif riddle_mode == "Cognitive Impairment":
        st.info("🧠 Read and choose the correct answer (easy format).")
        st.markdown(f"🧩 *Riddle:* {current_riddle['question']}")
        
        # Initialize options in session state to prevent reshuffling
        if f'options_{st.session_state.current_riddle_index}' not in st.session_state:
            import random
            options = [current_riddle["answer"], "car", "book", "phone"]
            random.shuffle(options)
            st.session_state[f'options_{st.session_state.current_riddle_index}'] = options
        
        # Get the stored options
        options = st.session_state[f'options_{st.session_state.current_riddle_index}']
        
        # Show result if answered but wait for user acknowledgment
        if st.session_state.riddle_answered and st.session_state.show_result:
            if st.session_state.correct_answer == "":
                st.success("🎉 Correct! Great job!")
            else:
                st.error(f"❌ Wrong! The correct answer is: {st.session_state.correct_answer}")
            
            # Wait for user to acknowledge the result before showing next button
            if not st.session_state.user_acknowledged:
                st.info("💡 Please take a moment to understand the answer.")
                if st.button("I Understand, Continue ✅"):
                    st.session_state.user_acknowledged = True
                    st.rerun()
            else:
                # Only show next riddle button after user acknowledges
                if st.button("Next Riddle ➡"):
                    next_riddle()
                    st.rerun()
        else:
            # Show options only if not answered yet
            user_choice = st.radio("Choose your answer:", options, key=f"choice_{st.session_state.current_riddle_index}")
            
            if st.button("Submit Answer"):
                if user_choice == current_riddle["answer"]:
                    st.session_state.riddle_answered = True
                    st.session_state.show_result = True
                    st.session_state.correct_answer = ""
                else:
                    st.session_state.riddle_answered = True
                    st.session_state.show_result = True
                    st.session_state.correct_answer = current_riddle['answer']
                
                st.rerun()