# views.py
from django.shortcuts import render
from django.contrib import messages
from .models import Sales
from .authorize_net import authorize_credit_card


def enter_payment_details(request):
    if request.method == 'POST':
        # Extract payment information from the form
        card_number = request.POST.get('card_number')
        expiration_date = request.POST.get('expiration_date')
        card_code = request.POST.get('card_code')
        amount = request.POST.get('amount')

        # Call the authorize_credit_card function with the provided payment details
        response = authorize_credit_card(card_number, expiration_date, card_code, amount)

        # Process the response from Authorize.Net and return an appropriate response
        if response:
            # Payment authorization successful
            return JsonResponse({'message': 'Payment authorized successfully'})
        else:
            # Payment authorization failed
            return JsonResponse({'error': 'Payment authorization failed'})

    return render(request, 'enter_payment_details.html')
