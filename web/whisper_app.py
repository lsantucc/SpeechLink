# https://github.com/m-bain/whisperX

import whisperx
import tempfile
import os
from pydub import AudioSegment
import numpy as np
import datetime

def is_silent(audio_path, silence_threshold=-40.0, chunk_size=10):
    """
    Check if the audio is silent.
    
    :param audio_path: Path to the audio file
    :param silence_threshold: Silence threshold in dB (e.g., -40 dB)
    :param chunk_size: Size of the chunk to process in milliseconds
    :return: True if the audio is silent, False otherwise
    """
    # Load the audio file
    audio = AudioSegment.from_file(audio_path)
    
    # Convert to mono if stereo
    if audio.channels > 1:
        audio = audio.set_channels(1)
    
    # Process the audio in chunks
    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i+chunk_size]
        # Get the loudness of the chunk in dB
        loudness = chunk.dBFS  # dB relative to full scale
        if loudness > silence_threshold:
            return False  # If any chunk is above the silence threshold, it's not silent
    
    return True  # If all chunks are below the threshold, it's silent

def transcribe(audio_data, model, device="cuda"):
    try:
        print(type(audio_data))

        # Despite claiming support for str, bytes, and os.PathLike objects I couldn't get whisperX to work with
        # bytes because of ffmpeg piping issue
        # Workaround is to create a temporary file, has surprisingly low time cost

        # Create temporary file (only took 0:00:00.002253 for 7 second file, low cost)
        # https://stackoverflow.com/questions/8577137/how-can-i-create-a-tmp-file-in-python
        start_time = datetime.datetime.now()    
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name
        end_time = datetime.datetime.now() - start_time
        print(end_time)

        if is_silent(tmp_path):
            return "", ""
        
        # Load audio
        audio = whisperx.load_audio(tmp_path)

        # Delete file containing audio data since we are done with it 
        os.unlink(tmp_path)
        
        # Transcribe
        result = model.transcribe(audio, batch_size=16)
        language = result["language"]
        
        # Align segments. This will be useful for when words are split. Can use all segments that we have
        # with relevant calculated timestamps and align
        
        # align (this causes bugs currently)
        #model_a, metadata = whisperx.load_align_model(language_code=language, device=device)
        #result = whisperx.align(result["segments"], model_a, metadata, audio, device)
        
        result_string = "".join(segment["text"] for segment in result["segments"])
        if result_string == " you" or result_string == "you" or result_string is None:
            result_string = ""
        return result_string, language
    
    except Exception as e:
        print(f"Error in whisper_app {e}")

# Test
if __name__ == "__main__":
    device = "cuda"
    model = whisperx.load_model("medium", device=device)

    with open(r"PUT PATH HERE", 'rb') as f:
        audio_data = f.read() 

    transcription, language = transcribe(audio_data, model)
    print(f"Transcription: {transcription}")
    print(f"Language: {language}")