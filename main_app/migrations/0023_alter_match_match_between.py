# Generated by Django 4.0.3 on 2022-08-18 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0022_alter_match_team_a_1_alter_match_team_a_1_attempt_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='match_between',
            field=models.TextField(default={}),
        ),
    ]
