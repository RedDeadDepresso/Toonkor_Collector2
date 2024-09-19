import base64
import os

from django.db import models
from functools import cached_property


def encode_name(name: str):
    return base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")


def decode_name(encoded_name: str):
    padded_encoded_name = encoded_name + "=" * (4 - len(encoded_name) % 4)
    return base64.urlsafe_b64decode(padded_encoded_name).decode()


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
        return f"/media/{encode_name(self.toonkor_id)}"
    
    @cached_property
    def path(self) -> str:
        return f"toonkor_collector2{self.media_path}"


class StatusChoices(models.TextChoices):
    NOT_READY = "NOT_READY"
    LOADING = "LOADING"
    READY = "READY"
    REMOVING = "REMOVING"


class Chapter(models.Model):
    index = models.IntegerField()
    toonkor_id = models.SlugField(default="")
    date_upload = models.CharField(max_length=512, blank=True)
    manhwa_id = models.CharField(max_length=512)

    download_status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.NOT_READY)
    translation_status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.NOT_READY)

    image_extensions = {'.png', '.jpeg', '.jpg', '.webp', '.gif', '.svg'}

    def __str__(self) -> str:
        return f"{self.manhwa_id} - Chapter {self.index}"
    
    @cached_property
    def manhwa_media_path(self) -> str:
        return f"/media/{encode_name(self.manhwa_id)}"
    
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
    
    @classmethod
    def is_page(cls, file: str):
        name, extension = os.path.splitext(file)
        if name.isdigit() and extension in cls.image_extensions:
            return True
        return False
    
    def media_pages(self, pages_path: str, media_pages_path: str) -> list[str]:
        pages = []
        if os.path.isdir(pages_path):
            pages = [f'{media_pages_path}/{file}' for file in os.listdir(pages_path) if self.is_page(file)] 
            pages.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
        return pages

    @property
    def media_download_pages(self) -> list[str]:
        return self.media_pages(self.downloaded_path, self.media_downloaded_path)

    @property
    def media_translation_pages(self) -> list[str]:
        return self.media_pages(self.translated_path, self.media_translated_path)
    
    def delete_pages(self, folder_path) -> bool:
        try:
            if not os.path.isdir(folder_path):
                return False
            
            for file in os.listdir(folder_path):
                if self.is_page(file):
                    os.remove(os.path.join(folder_path, file))

            if not os.listdir(folder_path):
                os.rmdir(folder_path)
            return True
        except:
            return False

    def delete_download(self, save=True):
        if self.delete_pages(self.downloaded_path):
            self.download_status = StatusChoices.NOT_READY
            if save:
                self.save()
            return True
        return False

    def delete_translation(self, save=True):
        if self.delete_pages(self.translated_path):
            self.translation_status = StatusChoices.NOT_READY
            if save:
                self.save()
            return True
        return False
    

class ToonkorSettings(models.Model):
    name = models.CharField(max_length=512)
    url = models.URLField(default="https://toonkor434.com")