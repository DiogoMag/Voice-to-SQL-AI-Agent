# 1. Voice Input (Whisper)
# Task: Transcribe spoken English into text.
# Tech: Use openai-whisper or whisper.cpp for local inference.
    
import whisper
model = whisper.load_model("base")
result = model.transcribe("audio.wav")
query_text = result["text"]
