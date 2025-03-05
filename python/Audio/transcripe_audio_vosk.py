from vosk import Model, KaldiRecognizer
import wave
import json
import sys
import os
import time

# Check for command-line arguments
if len(sys.argv) != 3:
    print("Usage: python vosk_transcription.py <input_audio_file> <vosk_model_path>")
    sys.exit(1)

# Get input audio file and model path from command-line arguments
input_audio = sys.argv[1]
model_path = sys.argv[2]
output_wav = "converted_audio.wav"

print("Starting audio conversion...")
# Convert MP3 to WAV (16KHz, mono) using FFmpeg
os.system(f"ffmpeg -i '{input_audio}' -ac 1 -ar 16000 '{output_wav}'")
print("Audio conversion completed.")

# Load the VOSK model
if not os.path.exists(model_path):
    print("VOSK model not found at specified path! Please check the path and try again.")
    sys.exit(1)

model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

# Open WAV file
with wave.open(output_wav, "rb") as wf:
    total_frames = wf.getnframes()
    frame_rate = wf.getframerate()
    transcript = []
    processed_frames = 0
    srt_output = ""
    index = 1
    time_step = 3  # Approximate subtitle duration in seconds
    current_time = 0
    
    print("Starting transcription...")
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result["text"]
            transcript.append(text)
            
            # Format timestamps
            start_timestamp = time.strftime('%H:%M:%S,000', time.gmtime(current_time))
            end_timestamp = time.strftime('%H:%M:%S,000', time.gmtime(current_time + time_step))
            
            # Construct SRT entry
            srt_output += f"{index}\n{start_timestamp} --> {end_timestamp}\n{text}\n\n"
            
            current_time += time_step
            index += 1
        
        processed_frames += len(data)
        progress = (processed_frames / total_frames) * 100
        print(f"Progress: {progress:.2f}% completed", end='\r')

# Save transcript
transcript_text = " ".join(transcript)
with open("transcript.txt", "w", encoding="utf-8") as f:
    f.write(transcript_text)

# Save subtitles in SRT format
with open("subtitles.srt", "w", encoding="utf-8") as f:
    f.write(srt_output)

print("\nGreek transcription complete! Transcript saved as transcript.txt and subtitles saved as subtitles.srt")
