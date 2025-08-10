import streamlit as st
import os
import time
from dotenv import load_dotenv
import sys
from pathlib import Path

# Windows PyAudio installation check
def ensure_pyaudio_installed():
    """Automatically install PyAudio on Windows if not available"""
    try:
        import pyaudio
        return True
    except ImportError:
        try:
            st.info("🔧 Installing PyAudio for Windows... This may take a moment.")
            # Try direct pip install first (works with newer Python versions)
            import subprocess
            import sys
            result = subprocess.run([sys.executable, "-m", "pip", "install", "PyAudio"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                import pyaudio
                st.success("✅ PyAudio installed successfully!")
                return True
            else:
                # Fallback to pipwin if available
                try:
                    import pipwin
                    # Use the command line interface since the module API changed
                    result = subprocess.run([sys.executable, "-m", "pipwin", "install", "pyaudio"], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        import pyaudio
                        st.success("✅ PyAudio installed successfully using pipwin!")
                        return True
                except:
                    pass
                
        except Exception as e:
            st.error(f"❌ Failed to install PyAudio: {e}")
            st.error("Please install PyAudio manually:")
            st.code("pip install PyAudio")
            st.info("If that fails, try: pip install pipwin && pipwin install pyaudio")
            return False

# Ensure PyAudio is available before proceeding
if not ensure_pyaudio_installed():
    st.stop()

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from voice_handler import VoiceHandler
from rag_system import RAGSystem

# Load environment variables
load_dotenv()

def init_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'voice_handler' not in st.session_state:
        st.session_state.voice_handler = None
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'voice_enabled' not in st.session_state:
        st.session_state.voice_enabled = False
    if 'listening' not in st.session_state:
        st.session_state.listening = False

def setup_page():
    """Configure Streamlit page"""
    st.set_page_config(
        page_title="🎤 Voice RAG Chatbot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎤 Voice RAG Chatbot")
    st.markdown("*Upload documents and ask questions - with voice or text!*")

def setup_sidebar():
    """Setup sidebar with configuration options"""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Google API Key
        google_key = st.text_input(
            "Google API Key",
            type="password",
            value=os.getenv("GOOGLE_API_KEY", ""),
            help="Enter your Google AI Studio API key to enable AI responses"
        )
        
        # Voice settings
        st.subheader("🎵 Voice Settings")
        use_voice = st.checkbox("Enable Voice Input/Output", value=False)
        
        if use_voice:
            tts_method = st.selectbox(
                "Text-to-Speech Method",
                ["Online (Google TTS)", "Offline (pyttsx3)"],
                help="Online TTS has better quality but requires internet"
            )
            
            voice_timeout = st.slider(
                "Voice Input Timeout (seconds)",
                min_value=3,
                max_value=15,
                value=5,
                help="Maximum time to wait for voice input"
            )
        else:
            tts_method = "Online (Google TTS)"
            voice_timeout = 5
        
        # Knowledge Base Management
        st.subheader("📚 Document Upload")
        
        # Enhanced file upload with better guidance
        st.info("🔹 **Upload your documents to get started!** The chatbot will answer questions based on your uploaded content.")
        
        # Examples of what to upload
        with st.expander("💡 What can I upload?", expanded=False):
            st.markdown("""
            **Supported File Types:**
            - 📄 **PDF**: Research papers, reports, manuals, books
            - 📝 **TXT**: Plain text documents, notes, transcripts
            - 📋 **DOCX**: Word documents, essays, articles
            
            **Great Use Cases:**
            - 📚 Company documentation and policies
            - 🔬 Research papers and articles  
            - 📖 Educational materials and textbooks
            - 📋 Meeting notes and transcripts
            - 🏢 Business reports and proposals
            - 💼 Legal documents and contracts
            """)
        
        uploaded_files = st.file_uploader(
            "Choose your documents:",
            type=['pdf', 'txt', 'docx'],
            accept_multiple_files=True,
            help="📎 Supported formats: PDF, TXT, DOCX • Multiple files allowed • Max size: 200MB per file"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) selected for upload")
            for file in uploaded_files:
                file_size = len(file.read())
                file.seek(0)  # Reset file pointer
                st.write(f"• {file.name} ({file_size:,} bytes)")
        else:
            st.warning("⚠️ No documents uploaded yet. Please upload documents to enable the chatbot.")
        
        # Manual text input - make it less prominent
        with st.expander("� Or Add Text Manually", expanded=False):
            manual_text = st.text_area(
                "Enter text content",
                height=100,
                placeholder="Paste your text content here..."
            )
            doc_name = st.text_input(
                "Document Name",
                value="Manual Entry",
                help="Name for this text document"
            )
            if st.button("Add Text to Knowledge Base"):
                if manual_text.strip() and st.session_state.rag_system:
                    st.session_state.rag_system.add_text_document(manual_text, doc_name)
                    st.success("✅ Text added to knowledge base!")
        
        # Knowledge base stats
        if st.session_state.rag_system:
            stats = st.session_state.rag_system.get_knowledge_base_stats()
            st.metric("Documents in KB", stats["total_documents"])
            
            if stats["sources"]:
                st.write("**Sources:**")
                for source in stats["sources"]:
                    st.write(f"• {source}")
        
        # Clear knowledge base
        if st.button("🗑️ Clear Knowledge Base", type="secondary"):
            if st.session_state.rag_system:
                st.session_state.rag_system.clear_knowledge_base()
                st.session_state.processed_files = []  # Reset processed files
                st.success("🗑️ Knowledge base cleared!")
        
        return google_key, use_voice, tts_method, voice_timeout, uploaded_files

def initialize_systems(google_key, use_voice):
    """Initialize voice handler and RAG system"""
    # Initialize RAG system
    if google_key and not st.session_state.rag_system:
        try:
            with st.spinner("🔄 Initializing RAG system..."):
                st.session_state.rag_system = RAGSystem(google_key)
        except Exception as e:
            st.error(f"❌ Failed to initialize RAG system: {e}")
            return False
    
    # Initialize voice handler
    if use_voice and not st.session_state.voice_handler:
        try:
            with st.spinner("🔄 Initializing voice system..."):
                st.session_state.voice_handler = VoiceHandler()
                # Test microphone
                if st.session_state.voice_handler.test_microphone():
                    st.session_state.voice_enabled = True
                    st.success("✅ Voice system initialized successfully")
                else:
                    st.warning("⚠️ Microphone test failed. Voice input may not work.")
        except Exception as e:
            st.error(f"❌ Failed to initialize voice system: {e}")
            st.session_state.voice_enabled = False
    
    return True

def process_uploaded_files(uploaded_files):
    """Process newly uploaded files"""
    if uploaded_files and st.session_state.rag_system:
        # Only process if we haven't processed these files before
        current_files = [f.name for f in uploaded_files]
        if 'processed_files' not in st.session_state:
            st.session_state.processed_files = []
        
        # Check if these are new files
        if current_files != st.session_state.processed_files:
            with st.spinner("📄 Processing uploaded files..."):
                processed = st.session_state.rag_system.process_documents(uploaded_files)
                if processed > 0:
                    st.session_state.processed_files = current_files
                    st.success(f"✅ Successfully processed {processed} documents!")

def handle_voice_input():
    """Handle continuous voice input"""
    if st.session_state.voice_handler and st.session_state.voice_enabled:
        try:
            # Listen for speech with continuous mode
            text = st.session_state.voice_handler.listen_for_speech(continuous=True)
            if text and text.strip():
                st.success(f"✅ Heard: '{text}'")
                return text
            else:
                return None
        except Exception as e:
            st.error(f"❌ Voice input error: {e}")
            st.session_state.listening = False
            return None
    else:
        st.error("❌ Voice system not available")
        return None

def handle_query(question, tts_method):
    """Process user query and return response"""
    if not question.strip():
        st.warning("⚠️ Please enter a question.")
        return
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Get response from RAG system
    if st.session_state.rag_system:
        try:
            with st.spinner("🤔 Thinking..."):
                response = st.session_state.rag_system.query_knowledge_base(question)
                answer = response["answer"]
                sources = response.get("source_documents", [])
            
            # Add assistant response to chat
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer,
                "sources": sources
            })
            
            # Text-to-speech for response
            if st.session_state.voice_handler and st.session_state.voice_enabled:
                use_online = tts_method == "Online (Google TTS)"
                try:
                    st.session_state.voice_handler.speak_text(answer, use_online=use_online)
                except Exception as e:
                    st.warning(f"⚠️ TTS error: {e}")
        except Exception as e:
            st.error(f"❌ Error processing query: {e}")
            # Add error message to chat
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"Sorry, I encountered an error while processing your question: {e}",
                "sources": []
            })
    else:
        st.error("❌ RAG system not initialized. Please provide Google API key.")

