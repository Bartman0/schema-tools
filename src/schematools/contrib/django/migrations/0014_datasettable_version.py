# Generated by Django 3.1.13 on 2021-11-22 10:34

from django.db import migrations, models

from schematools.types import SemVer


class Migration(migrations.Migration):

    dependencies = [
        ("datasets", "0013_profile_schema_data_as_textfield"),
    ]

    operations = [
        migrations.AddField(
            model_name="datasettable",
            name="version",
            field=models.TextField(default=SemVer("1.0.0")),
        ),
    ]
