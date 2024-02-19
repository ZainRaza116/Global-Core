import requests
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .authorizepayment import authorize_credit_card , charge_credit_card
import lxml.etree as ET
from .tests import gwapi


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
    if request.method == 'POST':
        # Hardcoded values for testing (replace these with actual values)
        cc_number = '4111111111111111'
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
        response_code = gw.authorize(amount, cc_number, cc_exp, cvv)

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

            fields = {
                'security_key': 'P2DZKaQB7y68s7wQ3yMf9Ap4k4APZG5C',
                'ccnumber': json_data['cardNumber'],
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
                'cavv': json_data.get('cavv'),
                'xid': json_data.get('xid'),
                'eci': json_data.get('eci'),
                'cardholder_auth': json_data.get('cardHolderAuth'),
                'three_ds_version': json_data.get('threeDsVersion'),
                'directory_server_id': json_data.get('directoryServerId'),
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