def display_chat():
    """Display chat messages"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Show sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                sources = message["sources"]
                if sources:
                    with st.expander(f"📚 Sources ({len(sources)})"):
                        for i, doc in enumerate(sources, 1):
                            st.write(f"**Source {i}:** {doc.metadata.get('source', 'Unknown')}")
                            st.write(f"*Content:* {doc.page_content[:200]}...")

def main():
    """Main application function"""
    init_session_state()
    setup_page()
    
    # Sidebar configuration
    google_key, use_voice, tts_method, voice_timeout, uploaded_files = setup_sidebar()
    
    # Initialize systems
    if not initialize_systems(google_key, use_voice):
        st.stop()
    
    # Process uploaded files
    process_uploaded_files(uploaded_files)
    
    # Main interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat interface
        st.subheader("💬 Chat")
        
        # Display chat messages
        display_chat()
        
        # Simple instruction if no messages
        if not st.session_state.messages:
            st.info("📝 Upload documents in the sidebar, then ask questions here!")
        
        # Input section
        st.subheader("🎯 Ask a Question")
        
        # Check if documents are loaded
        has_docs = False
        if st.session_state.rag_system:
            stats = st.session_state.rag_system.get_knowledge_base_stats()
            has_docs = stats["total_documents"] > 0
        
        # Simple form for questions
        with st.form("ask_question", clear_on_submit=True):
            question = st.text_input(
                "Your question:",
                placeholder="What would you like to know?" if has_docs else "Upload documents first",
                disabled=not has_docs
            )
            ask_button = st.form_submit_button("Ask", disabled=not has_docs)
            
            if ask_button and question and has_docs:
                handle_query(question, tts_method)
        
        # Voice button (if enabled)
        if use_voice and st.session_state.voice_enabled and has_docs:
            # Toggle voice listening state
            if st.session_state.listening:
                if st.button("🔴 Stop Listening", type="primary"):
                    st.session_state.listening = False
                    st.rerun()
                else:
                    # Handle continuous voice input while listening
                    st.info("🎤 Listening continuously... Speak your question or click 'Stop Listening'")
                    voice_q = handle_voice_input()
                    if voice_q and voice_q.strip():
                        st.session_state.listening = False
                        handle_query(voice_q, tts_method)
                        st.rerun()
                    else:
                        # Keep listening - auto-refresh to continue the loop
                        time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                        st.rerun()
            else:
                if st.button("🎤 Start Voice Question"):
                    st.session_state.listening = True
                    st.rerun()
    
    with col2:
        # Simple status
        st.subheader("📊 Status")
        
        if google_key:
            st.success("✅ API Key Ready")
        else:
            st.error("❌ Need API Key")
        
        if uploaded_files and st.session_state.rag_system:
            stats = st.session_state.rag_system.get_knowledge_base_stats()
            if stats["total_documents"] > 0:
                st.success(f"✅ {stats['total_documents']} Documents Processed")
            else:
                st.info(f"📁 {len(uploaded_files)} Documents Ready")
        else:
            st.warning("📁 No Documents")
        
        if use_voice and st.session_state.voice_enabled:
            st.success("🎤 Voice Ready")
        elif use_voice:
            st.warning("🎤 Voice Issues")
        
        # Simple instructions
        st.subheader("📝 How to Use")
        st.markdown("""
        1. **🔑** Enter Google API key
        2. **📁** Upload documents 
        3. **�** Ask questions
        4. **🎤** Use voice (optional)
        """)
        
        if not google_key:
            st.info("Get API key from [Google AI Studio](https://aistudio.google.com/)")

if __name__ == "__main__":
    main()
