# Generated by Django 5.1.5 on 2025-02-11 16:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(default='')),
                ('location', models.JSONField(blank=True, default=dict)),
                ('user_agent', models.TextField(blank=True, default='Unknown')),
                ('request_method', models.CharField(blank=True, default='', max_length=10)),
                ('severity_level', models.CharField(choices=[('info', 'Info'), ('warning', 'Warning'), ('error', 'Error'), ('critical', 'Critical')], default='info', max_length=50)),
                ('referrer_url', models.TextField(blank=True, default='')),
                ('device', models.CharField(blank=True, default='Unknown Device', max_length=255)),
                ('path', models.CharField(blank=True, default='/', max_length=255)),
                ('verb', models.CharField(blank=True, default='', max_length=50)),
                ('description', models.TextField(blank=True, default='')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activity_logs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
