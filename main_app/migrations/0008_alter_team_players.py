# Generated by Django 4.0.3 on 2022-07-26 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0007_alter_players_teams'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='players',
            field=models.TextField(default=[]),
        ),
    ]
