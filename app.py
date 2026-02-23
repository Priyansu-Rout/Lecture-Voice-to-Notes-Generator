# app.py

import streamlit as st
from faster_whisper import WhisperModel
from openai import OpenAI
import os


# --- WHISPER MODEL LOADING ---
@st.cache_resource
def load_whisper():
    model = WhisperModel("base", device="cpu", compute_type="int8")
    return model


def transcribe_audio(model, audio_path):
    """Transcribe audio using Faster-Whisper."""
    try:
        segments, info = model.transcribe(audio_path, language="en")
        transcript = "".join([segment.text for segment in segments])
        return transcript
    except Exception as e:
        st.error(f"⚠️ Transcription failed: {str(e)}")
        return ""


def format_with_phi3(prompt):
    """Format using local Ollama Phi-3 model."""
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='ollama'
    )

    try:
        completion = client.chat.completions.create(
            model="phi3",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant skilled at formatting lecture transcripts "
                        "into structured class notes. Output only the formatted note."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Format the following lecture transcript into well-structured class notes with:\n"
                        "1. A title\n"
                        "2. Key Concepts (as bullet points)\n"
                        "3. Important Points\n"
                        "4. Short Summary\n\n"
                        f"Transcript:\n{prompt}"
                    )
                }
            ],
            temperature=0.5,
            max_tokens=500
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error calling Phi-3 via Ollama:\n{str(e)}"


def format_with_openai(prompt, api_key):
    """Format using OpenAI API."""
    client = OpenAI(api_key=api_key)
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant skilled at formatting lecture transcripts "
                        "into structured class notes. Output only the formatted note."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Format the following lecture transcript into well-structured class notes with:\n"
                        "1. A title\n"
                        "2. Key Concepts (as bullet points)\n"
                        "3. Important Points\n"
                        "4. Short Summary\n\n"
                        f"Transcript:\n{prompt}"
                    )
                }
            ],
            temperature=0.5,
            max_tokens=500
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error calling OpenAI API:\n{str(e)}"


# --- STREAMLIT APP ---
st.set_page_config(page_title="🎤 Lecture Voice-to-Notes Generator", layout="centered")

st.title("🎤 Lecture Voice-to-Notes Generator")
st.markdown("_Uses Faster-Whisper + Ollama/OpenAI for Smart Formatting_")

# --- MODE SELECTION ---
mode = st.radio("Choose Processing Mode:", ("🧠 Local LLM (Ollama Phi-3)", "☁️ OpenAI API"))

whisper_model = load_whisper()

api_key = None
if mode == "☁️ OpenAI API":
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key to continue.")
        st.stop()


# --- AUDIO TAB ---
st.markdown("### 🎧 From Audio File")

uploaded_file = st.file_uploader(
    "📤 Upload your lecture audio (MP3/WAV/M4A):",
    type=["mp3", "wav", "m4a"],
    key="audio_uploader"
)

if uploaded_file is not None:
    if uploaded_file.size == 0:
        st.error("❌ Uploaded file is empty.")
        st.stop()

    ext = uploaded_file.name.split(".")[-1].lower()
    temp_audio_path = f"temp_uploaded_audio.{ext}"

    with open(temp_audio_path, "wb") as f:
        f.write(uploaded_file.read())

    # Validate written file
    file_size = os.path.getsize(temp_audio_path)
    st.write(f"💾 Written file size: {file_size} bytes")
    if file_size == 0:
        st.error("🚨 Failed to save audio file correctly.")
        st.stop()

    st.audio(temp_audio_path)

    if st.button("🔁 Convert Audio to Notes"):
        with st.spinner("Transcribing audio..."):
            transcript = transcribe_audio(whisper_model, temp_audio_path)

        if not transcript:
            st.error("🚫 Transcription returned empty result.")
        else:
            st.subheader("📜 Full Transcript")
            st.text_area("", value=transcript, height=200)

            with st.spinner("Generating structured notes..."):
                if mode == "🧠 Local LLM (Ollama Phi-3)":
                    formatted_note = format_with_phi3(transcript)
                elif mode == "☁️ OpenAI API":
                    formatted_note = format_with_openai(transcript, api_key)

            st.subheader("🧾 Generated Notes")
            st.markdown(formatted_note)

            st.download_button(
                label="📥 Download as Markdown (.md)",
                data=formatted_note,
                file_name="audio_notes.md",
                mime="text/markdown"
            )

        os.remove(temp_audio_path)


# --- TEXT TAB ---
st.markdown("---")
st.markdown("### 📝 From Text Transcript")

user_text = st.text_area("Paste your lecture transcript here:", height=200, key="text_input")

if st.button("📄 Generate Notes from Text"):
    if user_text.strip() == "":
        st.warning("Please enter some text first.")
    else:
        with st.spinner("Generating structured notes from text..."):
            if mode == "🧠 Local LLM (Ollama Phi-3)":
                formatted_note = format_with_phi3(user_text)
            elif mode == "☁️ OpenAI API":
                formatted_note = format_with_openai(user_text, api_key)

        st.subheader("🧾 Generated Notes")
        st.markdown(formatted_note)

        st.download_button(
            label="📥 Download as Markdown (.md)",
            data=formatted_note,
            file_name="text_notes.md",
            mime="text/markdown"
        )
