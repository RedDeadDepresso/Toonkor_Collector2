import re
from ninja import NinjaAPI
from django.forms.models import model_to_dict
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from toonkor_collector2.models import Manhwa, Chapter
from toonkor_collector2.schemas import ManhwaModelSchema, ManhwaSchema, SetToonkorUrlSchema, ResponseToonkorUrlSchema, ChapterSchema
from toonkor_collector2.mangadex_api import mangadex_api
from toonkor_collector2.toonkor_api import toonkor_api


api = NinjaAPI()
cached_manhwas = {}


def is_valid_url(url):
    validator = URLValidator()
    try:
        validator(url)
        return True
    except ValidationError:
        return False


def exract_mangadex_url(url):
    pattern = r'^https?://(www\.)?mangadex\.org/title/([a-f0-9-]+)/?.*$'
    match = re.match(pattern, url)
    return match.group(2) if match else None


def extract_toonkor_url(url):
    # Updated pattern to match and capture the full path after the domain
    pattern = r'^https?://(www\.)?toonkor\d{3}\.com(/[\w%\-가-힣/]+).*$'
    match = re.match(pattern, url)    
    return match.group(2) if match else None


def search_database(manhwa_slug: str) -> Manhwa | None:
    """Search for a Manhwa in the database by slug."""
    try:
        manhwa = Manhwa.objects.get(slug=manhwa_slug)
        return manhwa
    except Exception as e:
        return None


def database_chapters(manhwa: Manhwa) -> list:
    chapters_db_dict = dict()
    try:
        chapters_db = Chapter.objects.filter(manhwa=manhwa)
        chapters_db_dict = {str(chapter_db.index): model_to_dict(chapter_db) for chapter_db in chapters_db}
    except:
        pass
    return chapters_db_dict
    
    
def database_chapters_to_list(manhwa: Manhwa, chapters_db: dict):
    end = manhwa.chapters_num + 1
    for index in range(1, end):
        str_index = str(index)
        if str_index not in chapters_db:
            chapters_db[str_index] = {'index': index, 'status': 'On Toonkor'}
    chapters_list = list(chapters_db.values())
    chapters_list.sort(key=lambda x: x["index"], reverse=True)
    return chapters_list


def update_manhwa_from_mangadex(manhwa: dict, manhwa_db: Manhwa | None):
    """Update Manhwa details using Mangadex API if necessary."""
    mangadex_search = mangadex_api.search(manhwa.get("title"))
    if mangadex_search:
        mangadex_data = mangadex_search[0]
        manhwa.update(mangadex_data)
        
        if manhwa_db:
            # Update database fields
            manhwa_db.en_title = manhwa.get("en_title", "")
            manhwa_db.en_description = manhwa.get("en_description", "")
            manhwa_db.mangadex_id = manhwa.get("mangadex_id", "")
            manhwa_db.save()
        

def get_manhwa_details(manhwa_slug: str) -> dict:
    """Get Manhwa details from Toonkor API and update using Mangadex if needed."""
    manhwa = {}
    manhwa_db = search_database(manhwa_slug)

    if manhwa_db is not None:
        manhwa = model_to_dict(manhwa_db)
        manhwa["chapters"] = database_chapters(manhwa_db)
        manhwa["in_library"] = True

    try:
        toonkor_details = toonkor_api.get_manga_details(manhwa_slug, manhwa.get('chapters', dict()))
        manhwa.update(toonkor_details)
        toonkor_chapters_num = len(manhwa['chapters'])
        if manhwa_db is not None and toonkor_chapters_num > manhwa_db.chapters_num:
            manhwa_db.chapters_num = toonkor_chapters_num
            manhwa_db.save()
        # Update from Mangadex if essential fields are missing
        if not all([manhwa.get("en_title"), manhwa.get("en_description"), manhwa.get("mangadex_id")]):
            update_manhwa_from_mangadex(manhwa, manhwa_db)
    except Exception as e:
        print(f"Error fetching details from Toonkor: {e}")

    if isinstance(manhwa["chapters"], dict):
        manhwa['chapters'] = database_chapters_to_list(manhwa_db, manhwa['chapters'])
    return manhwa


