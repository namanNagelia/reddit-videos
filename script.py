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
from multiprocessing import Pool

videoTool = VideoTools()


# Steps:
# 1: Make UI and you put reddit URL
# 2: It gets the text
scraper = RedditScraper()
post_url = "https://www.reddit.com/r/cheating_stories/comments/134cmw7/my_fianc%C3%A9_cheated_on_me_with_my_father/"
title = scraper.get_post_title(post_url)
post_text = scraper.get_post_text(post_url)
# Replace "AITA" with "Am I The Asshole" in the title
if "AITA" in title:
    title = title.replace("AITA", "Am I The Asshole")

text = title + "\n\n" + post_text[0]
# 3: Convert to audio
tts_path = videoTool.convert_text_to_speech(
    text=text, filename="audio.mp3")

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

shorts_folder = os.path.join(resources_folder, "shorts")
shorts_files = [f for f in os.listdir(
    shorts_folder) if f.endswith(('.mp4', '.avi', '.mov'))]
random_shorts = random.choice(shorts_files)
shorts_path = os.path.join(shorts_folder, random_shorts)

# 5: Export video
# video_args = video_args = [
#     (video_path, music_path, tts_path, srt_path,
#      "mainVideo.mp4", (720, 1280), font_file),
#     (shorts_path, music_path, tts_path, srt_path,
#      "youtube_shorts.mp4", (1080, 1920), font_file),
# ]

# with Pool(processes=2) as pool:
#     pool.starmap(videoTool.make_video, video_args)


# video = videoTool.make_video(video_path=video_path, music_path=music_path, tts_path=tts_path,
#                              srt_path=srt_path, output_path="mainVideo.mp4", target_resolution=(720, 1280), font=font_file)
youtube_shorts = videoTool.make_video(video_path=shorts_path, music_path=music_path,
                                      tts_path=tts_path, srt_path=srt_path, output_path="youtube_shorts.mp4", target_resolution=(1080, 1920), font=font_file)

# Youtube short resolution

# 6: Once approved, upload to youtube
