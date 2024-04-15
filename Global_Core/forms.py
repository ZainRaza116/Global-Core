from django.contrib import admin
from django import forms
from django.core.validators import RegexValidator

from .models import Sales,Card


class SalesForm(forms.ModelForm):
    phone_regex = RegexValidator(
        regex=r'^\(\d{3}\) \d{3}-\d{4}$',
        message="Phone number must be entered in the format: '(555) 555-1234'."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("I have been called")
        self.fields['sales_date'].widget = forms.DateInput(
                    attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['provider_name'].widget = forms.TextInput(
                    attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['added_by'].widget = forms.TextInput(
                    attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['company'].widget = forms.TextInput(
                    attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['btn'].widget = forms.TextInput(
                    attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['payment_method'].widget = forms.TextInput(
                    attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['status'].widget = forms.TextInput(
                    attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['reason'].widget = forms.TextInput(
                    attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['sales_date'].widget = forms.TextInput(
                    attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['customer_name'].widget = forms.TextInput(attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['customer_first_name'].widget = forms.TextInput(
            attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['customer_last_name'].widget = forms.TextInput(
            attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['customer_address'].widget = forms.TextInput(attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['state'].widget = forms.TextInput(attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['zip_code'].widget = forms.TextInput(attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['calling_no'].widget = forms.TextInput(
            attrs={'style': 'width: 45%; display: inline-block;', 'validators': [self.phone_regex]})
        self.fields['customer_email'].widget = forms.EmailInput(attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['ssn'].widget = forms.TextInput(attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['cus_dob'].widget = forms.DateInput(attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['pin'].widget = forms.TextInput(attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['acc_user_name'].widget = forms.TextInput(attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['password'].widget = forms.PasswordInput(attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['amount'].widget = forms.TextInput(attrs={'style': 'width: 45%; display: inline-block;'})
        self.fields['authorization'].widget = forms.FileInput(attrs={'style': 'width: 45%; display: inline-block;'})


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = '__all__'
        widgets = {
            'card_name': forms.TextInput(attrs={'placeholder': 'Enter card number'}),
            'billing_address': forms.TextInput(attrs={'placeholder': 'Billing Address Format : Address , State , Zip'}),
            'card_no': forms.TextInput(attrs={'placeholder': 'Enter Valid Card Number'}),
            'expiry_month': forms.TextInput(attrs={'placeholder': 'Enter Valid Expiry Month'}),
            'expiry_year': forms.TextInput(attrs={'placeholder': 'Enter Valid Expiry Year i-e 2030'}),
            'cvv': forms.TextInput(attrs={'placeholder': 'Enter Valid CVV'}),
            'gift_card': forms.Select(choices=Card.GIFT_CARD_OPTION),

        }

