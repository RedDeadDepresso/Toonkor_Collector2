from django.db import models
from toonkor_collector2.toonkor_api import toonkor_api
from functools import cached_property


# Create your models here.
class Manhwa(models.Model):
    title = models.CharField(max_length=512)
    description = models.TextField(blank=True)

    en_title = models.CharField(max_length=512, blank=True)
    en_description = models.TextField(blank=True)

    thumbnail = models.ImageField(blank=True)
    mangadex_id = models.CharField(max_length=512, blank=True)
    toonkor_id = models.SlugField(default="")

    def __str__(self) -> str:
        return self.title

    @cached_property
    def media_path(self) -> str:
        return f"/media/{toonkor_api.encode_name(self.toonkor_id)}"
    
    @cached_property
    def path(self) -> str:
        return f"toonkor_collector2{self.media_path}"


class StatusChoices(models.TextChoices):
    ON_TOONKOR = "On Toonkor", "On Toonkor"
    DOWNLOADED = "Downloaded", "Downloaded"
    TRANSLATED = "Translated", "Translated"


class Chapter(models.Model):
    index = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ON_TOONKOR,
    )
    toonkor_id = models.SlugField(default="")
    date_upload = models.CharField(max_length=512, blank=True)
    manhwa_id = models.CharField(max_length=512)

    def __str__(self) -> str:
        return f"{self.manhwa_id} - Chapter {self.index}"
    
    @cached_property
    def manhwa_media_path(self) -> str:
        return f"/media/{toonkor_api.encode_name(self.manhwa_id)}"
    
    @cached_property
    def manhwa_path(self) -> str:
        return f"toonkor_collector2{self.manhwa_media_path}"

    @cached_property
    def downloaded_path(self) -> str:
        return f"{self.manhwa_path}/{self.index}"

    @cached_property
    def translated_path(self) -> str:
        return f"{self.manhwa_path}/{self.index}/translated"
    
    @cached_property
    def media_downloaded_path(self) -> str:
        return f"{self.manhwa_media_path}/{self.index}"

    @cached_property
    def media_translated_path(self) -> str:
        return f"{self.manhwa_media_path}/{self.index}/translated"
