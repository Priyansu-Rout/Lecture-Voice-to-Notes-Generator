# 🎤 Lecture Voice-to-Notes Generator

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-brightgreen)](https://streamlit.io/)
[![License](https://img.shields.io/github/license/yourusername/lecture-to-notes)](LICENSE)

Convert lecture recordings into structured class notes using AI — fully offline or with cloud APIs.

## ✨ Features

- 🎧 Transcribe audio files (MP3, WAV, M4A) using Whisper
- 🧠 Format transcripts into clean class notes using:
  - Local LLM: [Ollama Phi-3](https://ollama.com/library/phi3)
  - Remote API: OpenAI GPT models
- 📥 Downloadable notes in Markdown format
- 💻 Runs locally or connects to the cloud

## 🧰 Requirements

### Software

- **Python 3.9+**
- [FFmpeg](https://ffmpeg.org/download.html) (for MP3/M4A support)
- [Ollama](https://ollama.com/download) (for local Phi-3 usage)

### Hardware

- Minimum: CPU with 4GB RAM
- Recommended: GPU for faster Whisper processing

## 🚀 Quickstart

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/lecture-to-notes.git
cd lecture-to-notes
```

# 2. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```
---
# 3. Install Dependencies
```bash
pip install -r requirements.txt
```
---
# 4. Install FFmpeg
Windows:
Download from https://www.gyan.dev/ffmpeg/builds/
Add `ffmpeg.exe` to system PATH.

#### macOS:
```bash
brew install ffmpeg
```
#### Linux (Ubuntu/Debian):
```bash
sudo apt update && sudo apt install ffmpeg
```
---
# 5. Set Up Ollama (Local Mode Only)
Install Ollama from: https://ollama.com/download

Pull Phi-3 model:
```bash
ollama pull phi3
ollama serve
```

# ▶️ Run the App
```bash
streamlit run app.py
```
Open http://localhost:8501 in your browser.

# 📦 Project Structure
```text
lecture-to-notes/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── LICENSE             # MIT License

```
# 🛡️ License
This project is licensed under the MIT License – see the LICENSE [blocked] file for details.

# 🤝 Contributing
Contributions welcome! Please read CONTRIBUTING.md [blocked] for details on our code of conduct, and the process for submitting pull requests.

# 🙌 Author
PRIYANSU ROUT

[Linkedin](https://www.linkedin.com/in/priyansu-rout-06a40834b/)

