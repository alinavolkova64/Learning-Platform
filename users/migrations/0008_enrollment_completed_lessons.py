# Generated by Django 5.1.1 on 2024-10-05 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_enrollment_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='completed_lessons',
            field=models.ManyToManyField(blank=True, default=0, to='users.lesson'),
        ),
    ]
