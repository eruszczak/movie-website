# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-29 10:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('titles', '0017_auto_20171228_1807'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='title',
            name='source',
        ),
    ]