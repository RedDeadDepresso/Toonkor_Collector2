import base64
import re
from datetime import datetime
from typing import List, Optional
from bs4 import BeautifulSoup
import requests

class ToonkorAPI:
    def __init__(self, base_url: str = "https://toonkor429.com"):
        self.name = "Toonkor"
        self.lang = "ko"
        self.supports_latest = True
        self.base_url = base_url
        self.client = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    # Popular

    webtoons_request_path = "/%EC%9B%B9%ED%88%B0"

    def popular_manga_request(self, page: int) -> str:
        return self.base_url + self.webtoons_request_path

    def popular_manga_selector(self) -> str:
        return "div.section-item-inner"

    def popular_manga_from_element(self, element) -> dict:
        title_element = element.select_one("div.section-item-title a h3")
        url = element.select_one("div.section-item-title a")['href']
        thumbnail_url = element.select_one("img")['src']

        return {
            "title": title_element.text,
            "url": url,
            "thumbnail_url": thumbnail_url
        }

    def popular_manga_next_page_selector(self) -> Optional[str]:
        return None

    # Latest

    latest_request_modifier = "?fil=%EC%B5%9C%EC%8B%A0"

    def latest_updates_request(self, page: int) -> str:
        return self.base_url + self.webtoons_request_path + self.latest_request_modifier

    def latest_updates_selector(self) -> str:
        return self.popular_manga_selector()

    def latest_updates_from_element(self, element) -> dict:
        return self.popular_manga_from_element(element)

    def latest_updates_next_page_selector(self) -> Optional[str]:
        return self.popular_manga_next_page_selector()

    # Search

    def search_manga_request(self, page: int, query: str, filters: dict) -> str:
        filter_list = filters or self.get_filter_list()

        # Webtoons, Manga, or Hentai
        type_filter = filter_list.get('type', '')
        # Popular, Latest, or Completed
        sort_filter = filter_list.get('sort', '')

        if query:
            request_path = f"/bbs/search.php?sfl=wr_subject%7C%7Cwr_content&stx={query}"
        elif type_filter == 'Hentai' and sort_filter == 'Completed':
            request_path = type_filter
        else:
            request_path = type_filter + sort_filter

        return self.base_url + request_path

    def search_manga_selector(self) -> str:
        return self.popular_manga_selector()

    def search_manga_from_element(self, element) -> dict:
        return self.popular_manga_from_element(element)

    def search_manga_next_page_selector(self) -> Optional[str]:
        return self.popular_manga_next_page_selector()

    # Details

    def manga_details_parse(self, document) -> dict:
        title = document.select_one("td.bt_title").text
        author = document.select_one("td.bt_label span.bt_data").text
        description = document.select_one("td.bt_over").text
        thumbnail_url = document.select_one("td.bt_thumb img")['src']

        return {
            "title": title,
            "author": author,
            "description": description,
            "thumbnail_url": thumbnail_url
        }

    # Chapters

    def chapter_list_selector(self) -> str:
        return "table.web_list tr:has(td.content__title)"

    def chapter_from_element(self, element) -> dict:
        url = element.select_one("td.content__title")['data-role']
        name = element.select_one("td.content__title").text
        date_upload = self.to_date(element.select_one("td.episode__index").text)

        return {
            "url": url,
            "name": name,
            "date_upload": date_upload
        }

    @staticmethod
    def to_date(date_str: str) -> int:
        date_format = "%Y-%m-%d"
        return int(datetime.strptime(date_str, date_format).timestamp())

    # Pages

    page_list_regex = re.compile(r'src="([^"]*)"')

    def page_list_parse(self, document) -> List[dict]:
        encoded = re.search(r"toon_img\s*=\s*'(.*?)'", document.text).group(1)
        if not encoded:
            raise Exception("toon_img script not found")

        decoded = base64.b64decode(encoded).decode('utf-8')
        return [{"index": i, "url": url if url.startswith("http") else self.base_url + url}
                for i, url in enumerate(self.page_list_regex.findall(decoded))]

    def image_url_parse(self, document) -> str:
        raise NotImplementedError("imageUrlParse is not supported.")

    # Filters

    def get_filter_list(self) -> dict:
        return {
            "type": self.get_type_list(),
            "sort": self.get_sort_list()
        }

    def get_type_list(self) -> dict:
        return {
            "Webtoons": self.webtoons_request_path,
            "Manga": "/%EB%8B%A8%ED%96%89%EB%B3%B8",
            "Hentai": "/%EB%A7%9D%EA%B0%80",
        }

    def get_sort_list(self) -> dict:
        return {
            "Popular": "",
            "Latest": self.latest_request_modifier,
            "Completed": "/%EC%99%84%EA%B2%B0",
        }

    # Preferences

    def setup_preference_screen(self, screen):
        base_url_pref = {
            "key": "Override BaseUrl",
            "title": "Override BaseUrl",
            "summary": "Override default domain with a different one",
            "default": self.base_url
        }
        screen.add(base_url_pref)

    def search(self, query):
        filters = {
            "type": "/%EB%8B%A8%ED%96%89%EB%B3%B8",  # Optional: specify type (e.g., "Manga")
            "sort": "?fil=%EC%B5%9C%EC%8B%A0"       # Optional: specify sorting (e.g., "Latest")
        }
        search_url = self.search_manga_request(1, query, filters)

        response = self.client.get(search_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Parse the search results
        output = {"results":[]}
        for element in soup.select(self.search_manga_selector()):
            manga = self.search_manga_from_element(element)
            output["results"].append(manga)
        
        return output