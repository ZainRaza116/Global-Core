from django import forms
from django.core.validators import RegexValidator
from .models import Sales


class SalesForm(forms.ModelForm):
    # Define a regex pattern for American phone numbers
    phone_regex = RegexValidator(
        regex=r'^\(\d{3}\) \d{3}-\d{4}$',
        message="Phone number must be entered in the format: '(555) 555-1234'."
    )

    # Add the phone number field with the validator
    calling_no = forms.CharField(
        validators=[phone_regex],
        max_length=15,
        required=False,
        label='Phone Number'
    )

    class Meta:
        model = Sales
        fields = '__all__'  # or specify the fields you want to include in the form
