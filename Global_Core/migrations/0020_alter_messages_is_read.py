# Generated by Django 4.2.10 on 2024-03-18 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Global_Core', '0019_alter_messages_is_read'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]
