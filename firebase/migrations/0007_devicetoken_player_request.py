# Generated by Django 4.0.3 on 2022-08-05 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firebase', '0006_devicetoken_team_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicetoken',
            name='player_request',
            field=models.TextField(default=[]),
        ),
    ]
