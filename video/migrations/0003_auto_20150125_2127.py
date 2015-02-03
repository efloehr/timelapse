# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0002_auto_20150125_2052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='info',
            name='filename',
            field=models.CharField(max_length=255),
        ),
    ]
