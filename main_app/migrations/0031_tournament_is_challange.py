# Generated by Django 4.0.3 on 2022-09-13 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0030_remove_playerranking_tour_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='is_challange',
            field=models.BooleanField(default=False),
        ),
    ]
