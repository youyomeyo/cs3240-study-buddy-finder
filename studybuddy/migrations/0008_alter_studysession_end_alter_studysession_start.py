# Generated by Django 4.1.1 on 2023-02-03 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("studybuddy", "0007_alter_studysession_end_alter_studysession_start"),
    ]

    operations = [
        migrations.AlterField(
            model_name="studysession",
            name="end",
            field=models.TimeField(default="20-04"),
        ),
        migrations.AlterField(
            model_name="studysession",
            name="start",
            field=models.TimeField(default="19-04"),
        ),
    ]