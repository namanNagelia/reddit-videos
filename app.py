import tkinter as tk
from tkinter import ttk
import threading
import os
import random

# Assuming these modules are available in your project
from src.redditScraper import RedditScraper
from src.videoTools import VideoTools


class Application:
    def __init__(self, master):
        self.master = master
        master.title("Reddit Video Generator")

        self.label = tk.Label(master, text="Enter Reddit Post URL:")
        self.label.pack(pady=5)

        self.entry = tk.Entry(master, width=50)
        self.entry.pack(pady=5)

        self.generate_button = tk.Button(
            master, text="Generate Video", command=self.start_process)
        self.generate_button.pack(pady=5)

        self.progress = ttk.Progressbar(
            master, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(pady=10)

        self.status_label = tk.Label(master, text="")
        self.status_label.pack(pady=5)

    def start_process(self):
        self.generate_button.config(state='disabled')
        self.status_label.config(text="Starting...")
        self.progress['value'] = 0
        threading.Thread(target=self.process).start()

    def update_status(self, message, progress_value):
        self.master.after(0, lambda: self._update_ui(message, progress_value))

    def _update_ui(self, message, progress_value):
        self.status_label.config(text=message)
        self.progress['value'] = progress_value

    def process(self):
        try:
            videoTool = VideoTools()

            # Update progress
            self.update_status("Fetching Reddit Post...", 10)

            # Get Reddit URL from entry
            post_url = self.entry.get()

            # Use RedditScraper to get post text
            scraper = RedditScraper()
            post_text = scraper.get_post_text(post_url)

            # Update progress
            self.update_status("Converting Text to Speech...", 30)

            # Convert to audio
            # text = videoTool.makeBetterScript(post_text[0])
            tts_path = videoTool.convert_text_to_speech(
                text=post_text[0], filename="audio.mp3")

            # Update progress
            self.update_status("Selecting Random Video and Music...", 40)

            # Randomly choose a video and music
            resources_folder = os.path.join(os.getcwd(), "resources")
            video_folder = os.path.join(resources_folder, "videos")
            music_folder = os.path.join(resources_folder, "music")
            video_files = [f for f in os.listdir(
                video_folder) if f.endswith(('.mp4', '.avi', '.mov'))]
            random_video = random.choice(video_files)
            video_path = os.path.join(video_folder, random_video)
            font_file = os.path.join(resources_folder, "Salsa.ttf")
            print(f"Font file used: {font_file}")

            # Get a random music file
            music_files = [f for f in os.listdir(
                music_folder) if f.endswith(('.mp3', '.wav'))]
            random_music = random.choice(music_files)
            music_path = os.path.join(music_folder, random_music)

            # Update progress
            self.update_status("Generating Subtitles...", 50)

            # Generate subtitles
            srt_path = videoTool.generate_srt(tts_path)

            # Update progress
            self.update_status("Creating Video...", 70)

            # Export video
            video = videoTool.make_video(
                video_path=video_path,
                music_path=music_path,
                tts_path=tts_path,
                srt_path=srt_path,
                output_path="output.mp4",
                target_resolution=(720, 1280),
                font=font_file
            )

            # Update progress
            self.update_status("Uploading to YouTube...", 90)

            # Code to upload to YouTube
            # You need to implement the upload_to_youtube method in your VideoTools class
            # Make sure to handle authentication and API setup

            # upload_result = videoTool.upload_to_youtube(
            #     video_file="output.mp4",
            #     title="Reddit Video",
            #     description=post_text[0]
            # )

            # Update progress
            self.update_status("Upload Completed!", 100)

            # Re-enable the button
            self.master.after(
                0, lambda: self.generate_button.config(state='normal'))

            # Notify the user
            # tk.messagebox.showinfo("Success", "Video uploaded successfully!")

        except Exception as e:
            self.master.after(
                0, lambda: self.status_label.config(text=f"Error: {e}"))
            self.master.after(
                0, lambda: self.generate_button.config(state='normal'))
            # tk.messagebox.showerror("Error", f"An error occurred: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()


# 1. Upload it to youtube
# 2: Export it to shorts video as well
# 3: Use GPT to generate title, hashtags
