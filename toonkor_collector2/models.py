import base64
from django.db import models


# Create your models here.
class Manhwa(models.Model):
    title = models.CharField(max_length=512)
    author = models.CharField(max_length=512, blank=True)
    description = models.TextField(blank=True)

    en_title = models.CharField(max_length=512, blank=True)
    en_author = models.CharField(max_length=512, blank=True)
    en_description = models.TextField(blank=True)

    thumbnail = models.ImageField(blank=True)
    slug = models.SlugField(default='')

    def __str__(self) -> str:
        return self.title

    @property
    def path(self) -> str:
        if self.en_title:
            return f"toonkor_collector2/media/{self.en_title}"
        else:
            return f"toonkor_collector2/media/{self.encode_name(self.title)}"

    def encode_name(self, name):
        return base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")


class StatusChoices(models.TextChoices):
    ON_TOONKOR = "ON_TOONKOR", "On Toonkor"
    DOWNLOADED = "DOWNLOADED", "Downloaded"
    TRANSLATED = "TRANSLATED", "Translated"


class Chapter(models.Model):
    manhwa = models.ForeignKey(Manhwa, on_delete=models.CASCADE)
    index = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ON_TOONKOR,
    )

    def __str__(self) -> str:
        return f"{self.manhwa.title} - Chapter {self.index}"

    @property
    def path(self) -> str:
        return f"toonkor_collector2/{self.manhwa.path}/{self.index}"

    @property
    def translated_path(self) -> str:
        return f"toonkor_collector2/{self.manhwa.path}/{self.index}/translated"
