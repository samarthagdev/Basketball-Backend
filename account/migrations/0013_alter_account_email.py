# Generated by Django 4.0.3 on 2022-09-17 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_account_is_youtuber'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='email',
            field=models.EmailField(max_length=500, null=True),
        ),
    ]
