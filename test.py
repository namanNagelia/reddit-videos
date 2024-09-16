from src.redditScraper import RedditScraper
# Example usage
scraper = RedditScraper()
post_url = "https://www.reddit.com/r/AmItheAsshole/comments/1fi3y87/aita_for_telling_my_wife_that_she_needs_to_get/"
post_text = scraper.get_post_text(post_url)
print(post_text)
