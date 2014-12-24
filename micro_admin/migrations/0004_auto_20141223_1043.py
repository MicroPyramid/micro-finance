# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('micro_admin', '0003_auto_20141218_0350'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fixeddeposits',
            name='savings_account',
        ),
        migrations.RemoveField(
            model_name='recurringdeposits',
            name='savings_account',
        ),
        migrations.AddField(
            model_name='fixeddeposits',
            name='nominee_photo',
            field=models.ImageField(default=None, upload_to=b'static/images/users'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fixeddeposits',
            name='nominee_signature',
            field=models.ImageField(default=None, upload_to=b'static/images/signatures'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recurringdeposits',
            name='nominee_photo',
            field=models.ImageField(default=None, upload_to=b'static/images/users'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recurringdeposits',
            name='nominee_signature',
            field=models.ImageField(default=None, upload_to=b'static/images/signatures'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='branch',
            name='phone_number',
            field=models.BigIntegerField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fixeddeposits',
            name='nominee_firstname',
            field=models.CharField(max_length=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fixeddeposits',
            name='nominee_lastname',
            field=models.CharField(max_length=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fixeddeposits',
            name='nominee_occupation',
            field=models.CharField(max_length=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fixeddeposits',
            name='relationship_with_nominee',
            field=models.CharField(max_length=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(max_length=200),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='recurringdeposits',
            name='nominee_firstname',
            field=models.CharField(max_length=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='recurringdeposits',
            name='nominee_lastname',
            field=models.CharField(max_length=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='recurringdeposits',
            name='nominee_occupation',
            field=models.CharField(max_length=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='recurringdeposits',
            name='relationship_with_nominee',
            field=models.CharField(max_length=50),
            preserve_default=True,
        ),
    ]
