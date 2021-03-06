# Generated by Django 3.0.2 on 2020-04-13 13:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Auctions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auction_bidding_price', models.IntegerField()),
                ('user_bidding', models.CharField(max_length=60)),
                ('auction_status', models.CharField(choices=[('OPEN', 'Open'), ('COMPLETED', 'Completed')], max_length=20)),
                ('time_left', models.DateTimeField()),
                ('auction_winner', models.CharField(max_length=60)),
                ('bids', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Items',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_title', models.CharField(max_length=60)),
                ('time_stamp', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('NEW', 'New'), ('USED', 'Used')], max_length=20)),
                ('item_description', models.CharField(max_length=60)),
                ('item_owner', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Bidding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auction_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.Auctions')),
                ('item_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.Items')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.User')),
            ],
        ),
        migrations.AddField(
            model_name='auctions',
            name='item_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.Items'),
        ),
    ]
