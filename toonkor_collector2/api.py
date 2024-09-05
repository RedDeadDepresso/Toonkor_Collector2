from ninja import NinjaAPI
from django.forms.models import model_to_dict
from toonkor_collector2.models import Manhwa
from toonkor_collector2.schemas import ManhwaModelSchema, ManhwaSchema
from toonkor_collector2.mangadex_api import mangadex_api
from toonkor_collector2.toonkor_api import toonkor_api

api = NinjaAPI()
cached_manhwas = {}


def search_database(manhwa_slug: str) -> Manhwa | None:
    """
    Search for a Manhwa in the database by slug.

    :param manhwa_slug: The slug of the Manhwa to search for.
    :return: A Manhwa object if found, otherwise None.
    """
    try:
        return Manhwa.objects.get(slug=manhwa_slug)
    except Manhwa.DoesNotExist:
        return None
    

def update_manhwa_from_mangadex(manhwa: dict, manhwa_db: Manhwa):
    """
    Update the Manhwa details using Mangadex API if necessary.

    :param manhwa: The Manhwa data dictionary to update.
    :param manhwa_db: The database instance of the Manhwa to update.
    """
    mangadex_search = mangadex_api.search(manhwa["title"])
    if mangadex_search:
        mangadex_data = mangadex_search[0]
        manhwa.update(mangadex_data)
    if manhwa_db:
        manhwa_db.en_title = manhwa.get("en_title", "")
        manhwa_db.en_description = manhwa.get("en_description", "")
        manhwa_db.mangadex_id = manhwa.get("mangadex_id", "")
        manhwa_db.save()
    if mangadex_search or manhwa_db:
        manhwa["mangadex_url"] = "https://mangadex.org/title/" + manhwa["mangadex_id"]


def search(manhwa_slug: str) -> dict:
    """
    Search for a Manhwa using the cache, database, and Toonkor API.

    :param manhwa_slug: The slug of the Manhwa to search for.
    :return: A dictionary containing the Manhwa details.
    """
    if manhwa_slug in cached_manhwas:
        return cached_manhwas[manhwa_slug]

    manhwa = {}
    manhwa_db = search_database(manhwa_slug)

    if manhwa_db:
        manhwa = model_to_dict(manhwa_db)

    try:
        # Update manhwa details from Toonkor API
        manhwa.update(toonkor_api.get_manga_details(manhwa_slug))

        # If English title or description is missing, update from Mangadex API
        if not all([manhwa.get("en_title"), manhwa.get("en_description"), manhwa.get("mangadex_id")]):
            update_manhwa_from_mangadex(manhwa, manhwa_db)

        cached_manhwas[manhwa_slug] = manhwa
    except Exception as e:
        print(f"Error searching for manhwa: {e}")

    return manhwa


@api.get("/library", response=list[ManhwaSchema])
def library(request):
    """
    Retrieve all Manhwa in the library.
    """
    return Manhwa.objects.all()


@api.get(path="/library/manhwa", response=ManhwaSchema)
def library_manhwa(request, manhwa_slug: str):
    """
    Retrieve a specific Manhwa by slug from the library.
    """
    return search(manhwa_slug)


@api.get("/browse/search", response=list[ManhwaSchema])
def browse(request, query: str):
    """
    Search for Manhwa using Mangadex API and update with Toonkor API.
    """
    results = mangadex_api.search(query)
    return toonkor_api.multi_update_mangadex_search(results)


@api.get("/browse/manhwa/", response=ManhwaSchema)
def browse_manhwa(request, manhwa_slug: str):
    """
    Browse and retrieve a specific Manhwa by slug.
    """
    return search(manhwa_slug)
