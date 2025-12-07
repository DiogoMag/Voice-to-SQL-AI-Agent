import os
import whisper

# Add FFmpeg to PATH
os.environ["PATH"] += os.pathsep + r"D:\Software\ffmpeg-8.0-full_build\bin"

# Load model and move to GPU
model = whisper.load_model("base").to("cuda")

# Transcribe
result = model.transcribe("../samples/whatsap_sample_1.wav")

print("Transcription:\n", result["text"])
