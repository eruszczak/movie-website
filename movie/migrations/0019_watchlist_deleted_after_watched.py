# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-09-19 07:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0018_auto_20160916_2249'),
    ]

    operations = [
        migrations.AddField(
            model_name='watchlist',
            name='deleted_after_watched',
            field=models.BooleanField(default=False),
        ),
    ]