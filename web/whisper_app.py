# Transcription/translation using whisper
# Whisper can only take 30 seconds of audio at a time. If the input file is longer than 30 seconds
#    we need to break it into chunks

# pip install -U openai-whisper py-chocolatey 
# choco install ffmpeg (with elevated priveleges)
import whisper
import os
from pydub import AudioSegment

file_types = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".wma", ".mp4", ".webm"]

def remove_extension(string):
    for file_type in file_types:
        string = string.replace(file_type, "")

    return string

def transcribe(filepath):
    # load model
    # filename = input("Enter file name including extension (ex. audio.mp3): ")

    # Turbo is too slow for our use case. Also would need to convert to 128 mel bins which makes it even slower
    # model = whisper.load_model("turbo") 

    # Tiny is much faster, near instant, but has trouble recognizing spoken words
    # model = whisper.load_model("tiny")

    # Medium seems to be the best balance of speed and accuracy
    model = whisper.load_model("medium")

    # need to split audio into chunks of 30s
    audio_chunks = []
    newAudio = AudioSegment.from_wav(filepath)
    time = 0
    timeIncrement = 30 * 1000 # (ms)
    totalTime = newAudio.duration_seconds * 1000 # (ms)
    while(time != totalTime):
        audio_chunks.append(newAudio[time:time+timeIncrement])
        time += timeIncrement

    # load audio and pad/trim it to fit 30 seconds for sliding window
    result = ""
    for chunk in audio_chunks:
        with open(f"temp{time}.wav", 'wb') as f:
            f.write()
        audio = whisper.load_audio(f"temp{time}.wav") # this expects filepath not memory     
        audio = whisper.pad_or_trim(audio)

        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        # print(mel.shape)

        # detect the spoken language
        _, probs = model.detect_language(mel)
        language = max(probs, key=probs.get)

        # decode the audio
        options = whisper.DecodingOptions(task="Translate" if language != "en" else "transcribe")
        decoded = whisper.decode(model, mel, options)
        result += decoded.text

    return result, language

if __name__ == "__main__":
    transcribe()
