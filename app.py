# app.py

import streamlit as st
import requests
import os
import shutil
from faster_whisper import WhisperModel
from huggingface_hub import snapshot_download


# --- ENVIRONMENT SETUP ---
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"


# --- DETECT IF RUNNING IN CLOUD ---
def is_deployed():
    return "STREAMLIT_SERVER_HEADLESS" in os.environ


# --- WHISPER MODEL LOADING ---
@st.cache_resource
def load_whisper():
    model_path = "./models/faster-whisper-base"

    # If not found, trigger download
    if not os.path.exists(model_path):
        st.warning("🔄 Model not found. Starting download...")
        try:
            from huggingface_hub import snapshot_download
            import shutil

            snapshot_dir = snapshot_download(
                repo_id="Systran/faster-whisper-base",
                revision="main"
            )
            shutil.copytree(snapshot_dir, model_path)
            st.success("✅ Model downloaded successfully!")
        except Exception as e:
            st.error(f"🚫 Failed to download model: {e}")
            st.stop()

    from faster_whisper import WhisperModel
    model = WhisperModel(model_path, device="cpu", compute_type="int8")
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


# --- OPENROUTER API CALLS ---
def call_openrouter(prompt, api_key, task="format"):
    """Call OpenRouter for various tasks."""
    system_prompts = {
        "format": (
            "You are a helpful assistant skilled at formatting lecture transcripts "
            "into structured class notes. Output only the formatted note."
        ),
        "quiz": (
            "You are a helpful assistant skilled at generating educational quiz questions. "
            "Generate 5 multiple-choice questions with 4 options each and indicate the correct answer."
        ),
        "topics": (
            "You are an expert educator. Given a lecture topic, suggest 5 related academic topics "
            "for deeper learning."
        ),
        "chat": (
            "You are an intelligent assistant helping students understand lectures. "
            "Answer clearly and concisely based on the provided content."
        )
    }

    user_prompts = {
        "format": (
            "Format the following lecture transcript into well-structured class notes with:\n"
            "1. A title\n"
            "2. Key Concepts (as bullet points)\n"
            "3. Important Points\n"
            "4. Short Summary\n\n"
            f"Transcript:\n{prompt}"
        ),
        "quiz": f"Based on this lecture content:\n\n{prompt}",
        "topics": f"Lecture Topic:\n{prompt[:500]}",
        "chat": prompt
    }

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": system_prompts[task]},
                    {"role": "user", "content": user_prompts[task]}
                ],
                "temperature": 0.6,
                "max_tokens": 800 if task == "quiz" else 500
            }
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Error calling OpenRouter API:\n{str(e)}"


# --- VALIDATE OPENROUTER KEY ---
def is_valid_openrouter_key(api_key: str) -> bool:
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        return response.status_code == 200
    except:
        return False


# --- DOWNLOAD MODEL SCRIPT (FOR LOCAL USE ONLY) ---
def download_model_locally():
    model_dir = "./models/faster-whisper-base"
    repo_id = "Systran/faster-whisper-base"

    if not os.path.exists(model_dir):
        with st.spinner("📥 Downloading Whisper model (one-time setup)..."):
            snapshot_dir = snapshot_download(
                repo_id=repo_id,
                revision="main",
                cache_dir="./hf_cache"
            )
            shutil.copytree(snapshot_dir, model_dir)
            shutil.rmtree("./hf_cache", ignore_errors=True)
        st.success("✅ Model downloaded and saved.")
    else:
        st.info("📁 Model already exists.")


# --- CHATBOT FUNCTION ---
def ask_question_about_lecture(question, context, api_key):
    full_prompt = f"""
    Lecture Content:
    {context}

    Student's Question:
    {question}

    Provide a clear and concise answer based on the lecture content.
    """
    return call_openrouter(full_prompt, api_key, task="chat")


# --- SESSION STATE INITIALIZATION ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "generated_notes" not in st.session_state:
    st.session_state.generated_notes = ""
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = ""
if "related_topics" not in st.session_state:
    st.session_state.related_topics = ""


# --- STREAMLIT APP ---
st.set_page_config(page_title="🎤 Lecture Voice-to-Notes Generator", layout="wide")

st.title("🎤 Lecture Voice-to-Notes Generator")
st.markdown("_Uses Faster-Whisper + OpenRouter API for Smart Formatting & Learning_")

# --- DOWNLOAD MODEL BUTTON (LOCAL ONLY) ---
if not is_deployed():
    if st.button("📥 Download Model (One-Time Setup)"):
        download_model_locally()

# --- FORCE OPENROUTER MODE IN CLOUD ---
mode = "☁️ OpenRouter API"
if is_deployed():
    st.info("🔒 Running in cloud mode. Only OpenRouter API available.")

# --- GET API KEY ---
api_key = st.text_input("🔑 Enter your OpenRouter API Key:", type="password")
if not api_key:
    st.warning("⚠️ Please enter your OpenRouter API key to continue.")
    st.stop()
