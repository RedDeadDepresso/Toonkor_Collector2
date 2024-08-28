from django.db import models
from toonkor_collector2.toonkor_api import toonkor_api


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
            return f"toonkor_collector2/media/{toonkor_api.encode_name(self.title)}"


class Chapter(models.Model):
    manhwa = models.ForeignKey(Manhwa, on_delete=models.CASCADE)
    index = models.IntegerField()
    translated = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.manhwa.title} - Chapter {self.index}"
    
    @property
    def path(self) -> str:
        return f"toonkor_collector2/{self.manhwa.path()}/{self.index}"
    
    @property
    def translated_path(self) -> str:
        return f"toonkor_collector2/{self.manhwa.path()}/{self.index}/translated"