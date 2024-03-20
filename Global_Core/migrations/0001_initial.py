# Generated by Django 5.0.1 on 2024-02-14 13:59

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=255, verbose_name='Company Name')),
            ],
        ),
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Expenses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_incurred', models.DateField(auto_now_add=True, verbose_name='Created Date')),
                ('expense_date', models.DateField(default=django.utils.timezone.now, verbose_name='Date')),
                ('title', models.CharField(max_length=255, verbose_name='Expense Title')),
                ('amount', models.CharField(max_length=255, verbose_name='Expense Amount')),
                ('expenses_type', models.CharField(choices=[('payroll', 'Payroll'), ('office', 'Office'), ('utility', 'Utility'), ('Rent', 'Rent'), ('Other', 'Other')], max_length=50, verbose_name='Expenses Type')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Details')),
            ],
        ),
        migrations.CreateModel(
            name='Merchants',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('merchant', models.CharField(max_length=255, verbose_name='Merchant')),
                ('merchant_dba', models.CharField(max_length=255, verbose_name='Merchant DBA')),
                ('account_type', models.CharField(choices=[('merchant', 'Merchant'), ('Payment_portal', 'Payment Portal')], max_length=50, verbose_name='Account Type')),
                ('merchant_type', models.CharField(choices=[('full', 'Full'), ('link', 'Link')], max_length=50, verbose_name='Merchant Type')),
            ],
        ),
        migrations.CreateModel(
            name='Links',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.CharField(max_length=255, verbose_name='Link')),
                ('amount', models.FloatField(verbose_name='Amount')),
                ('merchant_link', models.ForeignKey(default=0, limit_choices_to={'merchant_type': 'link'}, on_delete=django.db.models.deletion.PROTECT, to='Global_Core.merchants', verbose_name='Merchant Name')),
            ],
        ),
        migrations.CreateModel(
            name='Accounts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Type', models.CharField(blank=True, max_length=255, null=True, verbose_name='Type')),
                ('Link', models.CharField(max_length=255, verbose_name='Access Link')),
                ('login', models.CharField(max_length=255, verbose_name='Login ID')),
                ('password', models.CharField(max_length=255, verbose_name='Password')),
                ('DBA', models.ForeignKey(default=0, on_delete=django.db.models.deletion.PROTECT, related_name='dba_accounts', to='Global_Core.company', verbose_name='Company Name')),
                ('merchant_link', models.ForeignKey(default=0, on_delete=django.db.models.deletion.PROTECT, related_name='merchant_accounts', to='Global_Core.merchants', verbose_name='Merchant Name')),
            ],
        ),
        migrations.CreateModel(
            name='Sales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sales_date', models.DateField(default=django.utils.timezone.now, verbose_name='Date')),
                ('provider_name', models.CharField(max_length=255, verbose_name='Provider Name')),
                ('customer_name', models.CharField(max_length=255, verbose_name='Customer Name')),
                ('customer_first_name', models.CharField(max_length=255, verbose_name='Customer First Name')),
                ('customer_last_name', models.CharField(max_length=255, verbose_name='Customer Last Name')),
                ('customer_address', models.CharField(max_length=255, verbose_name='Customer Address')),
                ('btn', models.CharField(blank=True, max_length=20, null=True, verbose_name='BTN')),
                ('calling_no', models.CharField(blank=True, max_length=15, null=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '(555) 555-1234'.", regex='^\\(\\d{3}\\) \\d{3}-\\d{4}$')], verbose_name='Phone Number')),
                ('customer_email', models.EmailField(max_length=254)),
                ('ssn', models.CharField(blank=True, max_length=10, null=True, validators=[django.core.validators.RegexValidator(message='SSN must be either 4 digits or 9 digits.', regex='^\\d{4}$|^\\d{9}$')], verbose_name='SSN')),
                ('cus_dob', models.DateField()),
                ('pin', models.CharField(blank=True, max_length=20, null=True, verbose_name='Pin')),
                ('acc_user_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Account User Name')),
                ('password', models.CharField(blank=True, max_length=255, null=True, verbose_name='Password')),
                ('amount', models.FloatField(blank=True, null=True, verbose_name='Amount')),
                ('payment_method', models.CharField(choices=[('card', 'Card'), ('account', 'Account')], default='account', max_length=50, verbose_name='Payment Method')),
                ('account_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name on Account')),
                ('checking_acc', models.CharField(blank=True, max_length=20, null=True, verbose_name='Checking Account')),
                ('routing_no', models.CharField(blank=True, max_length=20, null=True, verbose_name='Routing #')),
                ('checking_no', models.CharField(blank=True, max_length=20, null=True, verbose_name='Checking No')),
                ('account_address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Account Address')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_process', 'In-Process'), ('completed', 'Completed')], default='pending', max_length=50, verbose_name='Status')),
                ('reason', models.CharField(blank=True, max_length=255, null=True, verbose_name='Reason')),
                ('description', models.TextField(blank=True, max_length=255, null=True, verbose_name='Description')),
                ('authorization', models.FileField(blank=True, null=True, upload_to='sales_files/', verbose_name='Authorization')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='sales', to='Global_Core.company', verbose_name='Company')),
                ('merchant', models.ForeignKey(default=0, on_delete=django.db.models.deletion.PROTECT, related_name='sales', to='Global_Core.merchants', verbose_name='Merchant Name')),
            ],
            options={
                'permissions': [('view_own_sales', 'Can view own sales')],
            },
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name on Card')),
                ('billing_address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Billing Address')),
                ('card_no', models.CharField(blank=True, max_length=255, null=True, verbose_name='Card Number')),
                ('expire_date', models.DateField(blank=True, null=True, verbose_name='Expire Date')),
                ('cvv', models.CharField(blank=True, max_length=10, null=True, verbose_name='CVV')),
                ('sales', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cards', to='Global_Core.sales')),
            ],
            options={
                'verbose_name': 'Card',
                'verbose_name_plural': 'Cards',
            },
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('salary', models.CharField(max_length=255, verbose_name='Salary')),
                ('target', models.CharField(max_length=255, verbose_name='Target')),
                ('hiring_date', models.DateField(default=django.utils.timezone.now, verbose_name='Hiring Date')),
                ('is_floormanager', models.BooleanField(default=False, verbose_name='Floor Manager')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='sales',
            name='added_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Added By'),
        ),
    ]
