# Generated by Django 5.1.1 on 2024-10-16 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_lesson_is_complete'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='homework_requirements',
            field=models.TextField(blank=True, null=True),
        ),
    ]
