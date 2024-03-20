import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from .models import *
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.models import Group
from datetime import datetime
import lxml.etree as ET
from .authorizepayment import authorize_credit_card, charge_credit_card
from .stripe_payment import authorize_stripe, charge_stripe
import json
from django.shortcuts import render
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest
from .access_api import get_merchant_api_key, get_merchant_login_key
from .permission import IsEmployeePermission
from django.contrib import admin
from django.urls import path
from .models import Sales
from django.forms.models import BaseInlineFormSet

c_user = get_user_model()
print(get_user_model())

class CustomUserAdminForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(),
                                            widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    verbose_name_plural = 'Employees'
    list_display = ('Name', 'email', 'salary', 'target', 'hiring_date')

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])

    get_groups.short_description = 'Groups'

    form = CustomUserAdminForm

    fieldsets = (
        (None, {'fields': ('Name','email', 'password')}),
        ('Personal info', {'fields': ('salary', 'target', 'hiring_date')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('Name', 'email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active', 'groups')}
         ),
    )
    ordering = ('email',)


class GatewayAdmin(admin.ModelAdmin):
    list_display = ['merchant', 'merchant_dba', 'account_type', 'merchant_type']


class MerchantAdmin(admin.ModelAdmin):
    list_display = ['merchant_link', 'Company_Name']


class LinksAdmin(admin.ModelAdmin):
    list_display = ['merchant_link', 'link', 'amount']


class ExpensesAdmin(admin.ModelAdmin):
    list_display = ['date_incurred', 'title', 'amount', 'expenses_type']


# class AccountInlineFormSet(BaseInlineFormSet):
#     def clean(self):
#         super().clean()
#         in_use_count = sum(1 for form in self.forms if form.cleaned_data.get('account_to_be_used'))
#         if in_use_count == 0:
#             raise ValidationError("At least one Account must be marked as in use.")
#
#
# class CardInlineFormSet(BaseInlineFormSet):
#     def clean(self):
#         super().clean()
#         in_use_count = sum(1 for form in self.forms if form.cleaned_data.get('card_to_be_used'))
#         if in_use_count == 0:
#             raise ValidationError("At least one card must be marked as in use.")


class CardInline(admin.StackedInline):
    model = Card
    extra = 0
    # formset = CardInlineFormSet


class BankAccountInline(admin.StackedInline):
    model = BankAccount
    extra = 0
    # forms = AccountInlineFormSet


