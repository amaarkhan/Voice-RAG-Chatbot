#!/usr/bin/env python3
"""
Windows Setup Script for Voice RAG Chatbot
This script ensures all dependencies are properly installed on Windows,
including PyAudio which requires special handling.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8 or higher.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_requirements():
    """Install all requirements from requirements.txt"""
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing requirements from requirements.txt"
    )

def install_pyaudio_windows():
    """Install PyAudio specifically for Windows"""
    print("\n🎤 Setting up PyAudio for Windows...")
    
    # Check if PyAudio is already installed
    try:
        import pyaudio
        print("✅ PyAudio is already installed")
        return True
    except ImportError:
        pass
    
    # Try direct pip install first (works with newer Python versions)
    if run_command(f"{sys.executable} -m pip install PyAudio", "Installing PyAudio directly"):
        return True
    
    # Fallback to pipwin if direct install fails
    print("📦 Direct PyAudio installation failed, trying pipwin...")
    
    # Install pipwin first if not available
    try:
        import pipwin
    except ImportError:
        if not run_command(f"{sys.executable} -m pip install pipwin", "Installing pipwin"):
            return False
    
    # Install PyAudio using pipwin command line
    return run_command(
        f"{sys.executable} -m pipwin install pyaudio",
        "Installing PyAudio using pipwin"
    )

def test_voice_system():
    """Test if voice system components are working"""
    print("\n🎙️ Testing voice system components...")
    
    try:
        # Test PyAudio
        import pyaudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        p.terminate()
        print(f"✅ PyAudio working - Found {device_count} audio devices")
        
        # Test speech recognition
        import speech_recognition as sr
        r = sr.Recognizer()
        print("✅ SpeechRecognition imported successfully")
        
        # Test TTS
        import pyttsx3
        engine = pyttsx3.init()
        engine.stop()
        print("✅ pyttsx3 TTS engine working")
        
        # Test Google TTS
        try:
            import gtts
            print("✅ Google TTS (gtts) available")
        except Exception as e:
            print(f"⚠️ Google TTS warning: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice system test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Voice RAG Chatbot - Windows Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Upgrade pip
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip")
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements. Please check the error messages above.")
        return False
    
    # Install PyAudio for Windows
    if not install_pyaudio_windows():
        print("❌ Failed to install PyAudio. Voice features may not work.")
        print("You can try installing manually with: pip install pipwin && pipwin install pyaudio")
        return False
    
    # Test voice system
    if test_voice_system():
        print("\n🎉 Setup completed successfully!")
        print("\nYou can now run the application with:")
        print("streamlit run app.py")
    else:
        print("\n⚠️ Setup completed but voice system may have issues.")
        print("The text-based features should still work.")
        print("\nYou can still run the application with:")
        print("streamlit run app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)
