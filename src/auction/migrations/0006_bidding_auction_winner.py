# Generated by Django 3.0.2 on 2020-04-17 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0005_bidding_item_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='bidding',
            name='auction_winner',
            field=models.CharField(default='', max_length=60),
        ),
    ]
