# Generated by Django 4.0.3 on 2022-08-08 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0015_tournament_tour_teams'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='tournament',
            field=models.TextField(default={}),
        ),
    ]
