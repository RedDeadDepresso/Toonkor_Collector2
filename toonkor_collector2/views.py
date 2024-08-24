import re
import requests
import asyncio

from django.shortcuts import render

# Create your views here.
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Model
from django.http import HttpResponse, JsonResponse

from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.views import View

from toonkor_collector2.toonkor_api import toonkor_api
from toonkor_collector2.models import Manhwa, Chapter


# Views at the core of our applications, usually shared between multiple pages/templates
class LibraryView(View):
    def get(self, request):
        manhwas = Manhwa.objects.all().order_by('title')
        return render(request, 'library.html', {'manhwas': manhwas})
    

class ThemeView(View):
    """
    set the cookie for theme which is then used
    to assign the value for attrbute data-bs-theme in <html>
    https://getbootstrap.com/docs/5.3/customize/color-modes/#adding-theme-colors
    """
    def get(self, request):
        theme = request.GET.get('theme')
        if theme in ['dark', 'light']:
            response = HttpResponse("Theme set to: " + theme)
            response.set_cookie('theme', theme)
            return response
        else:
            return HttpResponse(-1)
        
    
class SetToonkorUrlView(View):
    def get(self, request):
        toonkor_url = request.GET.get('toonkor_url')
        response = HttpResponse("Url set to: " + toonkor_url)
        response.set_cookie('toonkor_url', toonkor_url)
        toonkor_api.base_url = toonkor_url
        return response
    

class FetchToonkorUrl(View):
    def get(self, request):
        url = toonkor_api.fetch_toonkor_url()
        toonkor_api.base_url = url
        return HttpResponse(url)


class LibrarySearch(View): 
    pass
                    

class BrowseSearch(View):
    def contains_korean(self, text):
        # Regular expression to match Korean characters
        korean_regex = re.compile('[\uac00-\ud7af]')
        
        # Search for any Korean character in the text
        return bool(korean_regex.search(text))
    
    def get_korean_title(self, query):
        base_url = "https://api.mangadex.org"

        r = requests.get(
            f"{base_url}/manga",
            params={"title": query}
        )

        for result in r.json()["data"]:
            alt_titles = result["attributes"]["altTitles"]
            for alt_title in alt_titles:
                if alt_title.get("ko"):
                    return alt_title["ko"]
                
        return query
   
    def get(self, request):
        query = request.GET.get('query')
        if not self.contains_korean(query):
            query = self.get_korean_title(query)
        return JsonResponse(toonkor_api.search(query))

    
class BrowseView(View):
    def get(self, request):
        context_dict = {}
        return render(request, 'browse.html', context=context_dict)
    

class BrowseManhwaView(View):
    def get(self, request, manhwa_slug):
        if Manhwa.objects.filter(slug=manhwa_slug):
            return redirect(reverse('toonkor_collector2:library_manhwa', kwargs={'manhwa_slug': manhwa_slug}))
        else:
            manhwa = toonkor_api.get_manga_details(manhwa_slug)
            return render(request, 'browse_manhwa.html', context={'manhwa':manhwa})
        

class AddLibrary(View):
    def get(self, request):
        manhwa_slug = request.GET.get("slug")
        manhwa_dict = toonkor_api.get_manga_details(manhwa_slug)
        manhwa, created = Manhwa.objects.get_or_create(
            title=manhwa_dict["title"],
            author=manhwa_dict["author"],
            description=manhwa_dict["description"],
            slug=manhwa_dict["slug"]
        )
        img_url = manhwa_dict['thumbnail_url']
        thumbnail_path = toonkor_api.download_thumbnail(manhwa_slug, img_url)
        if thumbnail_path is not None:
            manhwa.thumbnail = thumbnail_path
        manhwa.save()
        redirect_url = reverse('toonkor_collector2:library_manhwa', kwargs={'manhwa_slug': manhwa_slug})
        return JsonResponse({"status": "success", "redirect": redirect_url})
        

class RemoveLibrary(View):
    def get(self, request):
        manhwa_slug = request.GET.get("slug")
        Manhwa.objects.filter(slug=manhwa_slug).delete()
        redirect_url = reverse('toonkor_collector2:browse_manhwa', kwargs={'manhwa_slug': manhwa_slug})
        return JsonResponse({"status": "success", "redirect": redirect_url})    

class LibraryManhwaView(View):
    def get(self, request, manhwa_slug):
        manhwa = toonkor_api.get_manga_details(manhwa_slug)
        return render(request, 'library_manhwa.html', context={'manhwa':manhwa})
    

class DownloadChapters(View):
    async def get(self, request, manhwa_slug):
        chapters = request.GET.getlist('chapters')
        for chapter in chapters:
            await asyncio.to_thread(toonkor_api.download_chapter, manhwa_slug, chapter)
        return JsonResponse({'status': 'Download started'})
    
    
class DownloadTranslateChapters(View):
    def get(self, request, manhwa_slug, chapters):
        chapters = request.GET.getlist('chapters')
        return JsonResponse({'status': 'Download started'})