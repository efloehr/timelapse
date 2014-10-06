# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('filepath', models.CharField(unique=True, max_length=1024)),
                ('filename', models.CharField(unique=True, null=True, max_length=255)),
                ('size', models.IntegerField(default=0)),
                ('timestamp', models.DateTimeField(unique=True, null=True, db_index=True)),
                ('fstop', models.IntegerField(null=True)),
                ('exposure', models.IntegerField(null=True)),
                ('center_color', models.IntegerField(null=True)),
                ('mean_color', models.IntegerField(null=True)),
                ('median_color', models.IntegerField(null=True)),
                ('stddev_red', models.IntegerField(null=True)),
                ('stddev_green', models.IntegerField(null=True)),
                ('stddev_blue', models.IntegerField(null=True)),
                ('min_color', models.IntegerField(null=True)),
                ('max_color', models.IntegerField(null=True)),
                ('valid', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['timestamp'],
            },
            bases=(models.Model,),
        ),
    ]
