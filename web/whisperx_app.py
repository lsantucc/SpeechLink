from whisperx import load_model
from pydub import AudioSegment
import os
import shutil

file_types = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".wma", ".mp4", ".webm"]
temp_dir = "temp"

if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

def remove_extension(string):
    for file_type in file_types:
        string = string.replace(file_type, "")
    return string

def transcribe(filepath, model_size="medium", device="cpu"):
    model = load_model(model_size, device=device)

    filename, file_extension = os.path.splitext(filepath)
    audio = AudioSegment.from_file(filepath)

    time_increment = 30 * 1000  # 30 seconds in milliseconds
    total_time = len(audio)
    audio_chunks = []

    time = 0
    while time < total_time:
        audio_chunks.append(audio[time:time+time_increment])
        time += time_increment

    result = ""
    detected_language = ""

    for i, chunk in enumerate(audio_chunks):
        chunk_path = f"{temp_dir}/chunk_{i}{file_extension}"
        chunk.export(chunk_path, format=file_extension.replace('.', ''))

        audio_path = chunk_path
        audio_data = model.preprocess(audio_path)
        segments = model.transcribe(audio_data)

        if not detected_language and segments and 'language' in segments[0]:
            detected_language = segments[0]['language']

        for segment in segments:
            result += segment['text'].strip() + " "

    shutil.rmtree(temp_dir)

    final_result = ""
    if detected_language != "en":
        for i, char in enumerate(result):
            if char.isupper() and i >= 2 and result[i-2] not in {",", "?", "!", "."}:
                final_result = final_result[:-1]
                final_result += ". "
            final_result += char
    else:
        final_result = result

    return final_result.strip(), detected_language

if __name__ == "__main__":
    # Example usage
    # output_text, language = transcribe("your_audio_file.wav", model_size="medium", device="cpu")
    pass