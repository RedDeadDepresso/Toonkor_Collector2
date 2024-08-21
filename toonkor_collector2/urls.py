from django.urls import path
from toonkor_collector2 import views

app_name = 'toonkor_collector2'

urlpatterns = [
    # base urls
    path('library/', views.LibraryView.as_view(), name='library'),
    path('browse/', views.BrowseView.as_view(), name='browse'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
]