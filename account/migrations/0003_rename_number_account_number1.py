# Generated by Django 4.0.3 on 2022-06-28 12:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_alter_account_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='number',
            new_name='number1',
        ),
    ]
