# Generated by Django 4.0.3 on 2022-08-05 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0013_tournament_tour_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='tour_owner',
            field=models.CharField(default='', max_length=70),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='tour_referee',
            field=models.TextField(blank=True, default=[]),
        ),
    ]