def add_manhwa_to_library(manhwa_slug: str) -> bool:
    """Add a Manhwa to the library from Toonkor and Mangadex details."""
    try:
        manhwa_dict = cached_manhwas.get(manhwa_slug, toonkor_api.get_manga_details(manhwa_slug))
        mangadex_search = mangadex_api.search(manhwa_dict.get('title', ''))
        
        if mangadex_search:
            manhwa_dict.update(mangadex_search[0])

        # Filter out keys not in the Manhwa model fields
        model_fields = {field.name for field in Manhwa._meta.get_fields()}
        filtered_data = {key: value for key, value in manhwa_dict.items() if key in model_fields}
        manhwa, _ = Manhwa.objects.get_or_create(**filtered_data)

        # Download and set the thumbnail
        img_url = manhwa_dict.get('thumbnail', '')
        thumbnail_path = toonkor_api.download_thumbnail(manhwa, img_url)
        if thumbnail_path:
            manhwa.thumbnail = thumbnail_path
        manhwa.save()

        # Update cache
        manhwa_dict["in_library"] = True
        manhwa_dict["thumbnail"] = thumbnail_path
        cached_manhwas[manhwa_slug] = manhwa_dict
        return True
    except Exception as e:
        print(f"Error adding Manhwa to library: {e}")
        return False


def remove_manhwa_from_library(manhwa_slug: str) -> bool:
    """Remove a Manhwa from the library and update the cache."""
    try:
        Manhwa.objects.filter(slug=manhwa_slug).delete()
        if manhwa_slug in cached_manhwas:
            cached_manhwas[manhwa_slug]["in_library"] = False
        return True
    except Exception as e:
        print(f"Error removing Manhwa from library: {e}")
        return False


@api.get("/library", response=list[ManhwaSchema])
def library(request):
    """Retrieve all Manhwa in the library."""
    return Manhwa.objects.all()


@api.get("/manhwa", response=ManhwaSchema)
def manhwa(request, manhwa_slug: str):
    """Retrieve a specific Manhwa by slug from the library."""
    if manhwa_slug in cached_manhwas:
        return cached_manhwas[manhwa_slug]

    manhwa = get_manhwa_details(manhwa_slug)
    cached_manhwas[manhwa_slug] = manhwa
    return manhwa


@api.get("/browse/search")
def browse(request, query: str):
    """Search for Manhwa using Mangadex API and update with Toonkor API."""
    try:
        if is_valid_url(query):
            toonkor_slug = extract_toonkor_url(query)
            mangadex_id = exract_mangadex_url(query)
            if toonkor_slug is not None:
                return [get_manhwa_details(toonkor_slug)]
            elif mangadex_id is not None:
                results = mangadex_api.search_by_id(mangadex_id)
                return toonkor_api.multi_update_mangadex_search(results)

        results = mangadex_api.search(query)
        return toonkor_api.multi_update_mangadex_search(results)
    except Exception as e:
        print(f"Error browsing Manhwa: {e}")
        return []


@api.get("/add_library", response=bool)
def add_library(request, manhwa_slug: str):
    """Add a Manhwa to the library."""
    return add_manhwa_to_library(manhwa_slug)


@api.get("/remove_library", response=bool)
def remove_library(request, manhwa_slug: str):
    """Remove a Manhwa from the library."""
    return remove_manhwa_from_library(manhwa_slug)


@api.get("/fetch_toonkor_url", response=ResponseToonkorUrlSchema)
def fetch_toonkor_url(request):
    try:
        url = toonkor_api.fetch_toonkor_url()
        if toonkor_api.base_url == url:
            return {'url': url, 'error': ''}
        elif toonkor_api.set_toonkor_url(url):
            cached_manhwas.clear()
            return {'url': url, 'error': ''}
        else:
            return {'url': '', 'error': 'Invalid Url'}
    except Exception as e:
        return {'url': '', 'error': str(e)}


@api.post("/set_toonkor_url", response=ResponseToonkorUrlSchema)
def set_toonkor_url(request, data: SetToonkorUrlSchema):
    try:
        if toonkor_api == data.url:
            return {'url': data.url, 'error': ''}     
        elif toonkor_api.set_toonkor_url(data.url):
            cached_manhwas.clear()
            return {'url': data.url, 'error': ''}
        else:
            return {'url': '', 'error': 'Invalid Url'}
    except Exception as e:
        return {'url': '', 'error': str(e)}