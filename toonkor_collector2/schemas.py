from ninja import ModelSchema, Schema
from toonkor_collector2.models import Manhwa, Chapter


class ManhwaModelSchema(ModelSchema):
    class Meta:
        model = Manhwa
        fields = (
            "title",
            "description",
            "en_title",
            "en_description",
            "thumbnail",
            "slug",
        )


class ChapterSchema(Schema):
    index: str | int
    date_upload: str = ""
    status: str


class ManhwaSchema(Schema):
    title: str
    description: str = ""
    chapters: list[ChapterSchema] = []

    en_title: str = ""
    en_description: str = ""

    thumbnail: str = ""
    in_library: bool = False

    mangadex_id: str = ""
    slug: str


class ChapterModelSchema(ModelSchema):
    manhwa: ManhwaSchema | None = None

    class Meta:
        model = Chapter
        fields = ("manhwa", "index", "status")


class SetToonkorUrlSchema(Schema):
    url: str


class ResponseToonkorUrlSchema(Schema):
    url: str
    error: str