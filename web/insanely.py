from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu")

segments, info = model.transcribe("../example files/chinese.wav")

for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
