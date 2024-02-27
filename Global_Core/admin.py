from django.contrib import admin
import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils.html import format_html
from django.utils.safestring import mark_safe
# from stripe._account.Account.Settings import Payments
from .models import *
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.models import Group
from django.contrib.admin import AdminSite
# from . import urls
from datetime import datetime
from django.core.serializers import serialize
import lxml.etree as ET
from .authorizepayment import authorize_credit_card, charge_credit_card
from .stripe_payment import authorize_stripe
import stripe,json
get_user_model()
import squareup

stripe.api_key = "sk_test_51OlnMEI2KysFcOYIr0VF0wDzn7MXL3b8gqAMwWgTFTknOfrBif7IlTNybkNVL6MRVnZyfggGyf8DCQejI58HY4TF004pAsr1D1"

from django.shortcuts import render
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest

class CustomUserAdminForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(),
                                            widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    verbose_name_plural = 'Employees'
    list_display = ('email', 'salary', 'target', 'hiring_date')

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'

    form = CustomUserAdminForm

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('salary', 'target', 'hiring_date')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active', 'groups')}
        ),
    )
    ordering = ('email',)


class MerchantsAdmin(admin.ModelAdmin):
    list_display = ['merchant', 'merchant_dba', 'account_type', 'merchant_type']


class LinksAdmin(admin.ModelAdmin):
    list_display = ['merchant_link', 'link', 'amount']


class ExpensesAdmin(admin.ModelAdmin):
    list_display = ['date_incurred', 'title', 'amount', 'expenses_type']
from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .models import Sales


class CardInline(admin.StackedInline):
    model = Card
    extra = 1


class BankAccountInline(admin.StackedInline):
    model = BankAccount
    extra = 1


