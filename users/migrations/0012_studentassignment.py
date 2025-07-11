# Generated by Django 5.1.1 on 2024-10-24 17:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_lesson_pdf'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='assignment_files/')),
                ('handed_in', models.BooleanField(default=False)),
                ('date_handed_in', models.DateTimeField(auto_now_add=True)),
                ('grade', models.IntegerField(blank=True, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='users.course')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.lesson')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='users.profile')),
            ],
        ),
    ]