elif not is_valid_openrouter_key(api_key):
    st.error("❌ Invalid or expired OpenRouter API key.")
    st.stop()

# --- LOAD MODEL ---
whisper_model = load_whisper()


# --- MAIN TABS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎧 Audio",
    "📝 Text",
    "🧩 Quiz",
    "📚 Topics",
    "💬 Chat",
    "⬇️ Download"
])


# --- TAB 1: AUDIO ---
with tab1:
    st.header("🎤 Convert Audio to Notes")

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

        if st.button("🔁 Convert Audio to Notes", key="audio_convert"):
            with st.spinner("Transcribing audio..."):
                transcript = transcribe_audio(whisper_model, temp_audio_path)

            if not transcript:
                st.error("🚫 Transcription returned empty result.")
            else:
                st.session_state.transcript = transcript
                st.subheader("📜 Full Transcript")
                st.text_area("", value=transcript, height=200)

                with st.spinner("Generating structured notes..."):
                    formatted_note = call_openrouter(transcript, api_key, task="format")
                    st.session_state.generated_notes = formatted_note

                st.subheader("🧾 Generated Notes")
                st.markdown(formatted_note)

            os.remove(temp_audio_path)


# --- TAB 2: TEXT INPUT ---
with tab2:
    st.header("📝 Paste or Type Lecture Transcript")

    user_text = st.text_area("Paste your lecture transcript here:", height=200, key="text_input")
    if user_text.strip() != "":
        st.session_state.transcript = user_text

    if st.button("📄 Generate Notes from Text", key="text_convert"):
        if user_text.strip() == "":
            st.warning("Please enter some text first.")
        else:
            with st.spinner("Generating structured notes from text..."):
                formatted_note = call_openrouter(user_text, api_key, task="format")
                st.session_state.generated_notes = formatted_note

            st.subheader("🧾 Generated Notes")
            st.markdown(formatted_note)


# --- TAB 3: QUIZ GENERATOR ---
with tab3:
    st.header("🧩 Generate Quiz Questions")

    if st.session_state.transcript:
        if st.button("🧩 Generate Quiz", key="quiz_generate"):
            with st.spinner("Creating quiz questions..."):
                quiz = call_openrouter(st.session_state.transcript, api_key, task="quiz")
                st.session_state.quiz_questions = quiz
            st.subheader("🧩 Quiz Questions")
            st.markdown(quiz)
    else:
        st.info("📝 First generate notes or paste a transcript to unlock quiz generation.")


# --- TAB 4: RELATED TOPICS ---
with tab4:
    st.header("📚 Suggest Related Topics")

    if st.session_state.transcript:
        if st.button("📖 Find Related Topics", key="topics_generate"):
            with st.spinner("Finding related topics..."):
                topics = call_openrouter(st.session_state.transcript, api_key, task="topics")
                st.session_state.related_topics = topics
            st.subheader("📖 Related Topics")
            st.markdown(topics)
    else:
        st.info("📝 First generate notes or paste a transcript to unlock topic suggestions.")


# --- TAB 5: CHATBOT ---
with tab5:
    st.header("💬 Lecture Assistant Chatbot")

    # Show conversation history
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f"🧑‍🎓 **You:** {chat['content']}")
        else:
            st.markdown(f"🤖 **Bot:** {chat['content']}")

    # Chat input
    user_question = st.text_input("Ask something about the lecture:", key="chat_input")

    if st.button("Send", key="send_chat"):
        if not st.session_state.transcript:
            st.warning("Please generate notes or paste a transcript first.")
        else:
            with st.spinner("Thinking..."):
                answer = ask_question_about_lecture(
                    user_question,
                    st.session_state.transcript,
                    api_key
                )
            # Save to history
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()  # Refresh to show new message

    # Clear Chat Button
    if st.button("🗑️ Clear Chat", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()


# --- TAB 6: DOWNLOAD CENTER ---
with tab6:
    st.header("⬇️ Download All Materials")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.session_state.generated_notes:
            st.download_button(
                label="📄 Notes (.md)",
                data=st.session_state.generated_notes,
                file_name="lecture_notes.md",
                mime="text/markdown"
            )

    with col2:
        if st.session_state.quiz_questions:
            st.download_button(
                label="🧩 Quiz (.md)",
                data=st.session_state.quiz_questions,
                file_name="quiz_questions.md",
                mime="text/markdown"
            )

    with col3:
        if st.session_state.related_topics:
            st.download_button(
                label="📚 Topics (.md)",
                data=st.session_state.related_topics,
                file_name="related_topics.md",
                mime="text/markdown"
            )

    with col4:
        if st.session_state.transcript:
            st.download_button(
                label="📜 Transcript (.txt)",
                data=st.session_state.transcript,
                file_name="transcript.txt",
                mime="text/plain"
            )

    if not any([
        st.session_state.generated_notes,
        st.session_state.quiz_questions,
        st.session_state.related_topics,
        st.session_state.transcript
    ]):
        st.info("📝 Generate materials first to enable downloads.")
