# Generated by Django 4.0.3 on 2022-07-23 11:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_players_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='players',
            name='number',
        ),
    ]
