# Generated by Django 5.0.1 on 2024-02-15 12:18

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Global_Core', '0004_card_card_to_be_used_card_gift_card'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('merchant_name', models.CharField(default=django.utils.timezone.now, max_length=255, verbose_name='Merchant Name')),
                ('amount_paid', models.FloatField(verbose_name='Amount Paid')),
                ('sale', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment_detail', to='Global_Core.sales')),
            ],
        ),
    ]