from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeAudioClip,
    CompositeVideoClip,
    TextClip
)
from src.redditScraper import RedditScraper
from src.videoTools import VideoTools
import os
import random

videoTool = VideoTools()


# Steps:
# 1: Make UI and you put reddit URL
# 2: It gets the text
scraper = RedditScraper()
post_url = "https://www.reddit.com/r/AmItheAsshole/comments/1evge2u/aita_for_telling_my_coworker_that_i_didnt_enjoy/"
post_text = scraper.get_post_text(post_url)

# 3: Convert to audio
tts_path = videoTool.convert_text_to_speech(
    text=post_text[0], filename="audio.mp3")

# 4: Randomly choose a minecraft/SS video and concat
resources_folder = os.path.join(os.getcwd(), "resources")
video_folder = os.path.join(resources_folder, "videos")
music_folder = os.path.join(resources_folder, "music")
video_files = [f for f in os.listdir(
    video_folder) if f.endswith(('.mp4', '.avi', '.mov'))]
random_video = random.choice(video_files)
video_path = os.path.join(video_folder, random_video)
font_file = os.path.join(resources_folder, "Salsa.ttf")
print(font_file)
# Get a random music file
music_files = [f for f in os.listdir(
    music_folder) if f.endswith(('.mp3', '.wav'))]
random_music = random.choice(music_files)
music_path = os.path.join(music_folder, random_music)

# Generate subtitles
srt_path = videoTool.generate_srt(tts_path)

# 5: Export video
video = videoTool.make_video(video_path=video_path, music_path=music_path, tts_path=tts_path,
                             srt_path=srt_path, output_path="output.mp4", target_resolution=(720, 1280), font=font_file)

# 6: Once approved, upload to youtube
