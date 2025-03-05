import speech_recognition as sr
from pydub import AudioSegment
import sys
import time

# Check for command-line argument
if len(sys.argv) != 2:
    print("Usage: python Audio_Transcription.py <input_audio_file>")
    sys.exit(1)

# Get input audio file from command-line argument
input_audio = sys.argv[1]
output_wav = "converted_audio.wav"

print("Starting audio conversion...")
# Convert MP3 to WAV
audio = AudioSegment.from_file(input_audio)
audio.export(output_wav, format="wav")
print("Audio conversion completed.")

# Initialize recognizer
recognizer = sr.Recognizer()

print("Loading audio for transcription...")
# Load and transcribe audio
with sr.AudioFile(output_wav) as source:
    audio_data = recognizer.record(source)
    print("Transcription in progress...")
    
    try:
        start_time = time.time()
        text = recognizer.recognize_google(audio_data, language="el-GR")
        end_time = time.time()
        print("Transcription completed in {:.2f} seconds.".format(end_time - start_time))
        print("\nFull Transcript:\n", text)
        
        # Save transcript to a file
        with open("transcript.txt", "w", encoding="utf-8") as f:
            f.write(text)
    
    except sr.UnknownValueError:
        print("Speech could not be recognized.")
    except sr.RequestError:
        print("Could not request results from the speech recognition service.")