class SalesAdmin(admin.ModelAdmin):
    # inlines = [CardInline, BankAccountInline]
    change_form_template = 'admin/sales/change_form.html'

    def get_inline_instances(self, request, obj=None):
        if obj is None:  # If adding a new object
            default_payment_method = 'card'
            if default_payment_method == 'card':
                return [CardInline(self.model, self.admin_site)]
            elif default_payment_method == 'account':
                return [BankAccountInline(self.model, self.admin_site)]
            else:
                return []

        print("Payment Method:", obj.payment_method)  # Debug print

        if obj.payment_method == 'card':
            return [CardInline(Card, self.admin_site)]
        elif obj.payment_method == 'account':
            return [BankAccountInline(BankAccount, self.admin_site)]

        return []

    list_display = ['customer_name', "customer_address", "amount", "payment_method", "added_by" , "custom_action"]

    def get_urls(self):

        urls = super().get_urls()
        my_urls = [
            path("<int:object_id>/payment/", self.admin_site.admin_view(self.my_view)),
            path("<int:object_id>/payment/3D_secure", self.admin_site.admin_view(self.secure), name="secure"),
            path("<int:object_id>/payment/paypal", self.admin_site.admin_view(self.paypal), name="paypal"),
            path("<int:object_id>/payment/authorize_paypal", self.admin_site.admin_view(self.authorize_paypal), name="authorize_paypal")
        ]
        return my_urls + urls

    def authorize_paypal(request, object_id):
        sales = Sales.objects.get(pk=object_id)
        environment = SandboxEnvironment(
            client_id='AWTbh99Ts8lmshPbMfSB1XNNaSW9cwhNX6dMr-1ubyge1n3UgK4b2e6dtDcqdxcUz1sTO1ihwQsXc76O',
            client_secret='EMX8JMUA00riKFopJ4ZNB7jbJq5grLyV_DohOUfFAj14nvDb2WhcR7fK2QRw4npzyRNjKmgSYg1sTg0Z')
        client = PayPalHttpClient(environment)

        create_request = OrdersCreateRequest()
        create_request.prefer("return=representation")
        create_request.request_body({
            "intent": "AUTHORIZE",  # Set intent to AUTHORIZE for card authorization
            "purchase_units": [{
                "amount": {
                    "currency_code": "USD",
                    "value": sales.amount  # You can make this dynamic based on your requirements
                }
            }]
        })

        try:
            response = client.execute(create_request)
            order_id = response.result.id
            return render(request, 'paypal.html', {'order_id': order_id, 'object_id': object_id, 'sales': sales})
        except Exception as e:
            print({'error_message': str(e)})
            return render(request, 'error.html', {'error_message': str(e)})
    def paypal(self, request, object_id):
        sales = Sales.objects.get(pk=object_id)
        if request.method == 'POST':
            # Verify IPN data with PayPal (optional but recommended)
            # Process the IPN data
            ipn_data = request.POST.dict()

            # Perform actions based on the IPN data, such as updating database records
            # Example: Log IPN data to console
            print("Received PayPal IPN:")
            print(json.dumps(ipn_data, indent=4))

            # Return HTTP 200 OK status to acknowledge receipt of IPN
            return HttpResponse(status=200)
        else:
            environment = SandboxEnvironment(client_id='AWTbh99Ts8lmshPbMfSB1XNNaSW9cwhNX6dMr-1ubyge1n3UgK4b2e6dtDcqdxcUz1sTO1ihwQsXc76O', client_secret='EMX8JMUA00riKFopJ4ZNB7jbJq5grLyV_DohOUfFAj14nvDb2WhcR7fK2QRw4npzyRNjKmgSYg1sTg0Z')
            client = PayPalHttpClient(environment)
            # Create PayPal order
            create_request = OrdersCreateRequest()
            create_request.prefer("return=representation")
            create_request.request_body({
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": "USD",
                        "value": sales.amount  # You can make this dynamic based on your requirements
                    }
                }]
            })

            try:
                response = client.execute(create_request)
                order_id = response.result.id
                ipn_data = request.POST.dict()
                print("Received PayPal IPN:")
                print(json.dumps(ipn_data, indent=4))
                return render(request, 'paypal.html', {'order_id': order_id, 'object_id': object_id, 'sales': sales})
            except Exception as e:
                print({'error_message': str(e)})
                return render(request, 'error.html', {'error_message': str(e)})

    def secure(self, request, object_id):

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
                print(response.text)
                return JsonResponse({'message': 'Data received successfully'})
            except json.JSONDecodeError:
                # Handle JSON decoding errors
                return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

        sales = Sales.objects.get(pk=object_id)
        selected_card = sales.cards.filter(card_to_be_used=True).first()
        expiration_date = selected_card.expire_date
        expiration_month = expiration_date.strftime("%m")
        expiration_year = expiration_date.strftime("%Y")
        print(expiration_month, expiration_year)

        customer_info = {
            'customer_name': sales.customer_name,
            'customer_address': sales.customer_address,
            'customer_email': sales.customer_email,
            'amount': sales.amount,
            'phone': sales.calling_no,
            'address': sales.customer_address,
            'f_name': sales.customer_first_name,
            'l_name': sales.customer_last_name,
            'exp_mon': expiration_month,
            'exp_year': expiration_year
        }
        context = {
            'object_id': object_id,
            'selected_card': selected_card,
            'customer_info': customer_info,

        }
        # Render the template with the context and return an HttpResponse object
        return render(request, "example.html", context)

    def my_view(self, request, object_id):
        if request.method == 'POST':
            sales = Sales.objects.get(pk=object_id)
            charge_id = request.POST.get('charge_id')
            selected_card = sales.cards.filter(card_to_be_used=True).first()
            payment_method = request.POST.get('payment_method')
            gateway = request.POST.get('gateway')
            security = request.POST.get("security")
            print(security)
            amount = sales.amount
            credit_card_number = selected_card.card_no
            cardNumber = credit_card_number.replace(" ", "")
            expirationDate1 = selected_card.expire_date
            cardCod = selected_card.cvv
            firstName = sales.customer_first_name
            lastName = sales.customer_last_name
            company = sales.customer_name
            address = sales.customer_address
            state = 'NY'
            zip_code = '657899762'
            print(payment_method)
            if payment_method == 'Sale' and gateway == 'Authorize.net':
                expirationDate = expirationDate1.strftime("%m%d")
                xml_response = charge_credit_card(amount, cardNumber, expirationDate, cardCod, firstName, lastName,
                                                  company,
                                                  address, state, zip_code)
                # xml_string = ET.tostring(xml_response)
                return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))

            elif payment_method == 'Authorize' and gateway == 'Authorize.net':
                expirationDate = expirationDate1.strftime("%m%d")
                xml_response = authorize_credit_card(amount, cardNumber, expirationDate, cardCod, firstName, lastName,
                                                     company,
                                                     address, state, zip_code)
                xml_string = ET.tostring(xml_response)
                return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))
            # **************************  STRIPE  ******************************
            elif payment_method == 'Authorize' and gateway == 'Stripe':
                try:
                    amount = amount
                    print(amount)
                    authorize_stripe(amount)
                    # Assuming your view name is 'payment_view' and it expects an 'object_id' parameter
                    return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))
                except Exception as e:
                    error_message = "An error occurred: {}".format(e)
                    print("Error:", error_message)
                    return JsonResponse({'error': error_message}, status=500)
            elif payment_method == 'Authorize' and gateway == 'NMI':
                try:
                    expirationDate = expirationDate1.strftime("%m%d")
                    fields = {
                        'security_key': 'P2DZKaQB7y68s7wQ3yMf9Ap4k4APZG5C',
                        'amount': amount,
                        'ccnumber': credit_card_number,
                        'ccexp': expirationDate,
                        'cvv': '123',
                        'order-description': 'Example Charge',
                        'type': 'auth',
                    }
                    return fields
                    response = requests.post('https://secure.networkmerchants.com/api/transact.php', data=fields)
                    print("*********************")
                    # Print the response
                    print(response.text)

                    return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))
                except json.JSONDecodeError:
                    return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))

            elif security == '2D' and payment_method == 'Sale' and gateway == 'NMI':
                try:
                    expirationDate = expirationDate1.strftime("%m%d")
                    fields = {
                        'security_key': 'P2DZKaQB7y68s7wQ3yMf9Ap4k4APZG5C',
                        'amount': amount,
                        'ccnumber': credit_card_number,
                        'ccexp': expirationDate,
                        'cvv': '123',
                        'order-description': 'Example Charge',

                    }

                    response = requests.post('https://secure.networkmerchants.com/api/transact.php', data=fields)
                    print("*********************")
                    # Print the response
                    print(response.text)

                    return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))
                except json.JSONDecodeError:
                    return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))

            elif security == '3D' and gateway == 'NMI':
                print(object_id)
                return redirect('/admin/Global_Core/sales/{}/payment/3D_secure'.format(object_id))

            elif payment_method == 'Sale' and gateway == 'PayPal':
                return redirect('/admin/Global_Core/sales/{}/payment/paypal'.format(object_id))
            elif payment_method == 'Authorize' and gateway == 'PayPal':
                return redirect('/admin/Global_Core/sales/{}/payment/authorize_paypal'.format(object_id))
            elif payment_method == 'Sale' and gateway == 'Square':
                    square_client = square.Client(access_token=settings.SQUARE_ACCESS_TOKEN)

                    # Handle form submission or other triggers for payment processing
                    # For example, retrieve the amount from the form data
                    amount = request.POST.get('amount')

                    try:
                        # Create a payment using Square API
                        response = square_client.payments.create({
                            "source_id": request.POST.get('nonce'),  # Payment nonce generated by Square payment form
                            "amount_money": {
                                "amount": amount,
                                "currency": "USD"
                            },
                            "idempotency_key": "<YOUR_IDEMPOTENCY_KEY>"
                        })

                        # Handle successful payment
                        if response.is_success():
                            # Payment successful, update database or display success message
                            return HttpResponse("Payment successful!")
                        else:
                            # Payment failed, display error message
                            return HttpResponse("Payment failed: " + response.errors)
                    except square.exceptions.ApiError as e:
                        # Handle API errors
                        return HttpResponse("API error: " + str(e))
            else:
                return JsonResponse({'error': 'Invalid payment method or gateway'})

        else:
            try:
                sales = Sales.objects.get(pk=object_id)
            except Sales.DoesNotExist:
                return JsonResponse({'error ; "Sale" does not exist'}, status=400)

            customer_info = {
                'customer_name': sales.customer_name,
                'customer_address': sales.customer_address,
                'customer_email': sales.customer_email,
                'amount': sales.amount
            }

            selected_card = sales.cards.filter(card_to_be_used=True).first()
            # selected_card = cards_account.objects.filter(card_to_be_used=True).first()
            today_date = datetime.now().date()
            merchants = Merchants.objects.all()

            context = {
                'client_info': customer_info,
                'today_date': today_date,
                'cards': selected_card,
                'merchants': merchants,
                'object_id': object_id
            }

            return render(request, "enter_payment_details.html", context)

    def custom_action(self, obj):

        image_url = '/static/credit-card.png'  # Update the image path if needed
        return format_html(
            '<a href="{}"><div style="max-height: 20px; max-width: 20px;'
            ' overflow: hidden;"><img src="{}" alt="Credit Card Logo" style="width: 100%; height: auto;" /></div></a>',
            f"/admin/Global_Core/sales/{obj.id}/payment/", image_url)

    custom_action.short_description = 'Actions'


class MyAdminSite(AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('enter_payment_details/<int:sales_id>/', self.enter_payment_details, name='enter_payment_details'),
        ]
        return custom_urls + urls


my_admin_site = MyAdminSite()


admin.site.register(Sales, SalesAdmin)
admin.site.register(Expenses, ExpensesAdmin)
admin.site.register(Company)
admin.site.register(Links, LinksAdmin)
admin.site.register(Accounts)
admin.site.register(Merchants, MerchantsAdmin)
# admin.site.register(Sales)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Dashboard)
# admin.site.register(urls)
