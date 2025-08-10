import os
import tempfile
import streamlit as st
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import pygame
from io import BytesIO
import threading
import time
from pathlib import Path

class VoiceHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
    def setup_tts(self):
        """Configure text-to-speech settings"""
        try:
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to set a female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate and volume
            self.tts_engine.setProperty('rate', 180)
            self.tts_engine.setProperty('volume', 0.9)
        except Exception as e:
            st.warning(f"TTS setup warning: {e}")
    
    def listen_for_speech(self, timeout=5, phrase_timeout=2, continuous=False):
        """
        Listen for speech input from microphone
        
        Args:
            timeout: Maximum time to wait for speech (if None and continuous=False, uses default)
            phrase_timeout: Maximum time to wait for phrase completion
            continuous: If True, listen continuously without timeout
            
        Returns:
            str: Transcribed text or None if failed
        """
        try:
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
            if continuous:
                st.info("🎤 Listening continuously... Speak now!")
                # For continuous listening, use a longer timeout but still manageable
                actual_timeout = 30  # 30 seconds chunks
                actual_phrase_timeout = 10  # Allow longer phrases
            else:
                st.info("🎤 Listening... Speak now!")
                actual_timeout = timeout
                actual_phrase_timeout = phrase_timeout
            
            with self.microphone as source:
                # Listen for audio with appropriate timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=actual_timeout, 
                    phrase_time_limit=actual_phrase_timeout
                )
            
            st.info("🔄 Processing speech...")
            
            # Use Google's speech recognition
            text = self.recognizer.recognize_google(audio)
            return text
            
        except sr.WaitTimeoutError:
            if continuous:
                # For continuous mode, timeout is expected - just return None
                return None
            else:
                st.warning("⏰ No speech detected within timeout period")
                return None
        except sr.UnknownValueError:
            st.warning("🤷 Could not understand the audio")
            return None
        except sr.RequestError as e:
            st.error(f"❌ Speech recognition service error: {e}")
            return None
        except Exception as e:
            st.error(f"❌ Unexpected error during speech recognition: {e}")
            return None
    
    def speak_text_pyttsx3(self, text):
        """
        Convert text to speech using pyttsx3 (offline)
        
        Args:
            text: Text to convert to speech
        """
        try:
            # Run TTS in a separate thread to avoid blocking
            def speak():
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            
            thread = threading.Thread(target=speak)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            st.error(f"❌ Error with pyttsx3 TTS: {e}")
    
    def speak_text_gtts(self, text, language='en'):
        """
        Convert text to speech using Google TTS (online)
        
        Args:
            text: Text to convert to speech
            language: Language code (default: 'en')
        """
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to BytesIO object
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Play audio using pygame
            pygame.mixer.music.load(audio_buffer)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
        except Exception as e:
            st.error(f"❌ Error with Google TTS: {e}")
            # Fallback to pyttsx3
            self.speak_text_pyttsx3(text)
    
    def speak_text(self, text, use_online=True):
        """
        Convert text to speech with fallback options
        
        Args:
            text: Text to convert to speech
            use_online: Whether to use online TTS (Google) or offline (pyttsx3)
        """
        if not text or not text.strip():
            return
            
        # Limit text length for TTS
        if len(text) > 500:
            text = text[:500] + "..."
            
        if use_online:
            self.speak_text_gtts(text)
        else:
            self.speak_text_pyttsx3(text)
    
    def save_audio_file(self, text, filename, language='en'):
        """
        Save text as audio file
        
        Args:
            text: Text to convert
            filename: Output filename
            language: Language code
        """
        try:
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(filename)
            return True
        except Exception as e:
            st.error(f"❌ Error saving audio file: {e}")
            return False
    
    def test_microphone(self):
        """Test if microphone is working"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            return True
        except Exception as e:
            st.error(f"❌ Microphone test failed: {e}")
            return False
