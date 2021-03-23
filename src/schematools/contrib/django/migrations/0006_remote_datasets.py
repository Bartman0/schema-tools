# Generated by Django 3.0.4 on 2020-05-07 03:43

from django.db import migrations, models

import schematools.contrib.django.validators


class Migration(migrations.Migration):

    dependencies = [
        ("datasets", "0005_datasetfield"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataset",
            name="enable_db",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="dataset",
            name="endpoint_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="dataset",
            name="url_prefix",
            field=models.CharField(
                blank=True,
                max_length=100,
                validators=[schematools.contrib.django.validators.URLPathValidator()],
            ),
        ),
    ]