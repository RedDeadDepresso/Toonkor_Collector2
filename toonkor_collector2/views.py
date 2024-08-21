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


# Views at the core of our applications, usually shared between multiple pages/templates
class LibraryView(View):
    def get(self, request):
        context_dict = {}
        return render(request, 'library.html', context=context_dict)

class BrowseView(View):
    def get(self, request):
        context_dict = {}
        return render(request, 'library.html', context=context_dict)
    

class SettingsView(View):
    def get(self, request):
        context_dict = {}
        return render(request, 'library.html', context=context_dict)
    

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