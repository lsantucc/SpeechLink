# Transcription/translation using whisper
# Whisper can only take 30 seconds of audio at a time. If the input file is longer than 30 seconds
#    we need to break it into chunks
# If we return a lot of text it needs to be formatted to be displayed properly otherwise it will be one huge line
# Need to improve speed by forcing GPU use and parallel processing

# pip install -U openai-whisper py-chocolatey 
# choco install ffmpeg (with elevated priveleges)
import whisper
import os
from pydub import AudioSegment
import shutil

file_types = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".wma", ".mp4", ".webm"]
temp_dir = "temp"

def remove_extension(string):
    for file_type in file_types:
        string = string.replace(file_type, "")

    return string

def transcribe(filepath, model):
    # Medium seems to be the best balance of speed and accuracy
    # device = "cuda" 
    # model = model.to(device)
    filename, file_extension = os.path.splitext(filepath)
    # need to split audio into chunks of 30s
    audio = AudioSegment.from_file(filepath) 
    timeIncrement = 30 * 1000 # 30 seconds -> 30000 ms
    totalTime = len(audio) # total time in ms
    audio_chunks = []
   
    time = 0
    while time < totalTime:
        audio_chunks.append(audio[time:time+timeIncrement])
        time += timeIncrement

    # load audio and pad/trim it to fit 30 seconds for sliding window
    result = ""
    for i, chunk in enumerate(audio_chunks):
        chunk.export(out_f = f"{temp_dir}/time_split{i}{file_extension}", format = file_extension.replace('.', ''))
        audio = whisper.load_audio(f"{temp_dir}/time_split{i}{file_extension}") # this expects filepath not memory     
        audio = whisper.pad_or_trim(audio)

        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        # print(mel.shape)

        # detect the spoken language
        _, probs = model.detect_language(mel)
        language = max(probs, key=probs.get)

        # decode the audio
        options = whisper.DecodingOptions(task="Translate" if language != "en" else "transcribe")
        #options = whisper.DecodingOptions()
        decoded = whisper.decode(model, mel, options)
        result += f"{decoded.text}"

    # shutil.rmtree(temp_dir)
    # Translated text does not have punctuation
    if language != "en":
        final_result = ""
        for i, char in enumerate(result):
            if char.isupper() and result[i-2] != "," and result[i-2] != "?" and result[i-2] != "!" and result[i-2] != "." and i >= 2:
                final_result = final_result[:-1]
                final_result += ". "
            final_result += char
    else:
        final_result = result

    return final_result, language

if __name__ == "__main__":
    transcribe()
