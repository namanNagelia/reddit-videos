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
from PIL import Image, ImageDraw, ImageFont, ImageOps
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
        print(f"Saved TTS audio to {filename}")

        # Clean up the temporary file
        # os.remove(temp_filename)

        return filename

    def parse_srt(self, srt_file):
        with open(srt_file, "r") as f:
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

    def make_video(self,
                   video_path, music_folder, tts_path, srt_path, output_path, target_resolution=(
                       720, 1280)
                   ):
        video_clip = VideoFileClip(video_path)
        tts_clip = AudioFileClip(tts_path)
        video_clip = video_clip.resize(width=1920)
        music_files = [
            os.path.join(music_folder, file)
            for file in os.listdir(music_folder)
            if file.endswith(".mp3")
        ]
        num_music_files = len(music_files)
        num_clips_to_select = min(
            num_music_files, 40
        )  # Adjust the number of music clips to select as needed
        music_paths = random.sample(music_files, num_clips_to_select)
        music_clips = [
            AudioFileClip(music_path).fx(afx.volumex, 0.1) for music_path in music_paths
        ]  # Reduce volume by 50%

        # Repeat the video to match the length of the TTS clip
        video_clip = vfx.loop(video_clip, duration=tts_clip.duration)

        # Loop the audio clips sequentially to match the length of the TTS clip
        looped_music_clip = self.loop_audio_clips_sequentially(
            music_clips, tts_clip.duration)

        # Create a composite audio clip with TTS and music starting at the same time
        composite_audio = CompositeAudioClip([tts_clip, looped_music_clip]).set_duration(
            tts_clip.duration
        )
        subtitles = self.parse_srt(srt_path)
        font_path = "NotoSans-Bold.ttf"
        subtitle_clips = [
            TextClip(
                text,
                fontsize=60,
                color="white",
                font=font_path,
                stroke_color="black",
                stroke_width=1,
                method="caption",
                size=video_clip.size,
                align="center",
                # bg_color="rgba(0, 0, 0, 0.5)",  # semi-transparent background
            )
            .set_position(("center", "center"))
            .set_start(start)
            .set_end(end)
            for (start, end, text) in subtitles
        ]

        # Overlay subtitles on the video clip
        video_with_subtitles = CompositeVideoClip(
            [video_clip] + subtitle_clips)

        # Set the composite audio to the video clip with subtitles
        final_video = video_with_subtitles.set_audio(composite_audio)

        # Add fade-in and fade-out effects
        final_video = final_video.fadein(2).fadeout(2)

        # Write the final video to a file
        final_video.write_videofile(
            output_path, codec="libx264", audio_codec="aac", fps=30, preset="ultrafast"
        )
        print(f"Saved final video to {output_path}")
