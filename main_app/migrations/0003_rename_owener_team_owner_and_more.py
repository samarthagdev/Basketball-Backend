# Generated by Django 4.0.3 on 2022-07-19 13:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_team'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='owener',
            new_name='owner',
        ),
        migrations.RenameField(
            model_name='team',
            old_name='tournement',
            new_name='tournament',
        ),
    ]
