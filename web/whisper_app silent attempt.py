# Transcription/translation using whisper
# Whisper can only take 30 seconds of audio at a time. If the input file is longer than 30 seconds
#    we need to break it into chunks
# If we return a lot of text it needs to be formatted to be displayed properly otherwise it will be one huge line
# Need to improve speed by forcing GPU use on the 3080 and maybe parallel processing?
# Need to dynamically determine silence threshold based on average loudness (just lower than maybe 20%) ***


# pip install -U openai-whisper py-chocolatey 
# choco install ffmpeg (with elevated priveleges)
import whisper
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence

file_types = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".wma", ".mp4", ".webm"]

def remove_extension(string):
    for file_type in file_types:
        string = string.replace(file_type, "")

    return string

def transcribe(filepath, model):
    # FIRST check to see if the audio we get even has words
    # *** check decibel of audio; if its below 30 decibels we just ignore (involves sending 
    # specific response to frontend indicating this)
    pydub




    # load model
    # filename = input("Enter file name including extension (ex. audio.mp3): ")

    # Turbo is too slow for our use case. Also would need to convert to 128 mel bins which makes it even slower
    # model = whisper.load_model("turbo") 

    # Tiny is much faster, near instant, but has trouble recognizing spoken words
    # model = whisper.load_model("tiny")

    # Medium seems to be the best balance of speed and accuracy
    filename, file_extension = os.path.splitext(filepath)
    # need to split audio into chunks of 30s
    newAudio = AudioSegment.from_file(filepath) 
    timeIncrement = 30 * 1000 # 30 seconds -> 30000 ms
    totalTime = len(newAudio) # total time in ms
    audio_chunks = split_on_silence(newAudio, min_silence_len=200, silence_thresh=-5)
    with open("test.txt", "a+") as f:
        f.write(str(len(audio_chunks)))
    # need to loop here through the chunks array and make a new one with as many 30 second segments as possible
    # sum the chunks until we get a 30 second segment, add to new array, move on until end of audio_chunks
    new_chunk = audio_chunks[0]
    new_chunks = []
    while i < len(audio_chunks):
        # Combine audio clips until they are as close to 30 seconds as possible
        while len(new_chunk) + len(audio_chunks[i]) <= timeIncrement and i < len(audio_chunks):
            new_chunk += audio_chunks[i]
            i += 1
        
        # If the segment received from the silent split is >30s then we break it into parts
        time = 0
        while time <= totalTime:
            new_chunks.append(new_chunk[time:time+timeIncrement])  
            time += timeIncrement
        
        new_chunks.append(new_chunk)
        
        # Reset to empty audio
        new_chunk = AudioSegment.silent(0)

    with open("test.txt", "a+") as f:
        f.write(f"Length of new_chunks is {len(new_chunks)}")

    # load audio and pad/trim it to fit 30 seconds for sliding window
    result = ""
    for i, chunk in enumerate(new_chunks):
        chunk.export(out_f = f"time_split{i}{file_extension}", format = file_extension.replace('.', ''))
        audio = whisper.load_audio(f"time_split{i}{file_extension}") # this expects filepath not memory     
        audio = whisper.pad_or_trim(audio)

        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        # print(mel.shape)

        # detect the spoken language
        _, probs = model.detect_language(mel)
        language = max(probs, key=probs.get)

        # decode the audio
        # options = whisper.DecodingOptions(task="Translate" if language != "en" else "transcribe")
        options = whisper.DecodingOptions()
        decoded = whisper.decode(model, mel, options)
        result += f". {decoded.text}"

    return result, language

if __name__ == "__main__":
    transcribe()
