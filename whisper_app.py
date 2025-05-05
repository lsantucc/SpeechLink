# https://github.com/m-bain/whisperX

import whisperx
import tempfile
import os
from pydub import AudioSegment
from pydub.silence import detect_silence
import numpy as np
import datetime

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

        # audio_segment = AudioSegment.from_file(tmp_path)
        # if detect_silence(audio_segment, min_silence_len=450, silence_thresh=-40):
        #     return "", ""
        
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