# Generated by Django 5.1.1 on 2024-11-15 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='recipient',
        ),
        migrations.AddField(
            model_name='notification',
            name='recipient',
            field=models.ManyToManyField(related_name='notifications', to='users.profile'),
        ),
    ]
