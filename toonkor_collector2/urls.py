from django.urls import path
from toonkor_collector2 import views

app_name = 'toonkor_collector2'

urlpatterns = [
    # base urls
    path('library/', views.LibraryView.as_view(), name='library'),
    path('browse/', views.BrowseView.as_view(), name='browse'),
    path('browse_search/', views.BrowseSearch.as_view(), name='browse_search'),
    path('theme/', views.ThemeView.as_view(), name='theme'),
    path('fetch_toonkor_url/', views.FetchToonkorUrl.as_view(), name='fetch_toonkor_url')
]