# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0003_auto_20150125_2127'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.DateField(null=True, db_index=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('kind', models.SmallIntegerField(choices=[(1, b'Standard Daylight Video'), (2, b'Standard Night Video'), (3, b'All Day 24h Movie')])),
                ('filepath', models.CharField(unique=True, max_length=1024)),
                ('filename', models.CharField(max_length=255)),
                ('size', models.BigIntegerField(default=-1)),
            ],
            options={
                'ordering': ['day'],
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='Info',
        ),
    ]
