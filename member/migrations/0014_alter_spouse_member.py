# Generated by Django 5.1.5 on 2025-02-25 04:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0013_alter_member_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spouse',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='spouse', to='member.member'),
        ),
    ]
