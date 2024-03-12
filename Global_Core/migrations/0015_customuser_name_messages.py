# Generated by Django 4.2.10 on 2024-03-01 12:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Global_Core', '0014_alter_card_card_no_alter_card_expiry_month_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='Name',
            field=models.CharField(default=1, max_length=255, verbose_name='Salary'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField(verbose_name='Message')),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='Global_Core.sales')),
            ],
        ),
    ]
