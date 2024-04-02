from django.contrib import admin
from django import forms
from .models import Sales,Card


class SalesForm(forms.ModelForm):
    class Meta:
        model = Sales
        fields = '__all__'


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

