# download_model.py

import os
import shutil
from huggingface_hub import snapshot_download

model_dir = "./models/faster-whisper-base"
repo_id = "Systran/faster-whisper-base"

if not os.path.exists(model_dir):
    print("📥 Downloading Whisper 'base' model from Hugging Face...")

    # Download to temporary cache
    snapshot_dir = snapshot_download(
        repo_id=repo_id,
        revision="main",
        cache_dir="./hf_cache"
    )

    # Move to desired location
    shutil.copytree(snapshot_dir, model_dir)
    print(f"✅ Model saved to {model_dir}")

    # Cleanup temp cache
    shutil.rmtree("./hf_cache", ignore_errors=True)
else:
    print("📁 Model already exists.")
