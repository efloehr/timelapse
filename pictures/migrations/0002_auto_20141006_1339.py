# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pictures', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='picture',
            name='exposure',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='picture',
            name='filename',
            field=models.CharField(unique=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='picture',
            name='fstop',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='picture',
            name='timestamp',
            field=models.DateTimeField(unique=True, null=True, db_index=True),
        ),
    ]
