# Generated by Django 5.1.5 on 2025-06-22 03:48

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
            name='Email_Compose',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('subject', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_composes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmailAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('file', models.FileField(upload_to='attachmentsFiles/')),
                ('email_compose', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mails.email_compose')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Outbox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('email_address', models.EmailField(max_length=255)),
                ('status', models.CharField(choices=[('success', 'Success'), ('failed', 'Failed'), ('pending', 'Pending')], max_length=50)),
                ('failed_reason', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('email_compose', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mails.email_compose')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SMTPConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('provider', models.CharField(choices=[('gmail', 'Gmail'), ('personal', 'Personal Domain'), ('ses', 'Amazon SES')], default='gmail', max_length=50)),
                ('host', models.CharField(blank=True, max_length=255, null=True)),
                ('port', models.IntegerField(blank=True, null=True)),
                ('username', models.CharField(blank=True, max_length=255, null=True)),
                ('password', models.CharField(blank=True, max_length=255, null=True)),
                ('use_tls', models.BooleanField(blank=True, default=True, null=True)),
                ('use_ssl', models.BooleanField(blank=True, default=False, null=True)),
                ('aws_access_key_id', models.CharField(blank=True, max_length=255, null=True)),
                ('aws_secret_access_key', models.CharField(blank=True, max_length=255, null=True)),
                ('aws_region', models.CharField(blank=True, max_length=50, null=True)),
                ('ses_configuration_set', models.CharField(blank=True, max_length=255, null=True)),
                ('iam_role_arn', models.CharField(blank=True, max_length=255, null=True)),
                ('enable_tracking', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_smtp_configs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='email_compose',
            name='configurations',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mails.smtpconfiguration'),
        ),
    ]