class SalesAdmin(admin.ModelAdmin):
    change_form_template = 'admin/sales/change_form.html'
    inlines = [CardInline, BankAccountInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields['added_by'].disabled = True
            form.base_fields['added_by'].initial = request.user.id
        return form

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        return inline_instances

    def get_queryset(self, request):
        user = request.user
        if user.is_superuser:
            return super().get_queryset(request)
        else:
            return Sales.objects.filter(added_by=user)
    #     return super().get_queryset(request)

    def get_list_display(self, request):
        if request.user.is_superuser:
            return ['customer_name', "customer_address", "amount", "payment_method", "added_by", "pay",
                    "custom_action12"]
        else:
            return ['customer_name', "customer_address", "amount", "payment_method", "added_by", "custom_action12"]

    def pay(self, obj):
        payment_image_url = '/static/credit-card.png'
        payment_html = format_html(
            '<a href="{}"><img src="{}" alt="Payment" style="justify_content:center; max-height: 20px; '
            'max-width: 20px; '
            'margin-right: 5px;" /></a>',
            f"/admin/Global_Core/sales/{obj.id}/payment/", payment_image_url)
        return payment_html

    def custom_action12(self, obj):
        payment_image_url = '/static/credit-card.png'
        details_image_url = '/static/reply-message.png'
        status_image_url = '/static/loading.png'

        if obj.status == 'pending' or obj.status == 'in_process':
            status_html = format_html(
                '<img src="{}" alt="Status" style="max-height: 20px; max-width: 20px; margin-right: 5px;'
                ' cursor: pointer;" onclick="alert(\'You want to change your status to Completed?\')" />',
                status_image_url)
        else:
            status_html = format_html(
                '<a><img src="{}" alt="Status" style="max-height: 20px; max-width: 20px; '
                'margin-right: 5px;" /></a>',
                '/static/complete.png')

        message = obj.messages.first()
        if message and not message.is_read:
            details_image_url = '/static/notification_12299644.png'
            details_html = format_html(
                '<a href="{}?mark_as_read={}"><img src="{}" alt="View Details" style="max-height:'
                ' 20px; max-width: 20px; margin-right: 5px;" /></a>',
                f"/admin/Global_Core/sales/{obj.id}/response/", message.id, details_image_url)
        else:
            details_html = format_html(
                '<a href="{}"><img src="{}" alt="View Details" style="max-height:'
                ' 20px; max-width: 20px; margin-right: 5px;" /></a>',
                f"/admin/Global_Core/sales/{obj.id}/response/", details_image_url)

        return format_html(
            '<div style="display: flex;">'
            '{}{}'
            '</div>',
             details_html, status_html)

    custom_action12.short_description = 'Actions'


    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("<int:object_id>/payment/", self.admin_site.admin_view(self.my_view)),
            path("<int:object_id>/payment/3D_secure/<int:merchant_id>", self.admin_site.admin_view(self.secure),
                 name="secure"),
            path("<int:object_id>/payment/paypal/<int:merchant_id>", self.admin_site.admin_view(self.paypal),
                 name="paypal"),
            path("<int:object_id>/payment/authorize_paypal/<int:merchant_id>",
                 self.admin_site.admin_view(self.authorize_paypal), name="authorize_paypal"),
            path("<int:object_id>/response/", self.admin_site.admin_view(self.custom_response)),
            path("details/", self.admin_site.admin_view(self.get_details_view),
                 name="get_details_view")
        ]
        return my_urls + urls

    def custom_response(self, request, object_id):
        if request.method == "POST":
            message_text = request.POST.get("message")
            if message_text:
                sales = Sales.objects.get(pk=object_id)
                message = Messages.objects.create(added_by=request.user, sale=sales, message=message_text)
                return redirect('/admin/Global_Core/sales/')
        elif request.method == "GET" and 'mark_as_read' in request.GET:
            message_id = request.GET.get('mark_as_read')
            message = Messages.objects.get(pk=message_id)
            message.is_read = True
            message.save()
            sales = Sales.objects.get(pk=object_id)
            messages_all = sales.messages.all().order_by('timestamp')
            response = sales.description
            print(messages_all)
            context = {
                'message': messages_all,
                'object_id': object_id,
                'sales': sales,
                'response': response
            }
            return render(request, "response.html", context)

        sales = Sales.objects.get(pk=object_id)
        messages_all = sales.messages.all().order_by('timestamp')
        response = sales.description
        print(messages_all)
        context = {
            'message': messages_all,
            'object_id': object_id,
            'sales': sales,
            'response': response
        }
        return render(request, "response.html", context)

    def authorize_paypal(self, request, object_id, merchant_id, *args, **kwargs):

        sales = Sales.objects.get(pk=object_id)
        if request.method == 'POST':
            ipn_data = request.POST.dict()
            print("Received PayPal IPN:")
            print(json.dumps(ipn_data, indent=4))
            return HttpResponse(status=200)
        else:
            client_id = get_merchant_api_key(merchant_id)
            client_secret = get_merchant_login_key(merchant_id)
            environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
            client = PayPalHttpClient(environment)
            create_request = OrdersCreateRequest()
            create_request.prefer("return=representation")
            create_request.request_body({
                "intent": "AUTHORIZE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": "USD",
                        "value": sales.amount
                    }
                }]
            })

    def paypal(self, request, object_id, merchant_id):
        sales = Sales.objects.get(pk=object_id)
        if request.method == 'POST':
            ipn_data = request.POST.dict()
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
                        "value": sales.amount
                    }
                }]
            })

            try:
                response = client.execute(create_request)
                order_id = response.result.id
                ipn_data = request.POST.dict()
                print("Received PayPal IPN:")
                print(json.dumps(ipn_data, indent=4))
                return render(request, 'paypal.html', {'order_id': order_id,
                                                       'object_id': object_id, 'sales': sales})
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
                print(fields)
                response = requests.post('https://secure.networkmerchants.com/api/transact.php', data=fields)

                print(response.text)
                return JsonResponse({'message': 'Data received successfully'})
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

        sales = Sales.objects.get(pk=object_id)
        selected_card = sales.cards.filter(card_to_be_used=True).first()
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
            'merchant_id': merchant_id
        }
        return render(request, "example.html", context)

    @csrf_exempt
    def my_view(self, request, object_id):
        if request.method == "POST":
            print(request.body)
            sales = Sales.objects.get(pk=object_id)
            charge_id = request.POST.get('chargeId')
            selected_card = sales.cards.filter(card_to_be_used=True).first()
            merchant = request.POST.get('merchant')
            security = request.POST.get('security')

            amount = sales.amount
            credit_card_number = selected_card.card_no
            payment_method = request.POST.get('payment_method')
            gateway_info = request.POST.get('gateway')
            gateway_id, gateway = gateway_info.split(",")
            print(gateway_info)
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
            invoice = Invoice.objects.create(
                sale=sales,
                payment=payment_method,
                security=security,
                gateway=gateway,
                Merchant_Name=merchant
            )
            merchant_id = Merchants.objects.filter(
                merchant_link_id=gateway_id,
                Company_Name__company_name=merchant
            ).values_list('id', flat=True).first()
            print(payment_method)
            print(merchant_id)
            if payment_method == 'Sale' and gateway.lower() == 'authorize.net':
                expirationDate = f"{expirationMonth}/{expirationYear}"
                xml_response = charge_credit_card(amount, cardNumber, expirationDate, cardCod, firstName, lastName,
                                                  company,
                                                  address, state, zip_code, merchant_id)
                return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))

            elif payment_method == 'Authorize' and gateway.lower() == 'authorize.net':
                expirationDate = f"{expirationMonth}/{expirationYear}"
                xml_response = authorize_credit_card(amount, cardNumber, expirationDate, cardCod, firstName, lastName,
                                                     company,
                                                     address, state, zip_code, merchant_id)
                xml_string = ET.tostring(xml_response)
                return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))
            # **************************  STRIPE  ******************************
            elif payment_method == 'Authorize' and gateway.lower() == 'stripe':
                try:
                    amount = amount
                    print(amount)
                    authorize_stripe(amount, merchant_id)
                    return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))
                except Exception as e:
                    error_message = "An error occurred: {}".format(e)
                    print("Error:", error_message)
                    return JsonResponse({'error': error_message}, status=500)
            elif payment_method == 'Sale' and gateway.lower() == 'stripe':
                try:
                    amount = amount
                    print(amount)
                    charge_stripe(amount, merchant_id)
                    return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))
                except Exception as e:
                    error_message = "An error occurred: {}".format(e)
                    print("Error:", error_message)
                    return JsonResponse({'error': error_message}, status=500)
            elif payment_method == 'Authorize' and gateway.lower() == 'nmi':
                try:
                    expirationDate = f"{expirationMonth}/{expirationYear}"
                    fields = {
                        'security_key': get_merchant_api_key(merchant_id),
                        'firstname': sales.customer_first_name,
                        'lastname': sales.customer_last_name,
                        'company': sales.company,
                        'address1': sales.customer_address,
                        'state': sales.state,
                        'zip': sales.zip_code,
                        'country': "USA",
                        'phone': sales.calling_no,
                        'email': sales.customer_email,
                        'amount': amount,
                        'ccnumber': credit_card_number,
                        'ccexp': expirationDate,
                        'cvv': cardCod,
                        'order-description': 'Example Charge',
                        'type': 'auth',
                    }
                    response = requests.post('https://secure.networkmerchants.com/api/transact.php', data=fields)
                    print("*********************")
                    print(response.text)

                    return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))
                except json.JSONDecodeError:
                    return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))

            elif security == '2D' and payment_method == 'Sale' and gateway.lower() == 'nmi':
                try:
                    expirationDate = f"{expirationMonth}/{expirationYear}"
                    fields = {
                        'security_key': get_merchant_api_key(merchant_id),
                        'firstname': sales.customer_first_name,
                        'lastname': sales.customer_last_name,
                        'company': sales.company,
                        'address1': sales.customer_address,
                        'state': sales.state,
                        'zip': sales.zip_code,
                        'country': "USA",
                        'phone': sales.calling_no,
                        'email': sales.customer_email,
                        'amount': amount,
                        'ccnumber': credit_card_number,
                        'ccexp': expirationDate,
                        'cvv': cardCod,
                        'order-description': 'Charge',

                    }
                    print(fields)
                    response = requests.post('https://secure.networkmerchants.com/api/transact.php', data=fields)
                    print("*********************")
                    print(response.text)
                    return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))
                except json.JSONDecodeError:
                    return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))
            elif security == '3D' and gateway.lower() == 'nmi':
                check = get_merchant_login_key(merchant_id)
                print("****************")
                print(check)
                return redirect('/admin/Global_Core/sales/{}/payment/3D_secure/{}'.format(object_id, merchant_id))

            elif payment_method == 'Sale' and gateway.lower() == 'paypal':
                return redirect('/admin/Global_Core/sales/{}/payment/paypal/{}'.format(object_id, merchant_id))
            elif payment_method == 'Authorize' and gateway == 'PayPal':
                return redirect(
                    '/admin/Global_Core/sales/{}/payment/authorize_paypal/{}'.format(object_id, merchant_id))
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
            check = request.user.is_superuser
            if check:
                print("Hello Super User")
            else:
                print("Hello Employee")
            selected_card = sales.cards.filter(card_to_be_used=True).first()
            selected_account = sales.Accounts.filter(account_to_be_used=True).first()
            print(selected_account)
            if sales.payment_method == 'Account':
                selected_card = None
            else:
                selected_account = sales.Accounts.filter(account_to_be_used=True).first()

            print("*********")
            print(selected_card)
            today_date = datetime.now().date()
            gateways_queryset = Gateway.objects.all()
            gateways_list = [gateway.merchant for gateway in gateways_queryset]
            context = {
                'client_info': customer_info,
                'today_date': today_date,
                'cards': selected_card,
                'account': selected_account,
                'gateway': gateways_queryset,
                'object_id': object_id
            }
            return render(request, "enter_payment_details.html", context)

    def get_details_view(self, request):
        try:
            print("****")
            object_id = request.GET.get('objectId')
            sales = Sales.objects.get(pk=object_id)
            customer_info = {
                'customer_name': sales.customer_name,
                'customer_address': sales.customer_address,
                'customer_email': sales.customer_email,
                'amount': sales.amount
            }
            security_option = request.GET.get('security')
            payment_method = request.GET.get('payment_method')
            gateway = request.GET.get('gateway', '')
            merchant = request.GET.get('merchant')
            today_date = datetime.now().date()
            selected_card = sales.cards.filter(card_to_be_used=True).first()
            selected_account = sales.Accounts.filter(account_to_be_used=True).first()
            invoice = Invoice.objects.create(
                sale=sales,
                payment=payment_method,
                security=security_option,
                gateway=gateway,
                Merchant_Name=merchant
            )
            invoice_id = invoice.id

            context = {
                'invoice_id': invoice_id,
                'client_info': customer_info,
                'today_date': today_date,
                'account': selected_account,
                'object_id': object_id,
                'security_option': security_option,
                'payment_method': payment_method,
                'gateway': gateway,
                'merchant': merchant
            }

            return JsonResponse(context)

        except Sales.DoesNotExist:
            return JsonResponse({'error': 'Sales object does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



class DashboardAdmin(admin.ModelAdmin):
    class SalesChartDataView(TemplateView):
        template_name = 'sales_chart.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            sales_data = Sales.objects.all().values('date', 'amount')
            sales_data_list = list(sales_data)
            for sale in sales_data_list:
                sale['date'] = sale['date'].strftime('%Y-%m-%d')
            context['sales_data_json'] = json.dumps(sales_data_list)
            return context


admin.site.register(Sales, SalesAdmin)
admin.site.register(Expenses, ExpensesAdmin)
admin.site.register(Company)
admin.site.register(Links, LinksAdmin)
admin.site.register(Merchants, MerchantAdmin)
admin.site.register(Gateway, GatewayAdmin)
# admin.site.register(Sales)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Dashboard, DashboardAdmin)
# admin.site.register(urls)
admin.site.register(Invoice)