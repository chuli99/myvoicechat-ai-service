import whisper

model = whisper.load_model("turbo",device="cuda")
result = model.transcribe("audios/audioJulian.ogg",fp16=True)
print(result["text"])
print("A")