import speech_recognition as sr
from pydub import AudioSegment
import sys
import time
import os

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

total_chunks = len(audio) // 30000 + 1
print(f"Loading audio for transcription... Total chunks: {total_chunks}")

audio = AudioSegment.from_wav(output_wav)
chunk_length_ms = 30000  # 30 seconds
chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

full_text = ""
srt_output = ""

start_time_sec = 0

for i, chunk in enumerate(chunks):
    chunk_filename = f"chunk_{i}.wav"
    chunk.export(chunk_filename, format="wav")

    with sr.AudioFile(chunk_filename) as source:
        audio_data = recognizer.record(source)
        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")

        try:
            start_transcribe_time = time.time()
            text = recognizer.recognize_google(audio_data, language="el-GR")
            end_transcribe_time = time.time()
            
            time_taken = end_transcribe_time - start_transcribe_time
            print(f"Chunk {i + 1} transcribed successfully in {time_taken:.2f} seconds.")
            
            full_text += text + " "

            # Calculate timestamps
            end_time_sec = start_time_sec + (chunk_length_ms / 1000)
            start_timestamp = time.strftime('%H:%M:%S,000', time.gmtime(start_time_sec))
            end_timestamp = time.strftime('%H:%M:%S,000', time.gmtime(end_time_sec))
            
            srt_output += f"{i+1}\n{start_timestamp} --> {end_timestamp}\n{text}\n\n"
            
            start_time_sec = end_time_sec
        
        except sr.UnknownValueError:
            print(f"Chunk {i + 1}: Speech could not be recognized.")
        except sr.RequestError:
            print(f"Chunk {i + 1}: Could not request results.")

    progress = (i + 1) / len(chunks) * 100
    print(f"Progress: {progress:.2f}% completed")

# Save transcript
with open("transcript.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

# Save subtitles in SRT format
with open("subtitles.srt", "w", encoding="utf-8") as f:
    f.write(srt_output)

print("Transcription and subtitle generation completed!")
