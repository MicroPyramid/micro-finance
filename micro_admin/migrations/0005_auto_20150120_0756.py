# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('micro_admin', '0004_auto_20141223_1043'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': (('branch_manager', 'Can manage all accounts under his/her branch.'),)},
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(related_name='user_permissions', to='auth.Permission', blank=True),
            preserve_default=True,
        ),
    ]
