# pip install -U openai-whisper py-chocolatey 
# choco install ffmpeg (with elevated priveleges)
import whisper
import os

file_types = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".wma", ".mp4", ".webm"]

def remove_extension(string):
    for file_type in file_types:
        string = string.replace(file_type, "")

    return string

def main():
    # load model
    filename = input("Enter file name including extension (ex. audio.mp3): ")

    # Turbo is too slow for our use case. Also would need to convert to 128 mel bins which makes it even slower
    # model = whisper.load_model("turbo") 

    # Tiny is much faster, near instant, but has trouble recognizing spoken words
    # model = whisper.load_model("tiny")

    # Medium seems to be the best balance of speed and accuracy
    model = whisper.load_model("medium")
 
    # load audio and pad/trim it to fit 30 seconds for sliding window
    audio = whisper.load_audio(filename)
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    # print(mel.shape)

    # detect the spoken language
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")

    # decode the audio
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)

    # write to file
    output_filename = remove_extension(filename)
    with open(f"{output_filename}.txt", "w", encoding="utf-8") as file:
        file.write(result.text)

    # print the recognized text
    print(result.text)

if __name__ == "__main__":
    main()