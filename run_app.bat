@echo off
echo Starting Voice RAG Chatbot...
echo.
cd /d "%~dp0"
.venv\Scripts\streamlit.exe run app.py
pause
