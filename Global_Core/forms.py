from django import forms
from models import *


class PaymentDetailForm(forms.ModelForm):
    class Meta:
        model = PaymentDetail
        fields = ['payment_date', 'amount_paid', ...]
