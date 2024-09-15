from ninja import Schema
from typing import Literal


class ChapterSchema(Schema):
    index: str | int
    date_upload: str = ""
    status: str
    toonkor_id: str = ''


class ManhwaSchema(Schema):
    title: str
    description: str = ""
    chapters: list[ChapterSchema] = []

    en_title: str = ""
    en_description: str = ""

    thumbnail: str = ""
    in_library: bool = False

    mangadex_id: str = ""
    toonkor_id: str


class ChapterPaginationSchema(Schema):
    manhwa_id: str
    manhwa_title: str
    manhwa_en_title: str
    prev_chapter: ChapterSchema | None = None
    current_chapter: ChapterSchema
    next_chapter: ChapterSchema | None = None
    pages: list[str] 


class SetToonkorUrlSchema(Schema):
    url: str


class ResponseToonkorUrlSchema(Schema):
    url: str
    error: str


class DownloadTranslateSchema(Schema):
    task: Literal["download", "download_translate"]
    toonkor_id: str
    chapters: list[int]