# Generated by Django 5.1.5 on 2025-02-16 03:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_forgetpasswordotp_delete_accounttestmodel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='club',
        ),
    ]
