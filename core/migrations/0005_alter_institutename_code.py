# Generated by Django 5.1.5 on 2025-05-13 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_institutename_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institutename',
            name='code',
            field=models.CharField(
                default='', max_length=50, null=True, unique=True),
        ),
    ]
