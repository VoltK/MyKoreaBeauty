# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-07-24 21:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20180725_0045'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'verbose_name': 'пост', 'verbose_name_plural': 'Посты'},
        ),
    ]
