# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-06-24 12:41
from __future__ import unicode_literals

import blog.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20180315_2337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to=blog.models.upload_image_path),
        ),
    ]
