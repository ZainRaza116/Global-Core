from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from localflavor.us.models import USStateField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator

class CustomUser(AbstractUser, PermissionsMixin):
    username = None
    Name = models.CharField(max_length=255, blank=False, null=False, verbose_name='Name')
    email = models.EmailField(unique=True)
    salary = models.CharField(max_length=255, blank=False, null=False, verbose_name='Salary')
    target = models.CharField(max_length=255, blank=False, null=False, verbose_name='Target')
    commission = models.CharField(max_length=255, blank=False, null=False, verbose_name='Commision')
    hiring_date = models.DateField(blank=False, default=timezone.now, null=False, verbose_name='Hiring Date')
    is_floormanager = models.BooleanField(default=False, verbose_name='Floor Manager')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['salary', 'target', 'hiring_date']
    objects = UserManager()
    class Meta:
        verbose_name_plural = "Users"


class Dashboard(models.Model):
    pass


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
    class Meta:
        verbose_name_plural = "Expenses"


class Company(models.Model):
    company_name = models.CharField(max_length=255, blank=False, null=False, verbose_name='Company Name')
    company_address = models.CharField(max_length=255, blank=False, null=False, verbose_name='Company Address')
    company_phone = models.CharField(max_length=20, verbose_name='Company Phone')
    company_email = models.CharField(max_length=255, blank=False, null=False, verbose_name='Company Email')
    company_website = models.CharField(max_length=255, blank=False, null=False, verbose_name='Company website')
    authorization = models.FileField(
        upload_to='static/',
        verbose_name='Authorization',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])]
    )
    def __str__(self):
        return str(self.company_name)
    class Meta:
        verbose_name_plural = "Companies"


class Gateway(models.Model):
    ACCOUNT_CHOICES = [
        ('merchant', 'Merchant'),
        ('Payment_portal', 'Payment Portal'),
    ]
    MERCHANT_CHOICES = [
        ('full', 'Full'),
        ('link', 'Link'),
    ]

    merchant = models.CharField(max_length=255, blank=False, null=False, verbose_name='Merchant')
    merchant_dba = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        verbose_name='merchant DBA',
        related_name='merchant_gateways',
        null=True,
        blank=True,
    )
    account_type = models.CharField(max_length=50, choices=ACCOUNT_CHOICES, verbose_name='Account Type')
    merchant_type = models.CharField(max_length=50, choices=MERCHANT_CHOICES, verbose_name='Merchant Type')

    def __str__(self): return self.merchant
    class Meta:
        verbose_name_plural = "Gateways"


class Sales(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Card'),
        ('account', 'Account'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_process', 'In-Process'),
        ('completed', 'Completed')
    ]
    ssn_regex = RegexValidator(
        regex=r'^\d{4}$|^\d{9}$',
        message="SSN must be either 4 digits or 9 digits."
    )
    phone_regex = RegexValidator(
        regex=r'^\(\d{3}\) \d{3}-\d{4}$',
        message="Phone number must be entered in the format: '(555) 555-1234'."
    )

    sales_date = models.DateField(verbose_name='Date', default=timezone.now)
    provider_name = models.CharField(max_length=255, verbose_name='Provider Name')
    added_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        verbose_name='Added By',
        null=True,
        blank=True,
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        verbose_name='Company',
        related_name='sales',
        null=True,
        blank=True,
    )
    customer_name = models.CharField(max_length=255, verbose_name="Customer Name")
    customer_first_name = models.CharField(max_length=255, verbose_name="Customer First Name")
    customer_last_name = models.CharField(max_length=255, verbose_name="Customer Last Name")
    customer_address = models.CharField(max_length=255, verbose_name="Customer Address")
    state = USStateField(verbose_name='Customer State')
    transaction_type = models.CharField(max_length=20, verbose_name='transaction type')
    zip_code = models.CharField(max_length=255, verbose_name="Zip Code")
    btn = models.CharField(max_length=20, verbose_name='BTN', null=True, blank=True)
    calling_no = models.CharField(max_length=15, verbose_name='Phone Number', null=True, blank=True)
    customer_email = models.EmailField()
    ssn = models.CharField(max_length=10, verbose_name='SSN', null=True, blank=True)
    cus_dob = models.DateField()
    pin = models.CharField(max_length=20, verbose_name='Pin', null=True, blank=True)
    acc_user_name = models.CharField(max_length=255, verbose_name='Account User Name', null=True, blank=True)
    password = models.CharField(max_length=255, verbose_name='Password', null=True, blank=True)
    amount = models.FloatField(verbose_name='Amount', null=True, blank=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, verbose_name='Payment Method', default='card')

    wallet_check = models.BooleanField(default=False, verbose_name='Wallet Check')

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name='Status', default="pending")
    reason = models.CharField(max_length=255, verbose_name='Reason', null=True, blank=True)
    description = models.TextField(max_length=255, verbose_name='Description', null=True, blank=True)
    authorization = models.FileField(upload_to='sales_files/', verbose_name='Authorization', blank=True, null=True)


    def __str__(self):
        return self.provider_name

    class Meta:
        verbose_name_plural = "Sales"


class BankAccount(models.Model):
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name='Accounts')
    account_name = models.CharField(max_length=255, verbose_name='Name on Account', null=True, blank=True)
    checking_acc = models.CharField(max_length=20, verbose_name='Checking Account', null=True, blank=True)
    routing_no = models.CharField(max_length=20, verbose_name='Routing #', null=True, blank=True)
    checking_no = models.CharField(max_length=20, verbose_name='Checking No', null=True, blank=True)
    account_address = models.CharField(max_length=255, verbose_name='Account Address', null=True, blank=True)
    account_to_be_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Bank Account'
        verbose_name_plural = 'Bank Accounts'

    def __str__(self):
        return f"Card - {self.account_name}"

    def save(self, *args, **kwargs):

        if self.account_to_be_used:
            BankAccount.objects.filter(sales=self.sales).exclude(id=self.id).update(account_to_be_used=False)
        super().save(*args, **kwargs)


