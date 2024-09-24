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


font_path = "resources/fonts/Salsa.ttf"

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './redditGoogleKey.json'


class VideoTools:
    def __init__(self):
        pass

    def print_OpenAI(self):
        print(client)

    def convert_text_to_speech(self, text, filename, voice_name="en-US-Neural2-J"):

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
            speaking_rate=1.0,
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

    def generate_srt(self, file_path):
        audio_file = open(file_path, "rb")
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["word"],
        )

        # Group words into lines with approximately three words per line
        grouped_segments = []
        current_line = []
        current_start = None
        for index, segment in enumerate(transcript.words):
            if len(current_line) == 0:
                current_start = segment["start"]
            current_line.append(segment["word"])
            if len(current_line) == 3 or index == len(transcript.words) - 1:
                current_end = segment["end"]
                grouped_segments.append(
                    (current_start, current_end, " ".join(current_line))
                )
                current_line = []

        script_dir = os.path.dirname(os.path.abspath(__file__))

        srt_file_path = os.path.join(script_dir, "subtitles.srt")
        with open(srt_file_path, "w") as srt_file:
            for index, (start_time, end_time, text) in enumerate(grouped_segments):
                start_time_str = (
                    time.strftime("%H:%M:%S", time.gmtime(start_time))
                    + ","
                    + str(int((start_time % 1) * 1000)).zfill(3)
                )
                end_time_str = (
                    time.strftime("%H:%M:%S", time.gmtime(end_time))
                    + ","
                    + str(int((end_time % 1) * 1000)).zfill(3)
                )
                srt_file.write(
                    f"{index + 1}\n{start_time_str} --> {end_time_str}\n{text}\n\n"
                )

        print(f"Saved SRT file to {srt_file_path}")
        return srt_file_path

    def make_video(self, video_path, music_path, tts_path, srt_path, output_path, target_resolution=(720, 1280)):
        try:
            video_clip = VideoFileClip(video_path)
            tts_clip = AudioFileClip(tts_path)
            music_clip = AudioFileClip(music_path).fx(afx.volumex, 0.1)

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
                subtitle_clip = (TextClip(text, fontsize=60, color='white', font="Salsa",
                                          stroke_color='black', stroke_width=1,
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
                output_path, codec="libx264", audio_codec="aac", fps=30, preset="ultrafast"
            )
            print(f"Saved final video to {output_path}")

        except Exception as e:
            print(f"An error occurred while making the video: {str(e)}")

    def time_to_seconds(self, time_str):
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + float(s)
