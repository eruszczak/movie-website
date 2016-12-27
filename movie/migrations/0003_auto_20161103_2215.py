# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-11-03 21:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0002_auto_20161029_1753'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='title',
            options={'ordering': ('-inserted_date',)},
        ),
        migrations.RemoveField(
            model_name='title',
            name='watch_again_date',
        ),
        migrations.AlterUniqueTogether(
            name='favourite',
            unique_together=set([('user', 'title')]),
        ),
        migrations.AlterUniqueTogether(
            name='rating',
            unique_together=set([('user', 'title', 'rate_date')]),
        ),
        migrations.AlterUniqueTogether(
            name='watchlist',
            unique_together=set([('user', 'title')]),
        ),
    ]