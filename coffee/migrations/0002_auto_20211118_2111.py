# Generated by Django 3.2.9 on 2021-11-18 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coffee', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='sugar',
        ),
        migrations.AddField(
            model_name='cartitem',
            name='sugar',
            field=models.TextField(blank=True),
        ),
    ]
