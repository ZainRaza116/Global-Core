# Generated by Django 4.2.10 on 2024-02-28 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Global_Core', '0009_merchants_delete_accounts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='merchants',
            name='login_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Login Id/ Gateway Token'),
        ),
    ]