# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0002_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='filename',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='product',
            name='kind',
            field=models.SmallIntegerField(choices=[(1, b'All-night overlay image'), (2, b'All-night overlay image negative'), (3, b'Classic daystrip'), (4, b'Daystrip that goes from left to right and is each column in the image')]),
        ),
    ]
