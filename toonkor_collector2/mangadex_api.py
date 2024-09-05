import requests
import concurrent.futures
from toonkor_collector2.schemas import ManhwaSchema


class MangadexAPI:
    def __init__(self):
        self.client = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.base_url = "https://api.mangadex.org"
        self.cached_manhwas = {}

    def search(self, query: str) -> list[ManhwaSchema]:
        output = []
        if query in self.cached_manhwas:
            output.append(self.cached_manhwas[query])
            return output

        response = self.client.get(
            f"{self.base_url}/manga", params={"title": query}, headers=self.headers
        )

        for result in response.json().get("data", []):
            for alt_title in result["attributes"].get("altTitles", []):
                if "ko" in alt_title:
                    korean_title = alt_title["ko"]
                    temp = {
                        "title": korean_title,
                        "en_title": result["attributes"]["title"].get("en", ""),
                        "en_description": result["attributes"]["description"].get(
                            "en", ""
                        ),
                    }
                    self.cached_manhwas[korean_title] = temp
                    output.append(temp)
        return output

    def update_toonkor_search(self, toonkor_search: dict) -> ManhwaSchema:
        korean_title = toonkor_search["title"]
        if korean_title in self.cached_manhwas:
            toonkor_search.update(self.cached_manhwas[korean_title])

        else:
            response = self.client.get(
                f"{self.base_url}/manga",
                params={"title": korean_title},
                headers=self.headers,
            )

            for result in response.json().get("data", []):
                for alt_title in result["attributes"].get("altTitles", []):
                    if alt_title.get("ko") == korean_title:
                        temp = {
                            "en_title": result["attributes"].get("title", ""),
                            "en_description": result["attributes"].get(
                                "description", ""
                            ),
                        }
                        self.cached_manhwas[korean_title] = temp
                        toonkor_search.update(temp)
        return toonkor_search

    def multi_update_toonkor_search(
        self, toonkor_results: list[ManhwaSchema]
    ) -> list[ManhwaSchema]:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.translate_toonkor_search, toonkor_search)
                for toonkor_search in toonkor_results
            ]
            return [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]


mangadex_api = MangadexAPI()
