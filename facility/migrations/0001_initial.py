# Generated by Django 5.1.5 on 2025-04-07 03:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0003_remove_employmenttypechoice_club_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Facility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField()),
                ('usages_fee', models.DecimalField(decimal_places=2, max_digits=10)),
                ('usages_roles', models.CharField(choices=[('member', 'Member'), ('staff', 'Staff'), ('admin', 'Admin'), ('manager', 'Manager')], default='member', max_length=50)),
                ('operating_hours', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed'), ('maintenance', 'Under Maintenance')], default='open', max_length=50)),
                ('capacity', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FacilityUseFee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('fee', models.DecimalField(decimal_places=2, max_digits=10)),
                ('facility', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='facility_use_fees', to='facility.facility')),
                ('membership_type', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='facility_fees_membership_type', to='core.membershiptype')),
            ],
            options={
                'unique_together': {('facility', 'membership_type')},
            },
        ),
    ]
