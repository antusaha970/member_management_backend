# Generated by Django 5.1.5 on 2025-02-18 05:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_employmenttypechoice_club_and_more'),
        ('member', '0006_alter_spouse_current_status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvailableID',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member_ID', models.CharField(max_length=200, unique=True)),
                ('membership_type', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='available_id', to='core.membershiptype')),
            ],
        ),
    ]
