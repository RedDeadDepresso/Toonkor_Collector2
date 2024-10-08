# Generated by Django 5.1 on 2024-08-23 00:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Manhwa",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=512)),
                ("author", models.CharField(blank=True, max_length=512)),
                ("description", models.TextField(blank=True)),
                ("thumbnail", models.ImageField(blank=True, upload_to="")),
            ],
        ),
        migrations.CreateModel(
            name="Chapter",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("index", models.IntegerField()),
                ("date_upload", models.DateTimeField()),
                ("downloaded_path", models.FilePathField()),
                ("translated_path", models.FilePathField()),
                (
                    "manhwa",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="toonkor_collector2.manhwa",
                    ),
                ),
            ],
        ),
    ]
