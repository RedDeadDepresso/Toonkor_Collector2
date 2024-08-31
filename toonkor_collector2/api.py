from django.shortcuts import get_object_or_404
from ninja import NinjaAPI
from toonkor_collector2.models import Manhwa, Chapter
from toonkor_collector2.schemas import ManhwaSchema, ChapterSchema


app = NinjaAPI()

@app.get("library/", response=list[ManhwaSchema])
def get_library(request):
    return Manhwa.objects.all()

@app.get("library/{manhwa_slug}", response=ManhwaSchema)
def get_library_manhwa(request, manhwa_slug: str):
    return Manhwa.objects.all(slug=manhwa_slug)

@app.get("browse/search/", response=dict)
def browse_search(request, query: str):
    return Manhwa.objects.all()

@app.get("library/{manhwa_slug}", response=ManhwaSchema)
def get_library_manhwa(request, manhwa_slug: str):
    return Manhwa.objects.all(slug=manhwa_slug)

