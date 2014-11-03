# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('username', models.CharField(unique=True, max_length=50)),
                ('email', models.EmailField(unique=True, max_length=255)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100, null=True)),
                ('gender', models.CharField(max_length=10, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('user_roles', models.CharField(max_length=20, choices=[(b'BranchManager', b'BranchManager'), (b'LoanOfficer', b'LoanOfficer'), (b'Cashier', b'Cashier')])),
                ('date_of_birth', models.DateField(default=b'2000-01-01', null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('country', models.CharField(max_length=50, null=True)),
                ('state', models.CharField(max_length=50, null=True)),
                ('district', models.CharField(max_length=50, null=True)),
                ('city', models.CharField(max_length=50, null=True)),
                ('area', models.CharField(max_length=150, null=True)),
                ('mobile', models.CharField(default=b'0', max_length=10, null=True)),
                ('pincode', models.CharField(default=b'', max_length=10, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('opening_date', models.DateField()),
                ('country', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('district', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('area', models.CharField(max_length=150)),
                ('phone_number', models.IntegerField()),
                ('pincode', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Centers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('created_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('branch', models.ForeignKey(to='micro_admin.Branch')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=255, null=True)),
                ('account_type', models.CharField(max_length=20, choices=[(b'SavingsAccount', b'SavingsAccount'), (b'LoanAccount', b'LoanAccount')])),
                ('account_number', models.CharField(unique=True, max_length=50)),
                ('date_of_birth', models.DateField()),
                ('blood_group', models.CharField(default=True, max_length=10, null=True)),
                ('gender', models.CharField(max_length=10, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('client_role', models.CharField(max_length=20, choices=[(b'FirstLeader', b'FirstLeader'), (b'SecondLeader', b'SecondLeader'), (b'GroupMember', b'GroupMember')])),
                ('occupation', models.CharField(max_length=200)),
                ('annual_income', models.BigIntegerField()),
                ('joined_date', models.DateField()),
                ('country', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('district', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('area', models.CharField(max_length=150)),
                ('mobile', models.CharField(default=True, max_length=20, null=True)),
                ('pincode', models.CharField(default=True, max_length=20, null=True)),
                ('photo', models.ImageField(null=True, upload_to=b'static/images/users')),
                ('signature', models.ImageField(null=True, upload_to=b'static/images/signatures')),
                ('is_active', models.BooleanField(default=True)),
                ('status', models.CharField(default=b'UnAssigned', max_length=50)),
                ('branch', models.ForeignKey(to='micro_admin.Branch')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('account_type', models.CharField(max_length=20, choices=[(b'SavingsAccount', b'SavingsAccount'), (b'LoanAccount', b'LoanAccount')])),
                ('account_number', models.CharField(unique=True, max_length=50)),
                ('activation_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('branch', models.ForeignKey(to='micro_admin.Branch')),
                ('clients', models.ManyToManyField(to='micro_admin.Client', null=True, blank=True)),
                ('staff', models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='centers',
            name='groups',
            field=models.ManyToManyField(to='micro_admin.Group', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='branch',
            field=models.ForeignKey(blank=True, to='micro_admin.Branch', null=True),
            preserve_default=True,
        ),
    ]
