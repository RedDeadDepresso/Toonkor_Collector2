from ninja import ModelSchema, Schema
from toonkor_collector2.models import Manhwa, Chapter


class ManhwaModelSchema(ModelSchema):
    class Meta:
        model = Manhwa
        fields = (
            'title', 
            'author',
            'description',

            'en_title',
            'en_author',
            'en_description',

            'thumbnail',
            'slug'
        )


class ChapterSchema(Schema):
    index: str
    date_upload: str
    status: str = "On Toonkor"


class ManhwaSchema(Schema):
    title: str
    author: str = ''
    description: str = ''
    thumbnail: str
    chapters: list[ChapterSchema] = []

    en_title: str | None = ''
    en_author: str = ''
    en_description: str = ''

    thumbnail: str = ''
    slug: str


class ChapterModelSchema(ModelSchema):
    manhwa: ManhwaSchema | None = None

    class Meta:
        model = Chapter
        fields = ('manhwa', 'index', 'status')

