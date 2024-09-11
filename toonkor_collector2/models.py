import base64
from django.db import models


# Create your models here.
class Manhwa(models.Model):
    title = models.CharField(max_length=512)
    description = models.TextField(blank=True)
    chapters_num = models.IntegerField(default=0)

    en_title = models.CharField(max_length=512, blank=True)
    en_description = models.TextField(blank=True)

    thumbnail = models.ImageField(blank=True)
    mangadex_id = models.CharField(max_length=512, blank=True)
    toonkor_id = models.SlugField(default="")

    def __str__(self) -> str:
        return self.title

    @property
    def path(self) -> str:
        if self.en_title:
            return f"toonkor_collector2/media/{self.en_title}"
        else:
            return f"toonkor_collector2/media/{self.encode_name(self.title)}"
        
    @property
    def media_path(self) -> str:
        if self.en_title:
            return f"/media/{self.en_title}"
        else:
            return f"/media/{self.encode_name(self.title)}"

    def encode_name(self, name):
        return base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")


class StatusChoices(models.TextChoices):
    ON_TOONKOR = "On Toonkor", "On Toonkor"
    DOWNLOADED = "Downloaded", "Downloaded"
    TRANSLATED = "Translated", "Translated"


class Chapter(models.Model):
    manhwa = models.ForeignKey(Manhwa, on_delete=models.CASCADE)
    index = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ON_TOONKOR,
    )
    toonkor_id = models.SlugField(default="")
    date_upload = models.CharField(max_length=512, blank=True)

    def __str__(self) -> str:
        return f"{self.manhwa.title} - Chapter {self.index}"

    @property
    def downloaded_path(self) -> str:
        return f"{self.manhwa.path}/{self.index}"

    @property
    def translated_path(self) -> str:
        return f"{self.manhwa.path}/{self.index}/translated"
    
    @property
    def media_downloaded_path(self) -> str:
        return f"{self.manhwa.media_path}/{self.index}"

    @property
    def media_translated_path(self) -> str:
        return f"{self.manhwa.media_path}/{self.index}/translated"
