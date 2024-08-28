import re

from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views import View

from toonkor_collector2.mangadex_api import mangadex_api
from toonkor_collector2.models import Manhwa, Chapter
from toonkor_collector2.toonkor_api import toonkor_api


# Browse
class BrowseSearch(View):
    def contains_korean(self, text):
        korean_regex = re.compile('[\uac00-\ud7af]')        
        # Search for any Korean character in the text
        return bool(korean_regex.search(text))
    
    def get_display_english(self, request):
        display_english = request.GET.get("display_english", "true")
        if display_english == "true":
            return True
        else:
            return False
    
    def get(self, request):
        query = request.GET.get('query')
        display_english = self.get_display_english(request)
        if self.contains_korean(query):
            results = toonkor_api.search(query)
            if display_english:
                results = mangadex_api.multi_update_toonkor_search(results)
        else:
            results = mangadex_api.search(query)
            results = toonkor_api.multi_update_mangadex_search(results)

        return JsonResponse(results)

    
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
            mangadex_search = mangadex_api.search(manhwa['title'])["results"]
            if mangadex_search:
                manhwa.update(mangadex_search[0])
            return render(request, 'browse_manhwa.html', context={'manhwa':manhwa})
        

# Library
class AddLibrary(View):
    def get(self, request):
        manhwa_slug = request.GET.get("slug")
        manhwa_dict = toonkor_api.get_manga_details(manhwa_slug)
        mangadex_search = mangadex_api.search(manhwa_dict['title'])["results"]
        if mangadex_search:
            manhwa_dict.update(mangadex_search[0])
        manhwa, created = Manhwa.objects.get_or_create(
            title=manhwa_dict["title"],
            author=manhwa_dict["author"],
            description=manhwa_dict["description"],
            slug=manhwa_dict["slug"],
            en_title=manhwa_dict.get("en_title", ""),
            en_description=manhwa_dict.get("en_description", "")
        )
        img_url = manhwa_dict['thumbnail_url']
        thumbnail_path = toonkor_api.download_thumbnail(manhwa, img_url)
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
        mangadex_search = mangadex_api.search(manhwa['title'])["results"]
        if mangadex_search:
            manhwa.update(mangadex_search[0])
        return render(request, 'library_manhwa.html', context={'manhwa':manhwa})
    

class LibraryView(View):
    def get(self, request):
        manhwas = Manhwa.objects.all().order_by('title')
        return render(request, 'library.html', {'manhwas': manhwas})
    

# Settings
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
        

class DisplayEnglish(View):
    def get(self, request):
        display_english = request.get.GET('display_english')
        if display_english in ['true', 'false']:
            response = HttpResponse("Display in English set to: " + display_english)
            response.set_cookie('display_english', display_english)
            return response
        else:
            return HttpResponse(-1)       


class FetchToonkorUrl(View):
    def get(self, request):
        url = toonkor_api.fetch_toonkor_url()
        toonkor_api.base_url = url
        return HttpResponse(url)


class SetToonkorUrlView(View):
    def get(self, request):
        toonkor_url = request.GET.get('toonkor_url')
        response = HttpResponse("Toonkor Url set to: " + toonkor_url)
        response.set_cookie('toonkor_url', toonkor_url)
        toonkor_api.base_url = toonkor_url
        return response

