# Generated by Django 4.1.1 on 2023-02-03 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("studybuddy", "0005_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="endDate",
            field=models.DateField(default="2023-02-10"),
        ),
        migrations.AlterField(
            model_name="post",
            name="startDate",
            field=models.DateField(default="2023-02-03"),
        ),
        migrations.AlterField(
            model_name="studysession",
            name="date",
            field=models.DateField(default="02-03-2023"),
        ),
        migrations.AlterField(
            model_name="studysession",
            name="end",
            field=models.TimeField(default="20-01"),
        ),
        migrations.AlterField(
            model_name="studysession",
            name="start",
            field=models.TimeField(default="19-01"),
        ),
    ]