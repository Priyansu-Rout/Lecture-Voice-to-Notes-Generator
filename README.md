# 🎤 Lecture Voice-to-Notes Generator

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-brightgreen)](https://streamlit.io/)

Convert lecture recordings into structured class notes using AI — fully offline-capable and cloud-ready.


## ✨ Features

- 🎧 **Audio Transcription** – Upload MP3, WAV, M4A files
- 🧠 **Smart Note Generation** – Structured class notes with titles, key points, and summaries
- ❓ **Quiz Generator** – Auto-generate multiple-choice questions
- 📚 **Topic Suggestions** – Discover related academic topics
- 💬 **Chatbot Assistant** – Ask questions about the lecture content
- ⬇️ **Download Center** – Export notes, quizzes, and transcripts
- 🌐 **Cloud Deployment Ready** – Works on Streamlit Community Cloud

## 🧰 Requirements

### Software

- **Python 3.9+**
- [OpenRouter API Key](https://openrouter.ai/keys) (free tier available)
- Pre-downloaded Whisper model (included in repo)

### Hardware

- Minimum: CPU with 4GB RAM
- Recommended: Any modern laptop/desktop

## 🚀 Quickstart

### Option 1: Use Pre-downloaded Model (Fastest)

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/lecture-to-notes.git
   cd lecture-to-notes
   ```
   
## Install dependencies:
```bash
pip install -r requirements.txt

```
## Run the app:

```bash
streamlit run app.py
```
## Option 2: Download Model Locally
If you prefer to download the model yourself:

1. Run once:

```bash
python download_model.py
```

2. Then run:

```bash
streamlit run app.py

```

## 🛡️ License

This project is licensed under the MIT License – see the LICENSE file for details.

## 🤝 Contributing
Contributions welcome! Please read CONTRIBUTING.md  for details.

## 🙌 Author
PRIYANSU ROUT


