from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import subprocess
from openai import OpenAI
import json
import requests
import numpy as np
from google.cloud import texttospeech
from pydub import AudioSegment
from pydub.silence import split_on_silence
from moviepy.audio.AudioClip import concatenate_audioclips
import re
import os
import random
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeAudioClip,
    CompositeVideoClip,
    TextClip
)
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import moviepy.video.fx.all as vfx
from moviepy.audio.fx.all import volumex
import moviepy.audio.fx.all as afx
import time
from datetime import datetime
import pickle
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_APIKEY"))

# completion = client.chat.completions.create(
#     model="gpt-4o",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Hello!"}
#     ]
# )


font_path = "resources/fonts/Mont.ttf"

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './redditGoogleKey.json'


class VideoTools:
    def __init__(self):
        pass

    def print_OpenAI(self):
        print(client)

    def makeBetterScript(self, text):
        prompt = f"""
    Please take the following script and make it more interesting and funny. 
    Enhance the dialogue, add humorous elements, and improve the overall 
    entertainment value while maintaining the core message and structure.

    Original script:
    {text}

    Improved, funnier version:
    """

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a talented  writer tasked with improving scripts."},
                {"role": "user", "content": prompt}
            ]
        )
        improved_script = completion.choices[0].message.content
        return improved_script

    def convert_text_to_speech(self, text, filename, voice_name="en-US-Neural2-J"):
        # Print the byte length of the text
        text_bytes = text.encode('utf-8')
        byte_length = len(text_bytes)
        print(f"Text length: {byte_length} bytes")

        # Check if text is too long for standard API
        if byte_length > 4800:  # Using 4800 as a safe limit (below 5000)
            print("Text is too long for standard API, splitting into chunks...")
            return self._process_long_text(text, filename, voice_name)

        # Standard processing for shorter texts
        client = texttospeech.TextToSpeechClient()

        # Use SSML to add breaks and emphasis for more natural speech
        ssml_text = f"""
        <speak>
        {text}
        </speak>
        """

        synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice_name,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.2,
            pitch=0,
            volume_gain_db=0,
            effects_profile_id=["medium-bluetooth-speaker-class-device"]
        )

        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # Write the response to a temporary file
        temp_filename = "temp_tts_output.mp3"
        with open(temp_filename, "wb") as out:
            out.write(response.audio_content)
            print(f'Audio content written to file "{temp_filename}"')

        # Load the audio file
        audio = AudioSegment.from_mp3(temp_filename)

        # Split on silence
        chunks = split_on_silence(
            audio, silence_thresh=-40, min_silence_len=300, keep_silence=100
        )

        # Combine chunks
        trimmed_audio = AudioSegment.empty()
        for chunk in chunks:
            trimmed_audio += chunk

        # Export the final audio
        # trimmed_audio.export(filename, format="mp3", bitrate="128k")
        print(f"Saved TTS audio to {temp_filename}")

        # Clean up the temporary file
        # os.remove(temp_filename)

        return temp_filename

    def _process_long_text(self, text, filename, voice_name):
        """Process long text by splitting it into smaller chunks and combining the audio."""
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = ""
        chunk_files = []

        # Group sentences into chunks under 4800 bytes
        for sentence in sentences:
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            if len(test_chunk.encode('utf-8')) > 4800:
                # Process current chunk if adding this sentence would make it too long
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = sentence
                else:
                    # If a single sentence is too long, split it into words
                    words = sentence.split()
                    temp_sentence = ""
                    for word in words:
                        test_sentence = temp_sentence + " " + word if temp_sentence else word
                        if len(test_sentence.encode('utf-8')) > 4800:
                            chunks.append(temp_sentence)
                            temp_sentence = word
                        else:
                            temp_sentence = test_sentence
                    if temp_sentence:
                        current_chunk = temp_sentence
            else:
                current_chunk = test_chunk

        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(current_chunk)

        print(f"Split text into {len(chunks)} chunks")

        # Process each chunk
        client = texttospeech.TextToSpeechClient()
        for i, chunk in enumerate(chunks):
            print(
                f"Processing chunk {i+1}/{len(chunks)} ({len(chunk.encode('utf-8'))} bytes)")

            ssml_text = f"""<speak>{chunk}</speak>"""
            synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name=voice_name,
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.2,
                pitch=0,
                volume_gain_db=0,
                effects_profile_id=["medium-bluetooth-speaker-class-device"]
            )

            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            chunk_filename = f"temp_chunk_{i}.mp3"
            with open(chunk_filename, "wb") as out:
                out.write(response.audio_content)

            chunk_files.append(chunk_filename)

        # Combine all audio chunks
        combined = AudioSegment.empty()
        for chunk_file in chunk_files:
            audio = AudioSegment.from_mp3(chunk_file)
            combined += audio

        # Export combined audio
        output_filename = "temp_tts_output.mp3"
        combined.export(output_filename, format="mp3", bitrate="128k")

        # Clean up temporary files
        for chunk_file in chunk_files:
            os.remove(chunk_file)

        print(f"Combined audio saved to {output_filename}")
        return output_filename

    def parse_srt(self, srt_file_path):
        try:
            # Check if the file exists
            if not os.path.exists(srt_file_path):
                raise FileNotFoundError(
                    f"The SRT file does not exist at the specified path: {srt_file_path}")

            with open(srt_file_path, "r", encoding="utf-8") as f:
                content = f.read()

            subtitles = []
            for block in content.strip().split("\n\n"):
                lines = block.split("\n")
                if len(lines) >= 3:
                    times = lines[1].split(" --> ")
                    start_time = times[0].replace(",", ".")
                    end_time = times[1].replace(",", ".")
                    text = " ".join(lines[2:])
                    subtitles.append((start_time, end_time, text))

            return subtitles

        except Exception as e:
            print(f"An error occurred while parsing the SRT file: {str(e)}")
            return []

    def loop_audio_clips_sequentially(self, audio_clips, duration):
        concatenated = concatenate_audioclips(audio_clips)
        loops = []
        current_duration = 0

        while current_duration < duration:
            remaining_duration = duration - current_duration
            clip_duration = concatenated.duration

            if remaining_duration >= clip_duration:
                loops.append(concatenated)
                current_duration += clip_duration
            else:
                loops.append(concatenated.subclip(0, remaining_duration))
                current_duration += remaining_duration

        return concatenate_audioclips(loops)

    def generate_srt(self, file_path, words=None):
        """
        Generate SRT subtitle file from audio using OpenAI Whisper API
        If words is provided, use that instead of transcribing the file
        """
        if words is None:
            # Open and transcribe the audio file
            with open(file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
                words = transcript.words
        else:
            print("Using provided words list")

        # Group words into lines with proper sentence structure
        grouped_segments = []
        current_line = []
        current_start = None
        sentence_endings = {'.', '!', '?'}

        def get_word_text(word):
            """Helper function to safely get word text"""
            if isinstance(word, dict):
                return word.get('word', '')
            return getattr(word, 'word', '')

        def get_word_start(word):
            """Helper function to safely get word start time"""
            if isinstance(word, dict):
                return word.get('start', 0)
            return getattr(word, 'start', 0)

        def get_word_end(word):
            """Helper function to safely get word end time"""
            if isinstance(word, dict):
                return word.get('end', 0)
            return getattr(word, 'end', 0)

        def is_next_word_capitalized(current_index, words_list):
            """Helper function to safely check if next word starts with capital"""
            if current_index >= len(words_list) - 1:
                return False
            next_word_text = get_word_text(words_list[current_index + 1])
            return next_word_text and next_word_text[0].isupper()

        def should_capitalize(word_text, is_start=False):
            """Helper function to determine if word should be capitalized"""
            if not word_text:
                return False
            always_capitalize = {'i', 'i\'m', 'i\'ve', 'i\'ll', 'i\'d'}
            return (is_start or
                    word_text.lower() in always_capitalize or
                    word_text.lower().startswith('i\''))

        def format_line(line):
            """Helper function to format a line of text"""
            if not line:
                return ""
            # Join words and handle basic punctuation
            text = " ".join(line)
            # Capitalize first word if needed
            if text and should_capitalize(line[0], True):
                text = text[0].upper() + \
                    text[1:] if len(text) > 1 else text.upper()
            # Add period if no sentence ending
            if text and not any(text.endswith(end) for end in sentence_endings):
                text += "."
            return text

        for index, word in enumerate(words):
            # Get word properties safely
            word_text = get_word_text(word)
            if not word_text:  # Skip empty words
                continue

            # Start a new line
            if len(current_line) == 0:
                current_start = get_word_start(word)

            # Handle capitalization
            if should_capitalize(word_text, len(current_line) == 0):
                word_text = word_text[0].upper(
                ) + word_text[1:] if len(word_text) > 1 else word_text.upper()

            # Add word to current line
            current_line.append(word_text)

            # Check if we should end the line
            should_end_line = (
                len(current_line) >= 5 or  # Line is long enough
                index == len(words) - 1 or  # Last word
                # Sentence ending
                any(word_text.endswith(end) for end in sentence_endings) or
                # Next word starts with capital
                is_next_word_capitalized(index, words)
            )

            if should_end_line:
                line_text = format_line(current_line)
                if line_text:  # Only add non-empty lines
                    grouped_segments.append(
                        (current_start, get_word_end(word), line_text)
                    )
                current_line = []

        # Generate SRT file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        srt_file_path = os.path.join(script_dir, "subtitles.srt")

        with open(srt_file_path, "w", encoding='utf-8') as srt_file:
            for index, (start_time, end_time, text) in enumerate(grouped_segments):
                # Format start time
                start_time_str = (
                    time.strftime("%H:%M:%S", time.gmtime(start_time))
                    + ","
                    + str(int((start_time % 1) * 1000)).zfill(3)
                )

                # Format end time
                end_time_str = (
                    time.strftime("%H:%M:%S", time.gmtime(end_time))
                    + ","
                    + str(int((end_time % 1) * 1000)).zfill(3)
                )

                # Write SRT entry
                srt_file.write(
                    f"{index + 1}\n{start_time_str} --> {end_time_str}\n{text}\n\n"
                )

        print(f"Saved SRT file to {srt_file_path}")
        return srt_file_path

    def make_video(self, video_path, music_path, tts_path, srt_path, output_path, font, target_resolution=(720, 1280)):
        try:
            video_clip = VideoFileClip(video_path)
            tts_clip = AudioFileClip(tts_path)
            music_clip = AudioFileClip(music_path).fx(afx.volumex, 0.05)

            video_clip = vfx.loop(video_clip, duration=tts_clip.duration)
            looped_music_clip = self.loop_audio_clips_sequentially(
                [music_clip], tts_clip.duration)

            composite_audio = CompositeAudioClip(
                [tts_clip, looped_music_clip]).set_duration(tts_clip.duration)

            subtitles = self.parse_srt(srt_path)

            subtitle_clips = []
            for start, end, text in subtitles:
                start_time = self.time_to_seconds(start)
                end_time = self.time_to_seconds(end)
                subtitle_clip = (TextClip(text, fontsize=60, color='white', font="Mont-Bold",
                                          stroke_color='white', stroke_width=1,
                                          size=video_clip.size, method='caption')
                                 .set_position(('center', 'bottom'))
                                 .set_start(start_time)
                                 .set_duration(end_time - start_time))
                subtitle_clips.append(subtitle_clip)

            video_with_subtitles = CompositeVideoClip(
                [video_clip] + subtitle_clips)
            final_video = video_with_subtitles.set_audio(composite_audio)

            final_video = final_video.fadein(2).fadeout(2)

            final_video.write_videofile(
                output_path, codec="libx264", audio_codec="aac", fps=30, preset="ultrafast", threads=os.cpu_count()
            )
            print(f"Saved final video to {output_path}")

        except Exception as e:
            print(f"An error occurred while making the video: {str(e)}")

    def time_to_seconds(self, time_str):
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + float(s)
