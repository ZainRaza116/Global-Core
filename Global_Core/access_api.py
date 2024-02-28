from django.shortcuts import get_object_or_404
from .models import Gateway , Merchants


def get_gateway_merchants(gateway_id):
    # Retrieve the selected gateway
    gateway = get_object_or_404(Gateway, pk=gateway_id)

    # Retrieve all merchants associated with the gateway
    merchants = gateway.merchant_set.all()

    return merchants


def get_merchant_api_key(merchant_id):
    # Retrieve the selected merchant
    merchant = get_object_or_404(Merchants, pk=merchant_id)

    # Retrieve and return the API key from the merchant
    return merchant.access_token


def get_merchant_login_key(merchant_id):
    # Retrieve the selected merchant
    merchant = get_object_or_404(Merchants, pk=merchant_id)

    # Retrieve and return the API key from the merchant
    return merchant.login_id
