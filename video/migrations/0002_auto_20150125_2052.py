# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='info',
            name='images',
        ),
        migrations.AlterField(
            model_name='info',
            name='kind',
            field=models.SmallIntegerField(choices=[(1, b'Standard Daylight Video'), (2, b'Standard Night Video'), (3, b'All Day 24h Movie')]),
        ),
        migrations.AlterField(
            model_name='info',
            name='size',
            field=models.BigIntegerField(default=-1),
        ),
    ]
