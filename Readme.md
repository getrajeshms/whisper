# 🎙️ Whisper Transcriber

A sleek, local-first audio transcription app built with **Streamlit** and **OpenAI Whisper**.  
Transcribe or translate audio files directly on your machine — no data leaves your system.

---

## 🚀 Features

- 🎧 Supports multiple audio formats (MP3, WAV, MP4, M4A, OGG, FLAC, WEBM)
- 🧠 Powered by OpenAI Whisper (local inference)
- 🌍 Multi-language support (Auto-detect + manual selection)
- 🔄 Transcription + Translation modes
- ⚡ Multiple model sizes (tiny → large)
- 📄 Export transcripts as:
  - `.txt` (plain text)
  - `.srt` (subtitle format with timestamps)
- 🎨 Clean, modern UI with dark theme

---

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/whisper-transcriber.git
cd whisper-transcriber

pip install streamlit openai-whisper