# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-11 13:16
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20180211_1828'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newspost',
            name='minute_interval',
        ),
        migrations.AlterField(
            model_name='newspost',
            name='time_of_post',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2018, 2, 11, 18, 46, 10, 205360)),
        ),
    ]
