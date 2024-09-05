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
    index: str
    date_upload: str
    status: str = "On Toonkor"


class ManhwaSchema(Schema):
    title: str
    description: str = ""
    chapters: list[ChapterSchema] = []

    en_title: str = ""
    en_description: str = ""

    toonkor_url: str = ""
    mangadex_url: str = ""
    thumbnail: str = ""

    mangadex_id: str = ""
    slug: str


class ChapterModelSchema(ModelSchema):
    manhwa: ManhwaSchema | None = None

    class Meta:
        model = Chapter
        fields = ("manhwa", "index", "status")
