# Generated by Django 5.1.1 on 2024-10-02 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_fieldofstudy_course_level_course_fields_of_study'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='fields_of_study',
            field=models.ManyToManyField(related_name='courses', to='users.fieldofstudy'),
        ),
    ]
