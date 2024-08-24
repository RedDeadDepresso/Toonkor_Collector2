from django.db import models

# Create your models here.
class Manhwa(models.Model):
    title = models.CharField(max_length=512)
    author = models.CharField(max_length=512, blank=True)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(blank=True)
    slug = models.SlugField(default='')


class Chapter(models.Model):
    manhwa = models.ForeignKey(Manhwa, on_delete=models.CASCADE)
    index = models.IntegerField()
    translated = models.BooleanField(default=False)