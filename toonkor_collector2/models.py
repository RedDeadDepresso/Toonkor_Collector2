from django.db import models

# Create your models here.
class Manhwa(models.Model):
    title = models.CharField(max_length=512)
    author = models.CharField(max_length=512, blank=True)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(blank=True)


class Chapter(models.Model):
    manhwa = models.ForeignKey(Manhwa, on_delete=models.CASCADE)
    index = models.IntegerField()
    date_upload = models.DateTimeField()
    downloaded_path = models.FilePathField()
    translated_path = models.FilePathField()