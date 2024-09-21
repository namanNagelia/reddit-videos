from src.redditScraper import RedditScraper
from src.videoTools import VideoTools
# Example usage

videoTool = VideoTools()


# Steps:
# 1: Make UI and you put reddit URL
# 2: It gets the text
scraper = RedditScraper()
post_url = "https://www.reddit.com/r/AmItheAsshole/comments/1evge2u/aita_for_telling_my_coworker_that_i_didnt_enjoy/"
post_text = scraper.get_post_text(post_url)
print(post_text[0])

# 3: Convert to audio
path = videoTool.convert_text_to_speech(
    text=post_text[0], filename="audio")
print(path)
# 4: Randomly choose a minecraft/SS video and concat
# 5: Export video
# 6: Once approved, upload to youtube
