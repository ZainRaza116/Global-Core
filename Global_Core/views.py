import requests
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils.datetime_safe import datetime
from django.views.decorators.http import require_POST

from .authorizepayment import authorize_credit_card, charge_credit_card
import lxml.etree as ET
from .tests import gwapi
import stripe
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse
from paypalrestsdk import Payment
from django.conf import settings


def charge_credit_card_view(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        cardNumber = request.POST.get('cardNumber')
        expirationDate = request.POST.get('expirationDate')
        cardCod = request.POST.get('cardCode')
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        company = request.POST.get('company')
        address = request.POST.get('address')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip')

        # Call the authorize_credit_card function to get the XML response
        xml_response = charge_credit_card(amount, cardNumber, expirationDate, cardCod, firstName, lastName, company,
                                          address, state, zip_code)

        # Redirect the user to the payment page

        # Convert the response XML to a string
        xml_string = ET.tostring(xml_response)

        # Return an HTTP response with the XML string
        return HttpResponse(xml_string, content_type='text/xml')

    else:
        # Render the HTML template containing the form
        return render(request, 'enter_payment_details.html')


def NMI(request):
        try:
            fields = {
                'security_key': 'P2DZKaQB7y68s7wQ3yMf9Ap4k4APZG5C',
                'amount': '12.00',
                'ccnumber': '4111111111111111',
                'ccexp': '0124',
                'cvv': '123',
                'order-description': 'Example Charge',
                'type': 'auth',
            }
            # Make POST request using requests library
            response = requests.post('https://secure.networkmerchants.com/api/transact.php', data=fields)
            print("*********************")
            # Print the response
            print(response.text)

            return JsonResponse({'message': response.json()})
        except json.JSONDecodeError:
            # Handle JSON decoding errors
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)



import json
from django.http import JsonResponse


def test(request):
    if request.method == 'POST':
        try:
            print(request.body)
            json_data = json.loads(request.body)
            print(json_data)

            fields = {
                'security_key': 'P2DZKaQB7y68s7wQ3yMf9Ap4k4APZG5C',
                'ccnumber': json_data['cardNumber'],
                'ccexp': json_data['cardExpMonth'] + json_data['cardExpYear'][-2:],
                'amount': json_data['amount'],
                'email': json_data['email'],
                'phone': json_data['phone'],
                'city': json_data['city'],
                'address1': json_data['address1'],
                'country': json_data['country'],
                'first_name': json_data['firstName'],
                'last_name': json_data['lastName'],
                'zip': json_data['postalCode'],
                'cavv': json_data['cavv'],
                'xid': json_data.get('xid'),
                'eci': json_data.get('eci'),
                'cardholder_auth': json_data.get('cardHolderAuth'),
                'three_ds_version': json_data.get('threeDsVersion'),
                'directory_server_id': json_data.get('directoryServerId'),
                'cardholder_info': json_data.get('cardHolderInfo'),
            }

            # Make POST request using requests library
            response = requests.post('https://secure.networkmerchants.com/api/transact.php', data=fields)

            # Print the response

            return JsonResponse({'message': 'Data received successfully'})
        except json.JSONDecodeError:
            # Handle JSON decoding errors
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    return render(request, 'example.html')


stripe.api_key = "sk_test_51OlnMEI2KysFcOYIr0VF0wDzn7MXL3b8gqAMwWgTFTknOfrBif7IlTNybkNVL6MRVnZyfggGyf8DCQejI58HY4TF004pAsr1D1"


