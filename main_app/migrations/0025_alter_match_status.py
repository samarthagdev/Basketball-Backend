# Generated by Django 4.0.3 on 2022-08-24 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0024_match_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='status',
            field=models.CharField(choices=[('Upcoming', 'Upcoming'), ('Live', 'Live'), ('TimeOut', 'TimeOut'), ('Ended', 'Ended')], default=('Upcoming', 'Upcoming'), max_length=10),
        ),
    ]
