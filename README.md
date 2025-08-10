# Voice RAG Chatbot

A complete Voice-enabled Retrieval-Augmented Generation (RAG) chatbot that allows you to:
- 🎤 **Voice Input**: Speak your questions naturally
- 📚 **Document Processing**: Upload and process PDF, TXT, and DOCX files
- 🤖 **AI Responses**: Get intelligent answers based on your documents
- 🔊 **Voice Output**: Hear responses spoken back to you
- 💬 **Chat Interface**: Intuitive web-based conversation interface

## Features

### 🎯 Core Functionality
- **Speech-to-Text**: Convert voice input to text using Google Speech Recognition
- **RAG System**: Retrieve relevant information from uploaded documents and generate contextual responses
- **Text-to-Speech**: Convert AI responses to speech using Google TTS or offline pyttsx3
- **Multi-format Support**: Process PDF, TXT, and DOCX documents
- **Vector Storage**: Persistent knowledge base using ChromaDB

### 🛠️ Technical Features
- **Streamlit Web Interface**: User-friendly chat interface
- **Google AI Integration**: Powered by Google's Gemini Pro model for intelligent responses
- **HuggingFace Embeddings**: Advanced document similarity search
- **Persistent Storage**: Knowledge base persists between sessions
- **Error Handling**: Robust error handling and fallback mechanisms

## Installation

### Prerequisites
- Python 3.8 or higher
- Google API key
- Microphone (for voice input)
- Speakers/headphones (for voice output)

### Quick Setup (Windows)

**Option 1: Automatic Setup (Recommended for Windows)**
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Voice-RAG-Chatbot
   ```

2. **Run the Windows setup script**:
   ```bash
   python setup_windows.py
   ```
   This will automatically:
   - Install all dependencies from requirements.txt
   - Install PyAudio using pipwin (Windows-specific)
   - Test all voice system components
   - Verify everything is working

3. **Set up your Google API key**:
   - Get your API key from [Google AI Studio](https://aistudio.google.com/)
   - Either:
     - Create a `.env` file: `GOOGLE_API_KEY=your_google_api_key_here`
     - Or enter it directly in the app sidebar when you run it

4. **Start the application**:
   ```bash
   streamlit run app.py
   ```

**Option 2: Manual Setup**
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Voice-RAG-Chatbot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install PyAudio for Windows**:
   ```bash
   pip install pipwin
   pipwin install pyaudio
   ```
   Note: The app will also try to install PyAudio automatically on first run if it's missing.

4. **Set up environment variables** (optional):
   - Copy `.env.example` to `.env`
   - Add your Google API key:
     ```
     GOOGLE_API_KEY=your_google_api_key_here
     ```

### Setup for Other Platforms

**Linux/Mac**:
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3-pyaudio portaudio19-dev

# Install Python dependencies
pip install -r requirements.txt
```

## Usage

### Starting the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Using the Chatbot

1. **Setup**:
   - Enter your Google API key in the sidebar
   - Enable voice input/output if desired

2. **Upload Documents**:
   - Use the file uploader in the sidebar
   - Supported formats: PDF, TXT, DOCX
   - You can upload multiple files at once

3. **Ask Questions**:
   - Type questions in the text input
   - Or click "🎤 Ask with Voice" for voice input
   - The AI will respond based on your uploaded documents

4. **Voice Features**:
   - Enable "Voice Input/Output" in the sidebar
   - Choose between online (Google TTS) or offline (pyttsx3) for speech output
   - Adjust voice input timeout as needed

### Example Workflows

#### Document Analysis
1. Upload research papers, reports, or documentation
2. Ask questions like:
   - "What are the main findings in this research?"
   - "Summarize the key points from the uploaded documents"
   - "What does the document say about [specific topic]?"

#### Voice Interaction
1. Enable voice features
2. Click the voice button and speak your question
3. Listen to the AI response
4. Continue the conversation naturally

## Configuration Options

### Voice Settings
- **Enable Voice Input/Output**: Toggle voice features on/off
- **TTS Method**: Choose between online (better quality) or offline (no internet required)
- **Voice Timeout**: Adjust how long to wait for voice input

### Knowledge Base Management
- **Upload Documents**: Add new files to the knowledge base
- **Manual Text Entry**: Add text content directly
- **Clear Knowledge Base**: Remove all documents and start fresh
- **View Statistics**: See how many documents are loaded

## Project Structure

```
Voice-RAG-Chatbot/
├── app.py                 # Main Streamlit application
├── src/
│   ├── voice_handler.py   # Voice input/output handling
│   └── rag_system.py      # RAG implementation
├── data/                  # Sample documents (optional)
├── audio/                 # Audio file storage
├── static/                # Static assets
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
└── README.md             # This file
```

## Technical Details

### Dependencies
- **Streamlit**: Web interface framework
- **OpenAI**: Language model API
- **LangChain**: RAG pipeline framework
- **ChromaDB**: Vector database for document storage
- **SpeechRecognition**: Voice input processing
- **pyttsx3 & gTTS**: Text-to-speech engines
- **PyAudio**: Audio input handling
- **HuggingFace Transformers**: Document embeddings

### RAG Pipeline
1. **Document Loading**: Parse PDF, TXT, DOCX files
2. **Text Splitting**: Chunk documents for optimal retrieval
3. **Embedding**: Convert text chunks to vector embeddings
4. **Storage**: Store embeddings in ChromaDB with metadata
5. **Retrieval**: Find relevant chunks based on user queries
6. **Generation**: Use OpenAI to generate contextual responses

### Voice Processing
1. **Input**: Capture audio from microphone
2. **Recognition**: Convert speech to text using Google API
3. **Processing**: Send text through RAG pipeline
4. **Synthesis**: Convert response to speech
5. **Output**: Play audio response

## Troubleshooting

### Common Issues

**PyAudio Installation Error (Windows)**:
The app should automatically install PyAudio on first run. If it fails:
```bash
pip install pipwin
pipwin install pyaudio
```
Or run the setup script: `python setup_windows.py`

**Voice System Not Working**:
- Run the setup script to test all components: `python setup_windows.py`
- Check microphone permissions in Windows settings
- Ensure microphone is set as default device
- Test microphone with other applications first

**Google API Errors**:
- Verify API key is correct and has proper permissions
- Get your key from [Google AI Studio](https://aistudio.google.com/)
- Check API quota and billing if using paid features
- Ensure internet connection is stable

**Voice Recognition Failing**:
- Speak clearly and at moderate pace
- Reduce background noise
- Increase voice timeout in settings

**Document Processing Errors**:
- Ensure files are not corrupted
- Check file permissions
- Try with smaller files first

### Performance Tips

- **Large Documents**: Break large files into smaller chunks
- **Multiple Documents**: Upload related documents together
- **Voice Quality**: Use a good quality microphone
- **Internet**: Stable connection improves voice recognition
- **Storage**: Clear knowledge base periodically to improve performance

## API Keys and Setup

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Add to your `.env` file

### Optional: HuggingFace Token
For advanced features, you can add a HuggingFace token:
1. Visit [HuggingFace](https://huggingface.co/)
2. Create account and get access token
3. Add to `.env`: `HUGGINGFACE_API_TOKEN=your_token`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Search existing issues on GitHub
3. Create a new issue with detailed information

## Future Enhancements

- [ ] Support for more document formats (Excel, PowerPoint)
- [ ] Multiple language support
- [ ] Custom voice models
- [ ] Advanced retrieval strategies
- [ ] Integration with cloud storage
- [ ] Mobile-responsive design
- [ ] User authentication and document management
- [ ] Real-time collaboration features
