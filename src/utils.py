"""
Utility functions for the Voice RAG Chatbot
"""

import os
import json
import logging
from pathlib import Path
import streamlit as st

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('voice_rag_chatbot.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def validate_api_key(api_key):
    """
    Validate OpenAI API key format
    
    Args:
        api_key: The API key to validate
        
    Returns:
        bool: True if format appears valid
    """
    if not api_key:
        return False
    
    # Basic format check for OpenAI API keys
    if api_key.startswith('sk-') and len(api_key) > 40:
        return True
    
    return False

def create_sample_documents():
    """Create sample documents for testing"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Sample text document
    sample_text = """
    # Sample Company Information
    
    Welcome to TechCorp, a leading technology company founded in 2020.
    
    ## Our Services
    - Software Development
    - AI/ML Consulting
    - Cloud Solutions
    - Data Analytics
    
    ## Mission Statement
    Our mission is to provide innovative technology solutions that help businesses 
    transform and succeed in the digital age. We believe in the power of artificial 
    intelligence and machine learning to solve complex problems.
    
    ## Contact Information
    - Email: info@techcorp.com
    - Phone: (555) 123-4567
    - Address: 123 Tech Street, Silicon Valley, CA 94000
    
    ## Recent Projects
    1. AI-powered customer service chatbot for retail company
    2. Machine learning model for fraud detection in banking
    3. Cloud migration project for healthcare organization
    4. Data analytics platform for e-commerce business
    
    ## Team
    Our team consists of experienced engineers, data scientists, and consultants
    who are passionate about technology and innovation.
    """
    
    with open(data_dir / "sample_company_info.txt", "w", encoding="utf-8") as f:
        f.write(sample_text)
    
    # Sample FAQ document
    faq_text = """
    # Frequently Asked Questions
    
    ## General Questions
    
    **Q: What is Voice RAG Chatbot?**
    A: Voice RAG Chatbot is an AI-powered assistant that can understand voice input,
    process documents, and provide intelligent responses based on your uploaded content.
    
    **Q: How does it work?**
    A: The system uses speech recognition to convert your voice to text, searches
    through your uploaded documents using advanced AI, and provides spoken responses
    back to you.
    
    **Q: What file formats are supported?**
    A: Currently supported formats include PDF, TXT, and DOCX files.
    
    ## Technical Questions
    
    **Q: Do I need an internet connection?**
    A: Yes, for voice recognition and AI responses. However, text-to-speech can
    work offline if you choose the offline option.
    
    **Q: Is my data secure?**
    A: Your documents are processed locally and stored in a local database.
    Only text queries are sent to OpenAI for generating responses.
    
    **Q: Can I use it without voice features?**
    A: Yes, you can disable voice features and use it as a text-based chatbot.
    
    ## Troubleshooting
    
    **Q: Voice recognition isn't working. What should I do?**
    A: Check your microphone permissions, ensure it's set as the default device,
    and try speaking more clearly. Also check your internet connection.
    
    **Q: The AI responses seem inaccurate. How can I improve them?**
    A: Make sure you've uploaded relevant documents and ask specific questions.
    The quality of responses depends on the content in your knowledge base.
    """
    
    with open(data_dir / "faq.txt", "w", encoding="utf-8") as f:
        f.write(faq_text)
    
    return True

def format_file_size(size_bytes):
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def clean_text(text):
    """
    Clean text for better processing
    
    Args:
        text: Raw text
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove special characters that might interfere
    text = text.replace('\x00', '')
    
    return text.strip()

def save_chat_history(messages, filename="chat_history.json"):
    """
    Save chat history to file
    
    Args:
        messages: List of chat messages
        filename: Output filename
    """
    try:
        # Convert messages to serializable format
        serializable_messages = []
        for msg in messages:
            clean_msg = {
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg.get("timestamp", "")
            }
            serializable_messages.append(clean_msg)
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(serializable_messages, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        st.error(f"Error saving chat history: {e}")
        return False

def load_chat_history(filename="chat_history.json"):
    """
    Load chat history from file
    
    Args:
        filename: Input filename
        
    Returns:
        list: List of chat messages
    """
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error loading chat history: {e}")
        return []

def check_system_requirements():
    """
    Check if system requirements are met
    
    Returns:
        dict: Status of various system components
    """
    requirements = {
        "python_version": True,
        "microphone": False,
        "internet": False,
        "storage": False
    }
    
    # Check Python version
    import sys
    if sys.version_info >= (3, 8):
        requirements["python_version"] = True
    
    # Check if microphone is available
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
        requirements["microphone"] = True
    except:
        requirements["microphone"] = False
    
    # Check internet connection
    try:
        import urllib.request
        urllib.request.urlopen('http://www.google.com', timeout=3)
        requirements["internet"] = True
    except:
        requirements["internet"] = False
    
    # Check storage space (basic check)
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        if free > 100 * 1024 * 1024:  # At least 100MB free
            requirements["storage"] = True
    except:
        requirements["storage"] = False
    
    return requirements

def get_audio_devices():
    """
    Get available audio input devices
    
    Returns:
        list: List of available microphones
    """
    try:
        import speech_recognition as sr
        devices = []
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            devices.append({"index": index, "name": name})
        return devices
    except:
        return []

def create_config_file():
    """Create default configuration file"""
    config = {
        "voice_settings": {
            "timeout": 5,
            "phrase_timeout": 2,
            "energy_threshold": 300,
            "dynamic_energy_threshold": True
        },
        "tts_settings": {
            "rate": 180,
            "volume": 0.9,
            "voice_id": None
        },
        "rag_settings": {
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "similarity_search_k": 3,
            "temperature": 0.7
        },
        "ui_settings": {
            "theme": "light",
            "show_sources": True,
            "auto_scroll": True
        }
    }
    
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    return config

def load_config():
    """Load configuration from file"""
    try:
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                return json.load(f)
        else:
            return create_config_file()
    except:
        return create_config_file()

# Initialize sample documents if data directory doesn't exist
# Commented out to encourage users to upload their own documents
# if not Path("data").exists():
#     create_sample_documents()
