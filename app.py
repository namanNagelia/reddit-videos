import tkinter as tk
from tkinter import ttk, messagebox
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
        threading.Thread(target=self.process, daemon=True).start()

    def update_status(self, message, progress_value):
        """Safely update the UI from any thread"""
        try:
            self.master.after(0, self._update_ui, message, progress_value)
        except Exception as e:
            print(f"Error updating status: {e}")

    def _update_ui(self, message, progress_value):
        """Update UI elements"""
        try:
            self.status_label.config(text=message)
            self.progress['value'] = progress_value
        except Exception as e:
            print(f"Error in _update_ui: {e}")

    def handle_error(self, error_message):
        """Safely handle errors and update UI"""
        print(f"Error: {error_message}")
        def _handle_error():
            self.status_label.config(text=f"Error: {error_message}")
            self.generate_button.config(state='normal')
            messagebox.showerror("Error", f"An error occurred: {error_message}")

        self.master.after(0, _handle_error)

    def process(self):
        """Main processing function"""
        try:
            videoTool = VideoTools()

            # Input validation
            post_url = self.entry.get().strip()
            if not post_url:
                raise ValueError("Please enter a Reddit post URL")

            # Fetch Reddit post
            self.update_status("Fetching Reddit Post...", 10)
            scraper = RedditScraper()
            post_text = scraper.get_post_text(post_url)

            if not post_text or not post_text[0]:
                raise ValueError("Failed to fetch post content")

            # Convert to audio
            self.update_status("Converting Text to Speech...", 30)
            tts_path = videoTool.convert_text_to_speech(
                text=post_text[0], filename="audio.mp3")

            # Select media files
            self.update_status("Selecting Random Video and Music...", 40)
            resources_folder = os.path.join(os.getcwd(), "resources")
            video_folder = os.path.join(resources_folder, "videos")
            music_folder = os.path.join(resources_folder, "music")

            # Validate resource directories
            if not all(os.path.exists(path) for path in [video_folder, music_folder]):
                raise FileNotFoundError("Required resource folders not found")

            # Get random video
            video_files = [f for f in os.listdir(video_folder)
                           if f.endswith(('.mp4', '.avi', '.mov'))]
            if not video_files:
                raise FileNotFoundError("No video files found in resources")

            random_video = random.choice(video_files)
            video_path = os.path.join(video_folder, random_video)

            # Get font file
            font_file = os.path.join(resources_folder, "Mont.ttf")
            if not os.path.exists(font_file):
                raise FileNotFoundError("Required font file not found")

            # Get random music
            music_files = [f for f in os.listdir(music_folder)
                           if f.endswith(('.mp3', '.wav'))]
            if not music_files:
                raise FileNotFoundError("No music files found in resources")

            random_music = random.choice(music_files)
            music_path = os.path.join(music_folder, random_music)

            # Generate subtitles
            self.update_status("Generating Subtitles...", 50)
            srt_path = videoTool.generate_srt(tts_path)

            # Create video
            self.update_status("Creating Video...", 70)
            video = videoTool.make_video(
                video_path=video_path,
                music_path=music_path,
                tts_path=tts_path,
                srt_path=srt_path,
                output_path="output.mp4",
                target_resolution=(720, 1280),
                font=font_file
            )

            # Final steps
            self.update_status("Process Completed!", 100)
            self.master.after(0, lambda: self.generate_button.config(state='normal'))
            self.master.after(0, lambda: messagebox.showinfo("Success",
                                                             "Video generated successfully!"))

        except Exception as error:
            self.handle_error(str(error))


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()