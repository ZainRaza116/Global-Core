# Generated by Django 5.0.1 on 2024-02-14 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Global_Core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='card_to_be_used',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='card',
            name='gift_card',
            field=models.CharField(blank=True, choices=[('yes', 'Yes'), ('No', 'No')], max_length=10, null=True, verbose_name='is it a gift card'),
        ),
        migrations.AlterField(
            model_name='sales',
            name='calling_no',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='sales',
            name='ssn',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='SSN'),
        ),
    ]
