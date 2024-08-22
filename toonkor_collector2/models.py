from django.db import models

# Create your models here.
    

class Manhwa(models.Model):
    title = models.CharField(max_length=512)
    author = models.CharField(max_length=512)
    chapters = models.IntegerField(default=0)
    banner = models.ImageField(blank=True)
    url = models.URLField()


class Chapter(models.Model):
    manhwa = models.ForeignKey(Manhwa, on_delete=models.CASCADE)
    path = models.FilePathField()
    translated_path = models.FilePathField()
