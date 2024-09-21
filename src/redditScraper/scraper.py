import requests
from bs4 import BeautifulSoup


class RedditScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    def get_post_text(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            post_title = soup.find('h1', {'slot': 'title'})
            post_content = soup.find(
                'div', {'class': 'text-neutral-content', 'slot': 'text-body'})

            if post_content:
                post_title = post_title.get_text(
                    strip=True) if post_title else ""
                text_elements = post_content.find_all(
                    ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                post_text = '\n\n'.join(
                    [elem.get_text(strip=True) for elem in text_elements])

                # Remove newlines and quotes from the post text
                cleaned_post_text = post_text.replace(
                    '\n', '').replace('"', '').replace("'", "")

                return (cleaned_post_text.strip(), post_title.strip())
            else:
                return "Post content not found."

        except requests.RequestException as e:
            return f"Error fetching the post: {str(e)}"
