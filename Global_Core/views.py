from django.shortcuts import render
from django.http import HttpResponse
from .authorizepayment import charge_credit_card


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

        response = charge_credit_card(amount, cardNumber, expirationDate, cardCod, firstName, lastName, company, address, state, zip_code)
        return response
        print(response)
    else:
        # Render the HTML template containing the form
        return render(request, 'enter_payment_details.html')
