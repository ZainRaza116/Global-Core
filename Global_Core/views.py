import requests
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .authorizepayment import authorize_credit_card , charge_credit_card
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
        xml_response = charge_credit_card(amount, cardNumber, expirationDate, cardCod, firstName, lastName, company, address, state, zip_code)

        # Redirect the user to the payment page

        # Convert the response XML to a string
        xml_string = ET.tostring(xml_response)

        # Return an HTTP response with the XML string
        return HttpResponse(xml_string, content_type='text/xml')

    else:
        # Render the HTML template containing the form
        return render(request, 'enter_payment_details.html')


def NMI(request):
    if request.method == 'GET':
        # Hardcoded values for testing (replace these with actual values)
        cc_number = '4000000000002701'
        cc_exp = '1212'
        cvv = '999'
        amount = '5.00'

        # Initialize gwapi object
        gw = gwapi()

        # Set your security key
        gw.setLogin("P2DZKaQB7y68s7wQ3yMf9Ap4k4APZG5C")

        # Set hardcoded billing, shipping, and order information
        gw.setBilling("John", "Smith", "Acme, Inc.", "123 Main St", "Suite 200", "Beverly Hills",
                      "CA", "90210", "US", "555-555-5555", "555-555-5556", "support@example.com",
                      "www.example.com")

        gw.setShipping("Mary", "Smith", "na", "124 Shipping Main St", "Suite Ship", "Beverly Hills",
                       "CA", "90210", "US", "support@example.com")

        gw.setOrder("1234", "Big Order", 1, 2, "PO1234",
                    request.META.get('REMOTE_ADDR'))
        # Process the payment
        response_code = gw.doSale(amount, cc_number, cc_exp, cvv)

        # Display response based on the response code
        if int(response_code) == 1:
            return HttpResponse("Payment Approved")
        elif int(response_code) == 2:
            return HttpResponse("Payment Declined")
        elif int(response_code) == 3:
            return HttpResponse("Payment Error")
        else:
            return HttpResponse("Unknown Response")

    else:
        return render(request, 'enter_payment_details.html')


import json
from django.http import JsonResponse
def test(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data sent from the client-side JavaScript
            json_data = json.loads(request.body)
            print(json_data)

            fields = {
                'security_key': 'P2DZKaQB7y68s7wQ3yMf9Ap4k4APZG5C',
                'ccnumber': 4000000000002503,
                'ccexp': json_data['cardExpMonth'] + json_data['cardExpYear'][-2:],
                'amount': '10.00',
                'email': json_data['email'],
                'phone': json_data['phone'],
                'city': json_data['city'],
                'address1': json_data['address1'],
                'country': json_data['country'],
                'first_name': json_data['firstName'],
                'last_name': json_data['lastName'],
                'zip': json_data['postalCode'],
                'cavv': "MTIzNDU2Nzg5MDEyMzQ1Njc4OTA=",
                'xid': json_data.get('xid'),
                'eci': "05",
                'cardholder_auth': "verified",
                'three_ds_version': "2.2.0",
                'directory_server_id': "19304dc2-58e0-497f-8508-f434c45a7a05",
                'cardholder_info': json_data.get('cardHolderInfo')
            }

            # Make POST request using requests library
            response = requests.post('https://secure.networkmerchants.com/api/transact.php', data=fields)

            # Print the response
            print(response.text)
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
                amount=1000  # Amount to capture in cents
            )
            return JsonResponse({'success': True, 'message': 'Payment captured successfully'})
        except stripe.error.StripeError as e:
            return JsonResponse({'success': False, 'message': 'Capture failed. Please try again.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def checkout(request):
    return render(request, 'checkout.html')


paypal_client_id = settings.PAYPAL_CLIENT_ID
paypal_client_secret = settings.PAYPAL_CLIENT_SECRET
print("***********************")
print(paypal_client_id)

def create_payment_paypal(request):
    payment = Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": "http://localhost:8000/payment/execute/",
            "cancel_url": "http://localhost:8000/payment/cancel/"
        },
        "transactions": [{
            "amount": {
                "paypal_client_id" : "settings.PAYPAL_CLIENT_ID",
                "total": "10.00",
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

