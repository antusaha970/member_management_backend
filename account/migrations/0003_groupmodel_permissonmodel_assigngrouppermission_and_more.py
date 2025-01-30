# Generated by Django 5.1.5 on 2025-01-30 10:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_accounttestmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PermissonModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssignGroupPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='custom_user', to=settings.AUTH_USER_MODEL)),
                ('group', models.ManyToManyField(related_name='group', to='account.groupmodel')),
            ],
        ),
        migrations.AddField(
            model_name='groupmodel',
            name='permission',
            field=models.ManyToManyField(related_name='group', to='account.permissonmodel'),
        ),
    ]
