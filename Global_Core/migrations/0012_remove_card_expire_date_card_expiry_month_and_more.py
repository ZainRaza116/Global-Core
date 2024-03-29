# Generated by Django 4.2.10 on 2024-02-29 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Global_Core', '0011_sales_state_sales_zip_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='card',
            name='expire_date',
        ),
        migrations.AddField(
            model_name='card',
            name='expiry_month',
            field=models.IntegerField(default=12, verbose_name='Expiry Month'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='card',
            name='expiry_year',
            field=models.IntegerField(default=12, verbose_name='Expiry Year'),
            preserve_default=False,
        ),
    ]
