# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('micro_admin', '0002_auto_20141218_0344'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanaccount',
            name='principle_repayment',
            field=models.DecimalField(null=True, max_digits=19, decimal_places=6, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='receipts',
            name='group_loan_account',
            field=models.ForeignKey(related_name='group_loan_account', blank=True, to='micro_admin.LoanAccount', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='receipts',
            name='member_loan_account',
            field=models.ForeignKey(blank=True, to='micro_admin.LoanAccount', null=True),
            preserve_default=True,
        ),
    ]
