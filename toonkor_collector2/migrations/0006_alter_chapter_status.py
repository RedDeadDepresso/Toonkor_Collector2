# Generated by Django 5.1 on 2024-09-05 02:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("toonkor_collector2", "0005_remove_chapter_translated_chapter_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chapter",
            name="status",
            field=models.CharField(
                choices=[
                    ("ON_TOONKOR", "On Toonkor"),
                    ("DOWNLOADED", "Downloaded"),
                    ("TRANSLATED", "Translated"),
                ],
                default="ON_TOONKOR",
                max_length=20,
            ),
        ),
    ]
