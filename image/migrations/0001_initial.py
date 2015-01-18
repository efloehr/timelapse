# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Info',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('filepath', models.CharField(unique=True, max_length=1024)),
                ('filename', models.CharField(max_length=255, unique=True, null=True)),
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
        migrations.CreateModel(
            name='Normal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('info', models.ForeignKey(to='image.Info', null=True)),
            ],
            options={
                'ordering': ['timestamp'],
            },
            bases=(models.Model,),
        ),
    ]
