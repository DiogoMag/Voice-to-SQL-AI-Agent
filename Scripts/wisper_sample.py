import whisper
model = whisper.load_model("base")
result = model.transcribe("audio.wav")
query_text = result["text"]
