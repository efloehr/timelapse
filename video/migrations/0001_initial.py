# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Info',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.DateField(db_index=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('kind', models.SmallIntegerField(choices=[(1, b'Standard Daylight Video'), (2, b'Standard Night Video')])),
                ('filepath', models.CharField(unique=True, max_length=1024)),
                ('filename', models.CharField(max_length=255, unique=True, null=True)),
                ('size', models.IntegerField(default=0)),
                ('images', models.ManyToManyField(related_name=b'video_normal', to='image.Normal')),
            ],
            options={
                'ordering': ['day'],
            },
            bases=(models.Model,),
        ),
    ]
