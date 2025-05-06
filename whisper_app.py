# File that uses WhisperX (fast fork of Open-AI's Whisper) to do transcription and translation if needed
# WhisperX: https://github.com/m-bain/whisperX

import whisperx
import tempfile
import os
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
        
        # Load audio
        audio = whisperx.load_audio(tmp_path)

        # Delete file containing audio data 
        os.unlink(tmp_path)
        
        # Transcribe
        result = model.transcribe(audio, batch_size=16)
        language = result["language"]
        
        # Join segments that WhisperX returns into text
        result_string = "".join(segment["text"] for segment in result["segments"])
        return result_string, language
    
    except Exception as e:
        print(f"Error in whisper_app {e}")

# Test with CUDA
if __name__ == "__main__":
    device = "cuda"
    model = whisperx.load_model("medium", device=device)

    with open(r"PUT PATH TO FILE HERE", 'rb') as f:
        audio_data = f.read() 

    transcription, language = transcribe(audio_data, model)
    print(f"Transcription: {transcription}")
    print(f"Language: {language}")