from django.urls import path
from toonkor_collector2 import views

app_name = 'toonkor_collector2'

urlpatterns = [
    # base urls
    path('library/', views.LibraryView.as_view(), name='library'),
    path('browse/', views.BrowseView.as_view(), name='browse'),
    path('browse_search/', views.BrowseSearch.as_view(), name='browse_search'),
    path('browse_manhwa/<str:manhwa_slug>/', views.BrowseManhwaView.as_view(), name='browse_manhwa'),
    path('theme/', views.ThemeView.as_view(), name='theme'),
    path('fetch_toonkor_url/', views.FetchToonkorUrl.as_view(), name='fetch_toonkor_url'),
    path('add_library/', views.AddLibrary.as_view(), name="add_library"),
    path('remove_library/', views.RemoveLibrary.as_view(), name="remove_library"),
    path('library_manhwa/<str:manhwa_slug>/', views.LibraryManhwaView.as_view(), name='library_manhwa'),
    path('download/<str:manhwa_slug>/', views.DownloadChapters.as_view(), name='download'),
    path('download_translate/<str:manhwa_slug>/', views.DownloadTranslateChapters.as_view(), name='download_translate'),
]