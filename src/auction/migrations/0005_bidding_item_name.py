# Generated by Django 3.0.2 on 2020-04-17 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0004_auto_20200416_2223'),
    ]

    operations = [
        migrations.AddField(
            model_name='bidding',
            name='item_name',
            field=models.CharField(default='', max_length=60),
        ),
    ]