# Generated by Django 4.2.10 on 2024-02-29 13:50

import Global_Core.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Global_Core', '0013_bankaccount_account_to_be_used_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='card_no',
            field=models.CharField(default=1, max_length=255, validators=[Global_Core.models.validate_credit_card_number], verbose_name='Card Number'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='card',
            name='expiry_month',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)], verbose_name='Expiry Month'),
        ),
        migrations.AlterField(
            model_name='card',
            name='expiry_year',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(2023)], verbose_name='Expiry Year'),
        ),
    ]
