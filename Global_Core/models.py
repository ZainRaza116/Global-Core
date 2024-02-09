from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Dashboard(models.Model):
    pass


class Merchants(models.Model):
    ACCOUNT_CHOICES = [
        ('merchant', 'Merchant'),
        ('Payment_portal', 'Payment Portal'),
    ]
    MERCHANT_CHOICES = [
        ('full', 'Full'),
        ('link', 'Link'),
    ]

    merchant = models.CharField(max_length=255, blank=False, null=False, verbose_name='Merchant')
    merchant_dba = models.CharField(max_length=255, blank=False, null=False, verbose_name='Merchant DBA')
    account_type = models.CharField(max_length=50, choices=ACCOUNT_CHOICES, verbose_name='Account Type')
    merchant_type = models.CharField(max_length=50, choices=MERCHANT_CHOICES, verbose_name='Merchant Type')

    def __str__(self): return self.merchant


class Expenses(models.Model):
    EXPENSES_CHOICES = [
        ('payroll', 'Payroll'),
        ('office', 'Office'),
        ('utility', 'Utility'),
        ('Rent', 'Rent'),
        ('Other', 'Other')
    ]
    date_incurred = models.DateField(verbose_name='Created Date', auto_now_add=True)
    expense_date = models.DateField(verbose_name='Date', default=timezone.now)
    title = models.CharField(max_length=255, blank=False, null=False, verbose_name='Expense Title')
    amount = models.CharField(max_length=255, blank=False, null=False, verbose_name='Expense Amount')
    expenses_type = models.CharField(max_length=50, choices=EXPENSES_CHOICES, verbose_name='Expenses Type')
    notes = models.TextField(blank=True, null=True, verbose_name='Details')

    def __str__(self): return self.title


class Sales(models.Model):
    pass


class Links(models.Model):
    merchant_link = models.ForeignKey(
        Merchants,
        on_delete=models.PROTECT,
        verbose_name='Merchant Name',
        default=0,
        limit_choices_to={'merchant_type': 'link'}
    )

    link = models.CharField(max_length=255, blank=False, null=False, verbose_name='Link')
    amount = models.FloatField(blank=False, null=False, verbose_name='Amount')

    def __str__(self):
        return str(self.merchant_link)


class Company(models.Model):
    company_name = models.CharField(max_length=255, blank=False, null=False, verbose_name='Company Name')

    def __str__(self):
        return str(self.company_name)


class Accounts(models.Model):
    merchant_link = models.ForeignKey(
        Merchants,
        on_delete=models.PROTECT,
        verbose_name='Merchant Name',
        related_name='merchant_accounts',
        default=0,
    )
    DBA = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        verbose_name='Company Name',
        related_name='dba_accounts',
        default=0,
    )
    Type = models.CharField(max_length=255, blank=True, null=True, verbose_name='Type')  # New field for Type
    Link = models.CharField(max_length=255, blank=False, null=False, verbose_name='Access Link')
    login = models.CharField(max_length=255, blank=False, null=False, verbose_name='Login ID')
    password = models.CharField(max_length=255, blank=False, null=False, verbose_name='Password')

    def save(self, *args, **kwargs):
        if self.merchant_link:
            self.Type = self.merchant_link.ACCOUNT_CHOICES
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.merchant_link)


class Employee(models.Model):
    pass


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    salary = models.CharField(max_length=255, blank=False, null=False, verbose_name='Salary')
    target = models.CharField(max_length=255, blank=False, null=False, verbose_name='Target')
    hiring_date = models.DateField(blank=False, default=timezone.now, null=False, verbose_name='Hiring Date')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['']
