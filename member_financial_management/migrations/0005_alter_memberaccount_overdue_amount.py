# Generated by Django 5.1.5 on 2025-04-08 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member_financial_management', '0004_remove_sale_discount_remove_sale_promo_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memberaccount',
            name='overdue_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
