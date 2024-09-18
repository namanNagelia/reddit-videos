from src.redditScraper import RedditScraper
from src.videoTools import VideoTools
# Example usage
scraper = RedditScraper()
post_url = "https://www.reddit.com/r/AmItheAsshole/comments/1evge2u/aita_for_telling_my_coworker_that_i_didnt_enjoy/"
post_text = scraper.get_post_text(post_url)
print(post_text)

videoTool = VideoTools()
