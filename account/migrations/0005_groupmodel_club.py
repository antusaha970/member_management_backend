# Generated by Django 5.1.5 on 2025-02-05 07:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_verifysuccessfulemail_remove_otp_user_otp_email_and_more'),
        ('club', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupmodel',
            name='club',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='club.club'),
        ),
    ]
