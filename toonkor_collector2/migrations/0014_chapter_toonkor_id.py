# Generated by Django 5.1 on 2024-09-10 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("toonkor_collector2", "0013_rename_slug_manhwa_toonkor_id_chapter_title"),
    ]

    operations = [
        migrations.AddField(
            model_name="chapter",
            name="toonkor_id",
            field=models.SlugField(default=""),
        ),
    ]