def validate_credit_card_number(value):
    cleaned_value = value.replace(' ', '').replace('-', '')
    if not cleaned_value.isdigit():
        raise ValidationError('Card number must contain only digits')
    if not (13 <= len(cleaned_value) <= 19):
        raise ValidationError('Invalid card number length')


class Card(models.Model):
    GIFT_CARD_OPTION = [
        ('yes', 'Yes'),
        ('no', 'No')
    ]

    sales = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name='cards')
    card_name = models.CharField(max_length=255, verbose_name='Name on Card', null=True, blank=True)
    billing_address = models.CharField(max_length=255, verbose_name='Billing Address', null=True, blank=True)
    card_no = models.CharField(
        max_length=255,
        verbose_name='Card Number',
        validators=[validate_credit_card_number],
        blank=True
    )
    expiry_month = models.IntegerField(
        verbose_name='Expiry Month',
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    expiry_year = models.IntegerField(
        verbose_name='Expiry Year',
        validators=[MinValueValidator(2023)]
    )
    cvv = models.CharField(max_length=10, verbose_name='CVV', null=True, blank=True)
    gift_card = models.CharField(max_length=10, verbose_name="is it a gift card", choices = GIFT_CARD_OPTION, null=True, blank=True, default="no" )
    card_to_be_used = models.BooleanField(default= False)

    class Meta:

        verbose_name = 'Card'
        verbose_name_plural = 'Cards'

    def clean(self):
        if self.card_to_be_used:
            # Check if any other card for the same sale is already marked as "CARD IN USE"
            if self.__class__.objects.filter(sales=self.sales, card_to_be_used=True).exclude(id=self.id).exists():
                raise ValidationError('Only one card can be marked as "CARD IN USE" for the same sale.')

    # def clean(self):
    #     if self.sales.payment_method == "account":
    #         # If payment method is "account", skip card validation
    #         return
    #     else:
    #         # If payment method is not "account", perform card validation
    #         super().clean()


    def __str__(self):
        return f"Card - {self.card_no}"

    # def save(self, *args, **kwargs):
    #     if self.card_to_be_used:
    #         Card.objects.filter(sales=self.sales).exclude(id=self.id).update(card_to_be_used=False)
    #     super().save(*args, **kwargs)
    #
    # def _update_errors(self, validation_error):
    #     for field, errors in validation_error.error_dict.items():
    #         for error in errors:
    #             self.add_error(field, error)

class PaymentDetail(models.Model):
    sale = models.OneToOneField(Sales, on_delete=models.CASCADE, related_name='payment_detail')
    merchant_name = models.CharField(max_length=255 , verbose_name='Merchant Name', default=timezone.now)
    amount_paid = models.FloatField(verbose_name='Amount Paid')


class Merchants(models.Model):
    merchant_link = models.ForeignKey(
        Gateway,
        on_delete=models.PROTECT,
        verbose_name='Gateway Name',
        related_name='merchant_accounts_link',
        default=0,
    )
    Company_Name = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        verbose_name='Company Name',
        related_name='dba_accounts',
        default=0,
    )
    access_token = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        verbose_name='Access Token'
    )
    login_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Login Id/ Gateway Token'
    )
    def __str__(self):
        return f"{self.merchant_link}"
    class Meta:
        verbose_name_plural = "Merchants"


class Messages(models.Model):
    added_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    sale = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField(verbose_name='Message')
    is_read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:
            if hasattr(self, 'request'):
                self.added_by = self.request.user
        super(Messages, self).save(*args, **kwargs)

    def __str__(self):
        return f"Card - {self.message}"


@receiver(post_save, sender=CustomUser)
def create_or_update_wallet(sender, instance, created, **kwargs):
    if created or not hasattr(instance, 'wallet'):
        print("Creating wallet")
        Wallet.objects.create(user=instance)
    else:
        print("No Wallet")
        pass

class Invoice(models.Model):
    PAYMENT_CHECK_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    sale = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name='Invoice')
    payment = models.CharField(max_length=255, verbose_name='Payment Method')
    security = models.CharField(max_length=255, verbose_name='Security')
    gateway = models.CharField(max_length=255, verbose_name='Gateway')
    Merchant_Name = models.CharField(max_length=255, verbose_name='Merchant')
    payment_check = models.CharField(max_length=3, choices=PAYMENT_CHECK_CHOICES, verbose_name='Payment Check',
                                     default='no')

class Links(models.Model):
    merchant_link = models.ForeignKey(
        Gateway,
        on_delete=models.PROTECT,
        verbose_name='Merchant Name',
        default=0,
        limit_choices_to={'merchant_type': 'link'}
    )

    link = models.CharField(max_length=255, blank=False, null=False, verbose_name='Link')
    amount = models.FloatField(blank=False, null=False, verbose_name='Amount')

    def __str__(self):
        return str(self.merchant_link)
    class Meta:
        verbose_name_plural = "Links"


class SalesUserAssociation(models.Model):
    sale = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name ="associate_users")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='wallet')
    value = models.FloatField(default=0.0)

    def __str__(self):
        return f"Wallet for {self.user.username}"


class WithdrawalRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    message = models.CharField(max_length=255, blank=False, default="Pending", verbose_name='Message')
