# Generated by Django 5.1.5 on 2025-02-20 03:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_employmenttypechoice_club_and_more'),
        ('member', '0010_address_is_active_certificate_is_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactnumber',
            name='contact_type',
            field=models.ForeignKey(blank=True, default='present', null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='contact_type_choice', to='core.contacttypechoice'),
        ),
    ]
