from django.urls import path
from toonkor_collector2 import views

app_name = "toonkor_collector2"

urlpatterns = [
    # browse urls
    path("browse/", views.BrowseView.as_view(), name="browse"),
    path(
        "browse_manhwa/<str:manhwa_slug>/",
        views.BrowseManhwaView.as_view(),
        name="browse_manhwa",
    ),
    path("browse_search/", views.BrowseSearch.as_view(), name="browse_search"),
    # library urls
    path("add_library/", views.AddLibrary.as_view(), name="add_library"),
    path("library/", views.LibraryView.as_view(), name="library"),
    path(
        "library_manhwa/<str:manhwa_slug>/",
        views.LibraryManhwaView.as_view(),
        name="library_manhwa",
    ),
    path("remove_library/", views.RemoveLibrary.as_view(), name="remove_library"),
    # settings urls
    path("theme/", views.ThemeView.as_view(), name="theme"),
    path(
        "fetch_toonkor_url/", views.FetchToonkorUrl.as_view(), name="fetch_toonkor_url"
    ),
]
