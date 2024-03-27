from django.contrib import admin
from django import forms
from .models import Sales,Card


class SalesForm(forms.ModelForm):
    class Meta:
        model = Sales
        fields = '__all__'
        widgets = {
            'cus_dob': forms.TextInput(attrs={'placeholder': 'Date Format YYYY-MM-DD'}),
            'sales_date': forms.DateInput(attrs={'type': 'date'}),
            'customer_name': forms.TextInput(attrs={'style': 'width: 45%; display: inline-block;'}),
            'customer_first_name': forms.TextInput(attrs={'style': 'width: 45%; display: inline-block;'}),
            'customer_last_name': forms.TextInput(attrs={'style': 'width: 45%; display: inline-block;'}),
            'customer_address': forms.TextInput(attrs={'style': 'width: 45%; display: inline-block;'}),
            'state': forms.Select(attrs={'style': 'width: 45%; display: inline-block;'}),
            'zip_code': forms.TextInput(attrs={'style': 'width: 50%; display: inline-block;'}),
            'btn': forms.TextInput(attrs={'style': 'width: 50%; display: inline-block;'}),
            'calling_no': forms.TextInput(attrs={'style': 'width: 50%; display: inline-block;'}),
            'customer_email': forms.EmailInput(attrs={'style': 'width: 50%; display: inline-block;'}),
            'ssn': forms.TextInput(attrs={'style': 'width: 50%; display: inline-block;'}),
            'cus_dob': forms.DateInput(attrs={'type': 'date', 'style': 'width: 50%; display: inline-block;'}),
            'pin': forms.TextInput(attrs={'style': 'width: 50%; display: inline-block;'}),
            'acc_user_name': forms.TextInput(attrs={'style': 'width: 50%; display: inline-block;'}),
            'password': forms.TextInput(attrs={'style': 'width: 50%; display: inline-block;'}),
            'amount': forms.NumberInput(attrs={'style': 'width: 50%; display: inline-block;'}),
            'payment_method': forms.Select(attrs={'style': 'width: 50%; display: inline-block;'}),
            'status': forms.Select(attrs={'style': 'width: 50%; display: inline-block;'}),
            'reason': forms.TextInput(attrs={'style': 'width: 50%; display: inline-block;'}),
            'description': forms.Textarea(attrs={'style': 'width: 50%; display: inline-block;'}),
            'authorization': forms.FileInput(attrs={'style': 'width: 50%; display: inline-block;'}),
        }


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

        }
