# Generated by Django 5.1 on 2024-09-10 22:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("toonkor_collector2", "0015_chapter_upload_date"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="chapter",
            name="title",
        ),
    ]
