from ninja import ModelSchema
from toonkor_collector2.models import Manhwa, Chapter


class ManhwaSchema(ModelSchema):
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


class ChapterSchema(ModelSchema):
    manhwa: ManhwaSchema | None = None

    class Meta:
        model = Chapter
        fields = ('manhwa', 'index', 'translated')

