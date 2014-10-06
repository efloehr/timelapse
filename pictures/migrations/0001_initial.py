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
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('filepath', models.CharField(max_length=1024, unique=True)),
                ('filename', models.CharField(max_length=255, unique=True)),
                ('size', models.IntegerField(default=0)),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('fstop', models.IntegerField()),
                ('exposure', models.IntegerField()),
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
