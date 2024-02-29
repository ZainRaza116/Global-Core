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
from .stripe_payment import authorize_stripe, charge_stripe
import stripe,json
get_user_model()
from django.shortcuts import render
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest
from .access_api import get_merchant_api_key , get_merchant_login_key


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
from django.forms.models import BaseInlineFormSet


class AccountInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        in_use_count = sum(1 for form in self.forms if form.cleaned_data.get('account_to_be_used'))
        if in_use_count == 0:
            raise ValidationError("At least one Account must be marked as in use.")


class CardInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        in_use_count = sum(1 for form in self.forms if form.cleaned_data.get('card_to_be_used'))
        if in_use_count == 0:
            raise ValidationError("At least one card must be marked as in use.")


class CardInline(admin.StackedInline):
    model = Card
    extra = 1
    formset = CardInlineFormSet


class BankAccountInline(admin.StackedInline):
    model = BankAccount
    extra = 1
    forms = AccountInlineFormSet


class SalesAdmin(admin.ModelAdmin):
    # inlines = [CardInline, BankAccountInline]
    change_form_template = 'admin/sales/change_form.html'

    # class Media:
    #     js = ('admin/dynamic_inline.js',)

    inlines = [CardInline, BankAccountInline]

    list_display = ['customer_name', "customer_address", "amount", "payment_method", "added_by" , "custom_action"]

    def get_urls(self):

        urls = super().get_urls()
        my_urls = [
            path("<int:object_id>/payment/", self.admin_site.admin_view(self.my_view)),
            path("<int:object_id>/payment/3D_secure/<int:merchant_id>", self.admin_site.admin_view(self.secure),
                 name="secure"),
            path("<int:object_id>/payment/paypal/<int:merchant_id>", self.admin_site.admin_view(self.paypal), name="paypal"),
            path("<int:object_id>/payment/authorize_paypal/<int:merchant_id>", self.admin_site.admin_view(self.authorize_paypal), name="authorize_paypal"),
        ]
        return my_urls + urls

    def authorize_paypal(self, request, object_id, merchant_id, *args, **kwargs):

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
            client_id = get_merchant_api_key(merchant_id)
            client_secret = get_merchant_login_key(merchant_id)
            environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
            client = PayPalHttpClient(environment)
            # Create PayPal order
            create_request = OrdersCreateRequest()
            create_request.prefer("return=representation")
            create_request.request_body({
                "intent": "AUTHORIZE",
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

    def paypal(self, request, object_id , merchant_id):
        sales = Sales.objects.get(pk=object_id)
        if request.method == 'POST':
            # Verify IPN data with PayPal (optional but recommended)
            # Process the IPN data
            ipn_data = request.POST.dict()

            # Perform actions based on the IPN data, such as updating database records
            # Example: Log IPN data to console
            print("Received PayPal IPN:")
            print(json.dumps(ipn_data, indent=4))

            return HttpResponse(status=200)
        else:
            client_id = get_merchant_api_key(merchant_id)
            client_secret = get_merchant_login_key(merchant_id)
            environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
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

    def secure(self, request, object_id, merchant_id):

        if request.method == 'POST':
            try:
                print(request.body)
                json_data = json.loads(request.body)
                print(json_data)

                fields = {
                    'security_key': get_merchant_api_key(merchant_id),
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
        # expiration_date = selected_card.expire_date
        expiration_month = selected_card.expiry_month
        expiration_year = selected_card.expiry_year
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
            gateway_info = request.POST.get('gateway')
            gateway_id, gateway = gateway_info.split(",")
            merchant = request.POST.get('merchant')
            security = request.POST.get("security")
            amount = sales.amount
            credit_card_number = selected_card.card_no
            cardNumber = credit_card_number.replace(" ", "")
            expirationMonth = selected_card.expiry_month
            expirationYear = selected_card.expiry_year
            cardCod = selected_card.cvv
            firstName = sales.customer_first_name
            lastName = sales.customer_last_name
            company = sales.customer_name
            address = sales.customer_address
            state = 'NY'
            zip_code = '657899762'
            merchant_id = Merchants.objects.filter(
                merchant_link_id=gateway_id,
                Company_Name__company_name= merchant
            ).values_list('id', flat=True).first()
            print(payment_method)
            print(merchant_id)
            if payment_method == 'Sale' and gateway == 'Authorize.net':
                expirationDate = f"{expirationMonth}/{expirationYear}"
                xml_response = charge_credit_card(amount, cardNumber, expirationDate, cardCod, firstName, lastName,
                                                  company,
                                                  address, state, zip_code , merchant_id)
                # xml_string = ET.tostring(xml_response)
                return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))

            elif payment_method == 'Authorize' and gateway == 'Authorize.net':
                expirationDate = f"{expirationMonth}/{expirationYear}"
                xml_response = authorize_credit_card(amount, cardNumber, expirationDate, cardCod, firstName, lastName,
                                                     company,
                                                     address, state, zip_code ,merchant_id )
                xml_string = ET.tostring(xml_response)
                return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))
            # **************************  STRIPE  ******************************
            elif payment_method == 'Authorize' and gateway == 'Stripe':
                try:
                    amount = amount
                    print(amount)
                    authorize_stripe(amount, merchant_id)
                    # Assuming your view name is 'payment_view' and it expects an 'object_id' parameter
                    return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))
                except Exception as e:
                    error_message = "An error occurred: {}".format(e)
                    print("Error:", error_message)
                    return JsonResponse({'error': error_message}, status=500)
            elif payment_method == 'Sale' and gateway == 'Stripe':
                try:
                    amount = amount
                    print(amount)
                    charge_stripe(amount, merchant_id)
                    return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))
                except Exception as e:
                    error_message = "An error occurred: {}".format(e)
                    print("Error:", error_message)
                    return JsonResponse({'error': error_message}, status=500)
            elif payment_method == 'Authorize' and gateway == 'NMI':
                try:
                    expirationDate = f"{expirationMonth}/{expirationYear}"
                    fields = {
                        'security_key': get_merchant_api_key(merchant_id),
                        'amount': amount,
                        'ccnumber': credit_card_number,
                        'ccexp': expirationDate,
                        'cvv': cardCod,
                        'order-description': 'Example Charge',
                        'type': 'auth',
                    }
                    response = requests.post('https://secure.networkmerchants.com/api/transact.php', data=fields)
                    print("*********************")
                    # Print the response
                    print(response.text)

                    return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))
                except json.JSONDecodeError:
                    return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))

            elif security == '2D' and payment_method == 'Sale' and gateway == 'NMI':
                try:
                    expirationDate = f"{expirationMonth}/{expirationYear}"
                    fields = {
                        'security_key': get_merchant_api_key(merchant_id),
                        'amount': amount,
                        'ccnumber': credit_card_number,
                        'ccexp': expirationDate,
                        'cvv': cardCod,
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
                check = get_merchant_login_key(merchant_id)
                print("****************")
                print(check)
                # if check is None:
                #     return JsonResponse({'error': 'No GateWay Key'}, status=500)
                # else:
                return redirect('/admin/Global_Core/sales/{}/payment/3D_secure/{}'.format(object_id, merchant_id))

            elif payment_method == 'Sale' and gateway == 'PayPal':
                return redirect('/admin/Global_Core/sales/{}/payment/paypal/{}'.format(object_id,merchant_id))
            elif payment_method == 'Authorize' and gateway == 'PayPal':
                return redirect('/admin/Global_Core/sales/{}/payment/authorize_paypal/{}'.format(object_id, merchant_id))
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
            selected_account = sales.Accounts.filter(account_to_be_used=True).first()
            print(selected_account)
            if sales.payment_method == 'Account':
                selected_card= None
            else:
                selected_account = sales.Accounts.filter(account_to_be_used=True).first()

            print("*********")
            print(selected_card)

            # selected_card = cards_account.objects.filter(card_to_be_used=True).first()
            today_date = datetime.now().date()
            gateway = Gateway.objects.all()

            context = {
                'client_info': customer_info,
                'today_date': today_date,
                'cards': selected_card,
                'account': selected_account,
                'gateway': gateway,
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
admin.site.register(Merchants)
admin.site.register(Gateway, MerchantsAdmin)
# admin.site.register(Sales)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Dashboard)
# admin.site.register(urls)