def charge(request):
    if request.method == 'GET':
        # Token from the client-side
        token = request.POST.get('stripeToken')

        try:
            # Create a charge
            charge = stripe.Charge.create(
                amount=1000,  # Amount in cents
                currency='usd',
                source=token,
                description='Example charge',
                capture=False  # Set capture to False for authorization
            )
            return JsonResponse({'success': True, 'message': 'Payment authorized'})
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            return JsonResponse({'success': False, 'message': 'Card declined'})
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            return JsonResponse({'success': False, 'message': 'Something went wrong. Please try again.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def capture_payment_stripe(request):
    if request.method == 'POST':
        charge_id = request.POST.get('charge_id')

        try:
            # Capture the payment
            capture = stripe.Charge.capture(
                charge_id,
                amount=1000
            )
            return JsonResponse({'success': True, 'message': 'Payment captured successfully'})
        except stripe.error.StripeError as e:
            return JsonResponse({'success': False, 'message': 'Capture failed. Please try again.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def checkout(request):
    return render(request, 'checkout.html')


# paypal_client_id = settings.PAYPAL_CLIENT_ID
# paypal_client_secret = settings.PAYPAL_CLIENT_SECRET
# print("***********************")
# print(paypal_client_id)


def create_payment_paypal(request):
    payment = Payment({
        "intent": "authorize",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": "http://localhost:8000/payment/execute/",
            "cancel_url": "http://localhost:8000/payment/cancel/"
        },
        "transactions": [{
            "amount": {
                "total": "1.00",
                "currency": "USD"
            },
            "description": "Payment description"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = link.href
                return HttpResponseRedirect(approval_url)
    else:
        print(payment.error)
        return HttpResponse('Payment creation failed')


def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        return HttpResponse('Payment successful')
    else:
        return HttpResponse('Payment failed')


import square


def square_payment(request):
    if request == "POST":
        nonce = request.POST.get('nonce')
        amount = request.POST.get('amount')

        # Set up the request to Square's Payments API
        headers = {
            'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
            'Content-Type': 'application/json'
        }
        data = {
            'source_id': nonce,
            'amount_money': {
                'amount': int(amount),
                'currency': 'USD'
            },
            'idempotency_key': 'UNIQUE_KEY'  # Set a unique key for idempotency
        }
        print("failed")
        # Send the request to charge the card
        try:
            response = requests.post('https://connect.squareup.com/v2/payments', headers=headers, data=json.dumps(data))
            print(response.json())
            if response.status_code == 200:
                return JsonResponse({'success': True, 'message': 'Payment successful'})
            else:
                return JsonResponse({'success': False, 'message': 'Payment failed'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    else:
        return render(request, 'square.html')


from .models import *


def get_merchants(request):

        gateway_id = request.GET.get('gateway_id')
        if gateway_id:
            merchants = Merchants.objects.filter(merchant_link_id=gateway_id).values_list('Company_Name__company_name', flat=True)
            return JsonResponse(list(merchants), safe=False)
        else:
            return JsonResponse([], safe=False)


# def get_details_view(request, object_id):
#     try:
#         sales = get_object_or_404(Sales, pk=object_id)
#         security_option = request.GET.get('security')
#         payment_method = request.GET.get('payment_method')
#         gateway = request.GET.get('gateway')
#         merchant = request.GET.get('merchant')
#
#         details = {
#             'invoice_id': invoice_id,
#             'object_id': object_id,
#             'security_option': security_option,
#             'payment_method': payment_method,
#             'gateway': gateway,
#             'merchant': merchant
#         }
#         return JsonResponse(details)
#     except Sales.DoesNotExist:
#         return JsonResponse({'error': 'Sales object does not exist'}, status=404)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)

def invoice(request, invoice_id):
    invoice_object = get_object_or_404(Invoice, pk=invoice_id)
    gateway = invoice_object.gateway
    sale_object = invoice_object.sale
    selected_card = sale_object.cards.filter(card_to_be_used=True).first()
    date = datetime.now().date()
    sale_id = sale_object.id
    payment = invoice_object.payment

    contex = {
        "object_id": sale_id,
        "gateway": gateway,
        "invoice_id": invoice_id,
        "invoice_object": invoice_object,
        "date": date,
        'sale': sale_object,
        'cards': selected_card,
        'payment_method': payment
    }
    return render(request, 'invoice.html', contex)


@require_POST
def mark_as_read(request, message_id):
        message = Messages.objects.get(pk=message_id)
        message.is_read = True
        message.save()
        return JsonResponse({'success': True})

