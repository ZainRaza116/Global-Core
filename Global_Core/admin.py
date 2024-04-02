import requests
from django.db.models import Count, Sum, Q
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
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
from datetime import datetime, timedelta
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
from .forms import SalesForm,CardForm
c_user = get_user_model()
from semantic_admin import SemanticStackedInline, SemanticTabularInline

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


class CardInline(SemanticStackedInline):
    model = Card
    extra = 0
    # formset = CardInlineFormSet
    form = CardForm
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and hasattr(obj, 'transaction_type') and obj.transaction_type in ['Sale', 'Authorize']:
            # Add fields from the Card model to readonly_fields
            readonly_fields += [field.name for field in self.model._meta.fields]
        return tuple(readonly_fields)

class BankAccountInline(SemanticStackedInline):
    model = BankAccount
    extra = 0
    # forms = AccountInlineFormSet

class SalesAdmin(admin.ModelAdmin):
    change_form_template = 'admin/sales/change_form.html'
    # fieldsets = (
    #     (None, {
    #         'fields': ('sales_date', 'provider_name'),
    #     }),
    #     ('Customer Information', {
    #         'fields': ('customer_name', 'customer_first_name', 'customer_last_name', 'customer_address', 'state', 'zip_code', 'calling_no', 'customer_email', 'ssn', 'cus_dob'),
    #     }),
    #     ('Payment Details', {
    #         'fields': ('transaction_type', 'payment_method', 'amount'),
    #     }),
    #     ('Additional Information', {
    #         'fields': ('btn', 'acc_user_name', 'password', 'status', 'reason', 'description', 'authorization'),
    #     }),
    # )

    inlines = [CardInline, BankAccountInline]
    form = SalesForm



    # def get_inline_instances(self, request, obj=None):
    #     inline_instances = super().get_inline_instances(request, obj)
    #     return inline_instances

    def get_queryset(self, request):
        user = request.user
        if user.is_superuser:
            return super().get_queryset(request)
        else:
            return Sales.objects.filter(
                models.Q(added_by=user) |  # Filter for sales added by the user
                models.Q(associate_users__user=user)  # Filter for sales where the user is part of associated users
            ).distinct()
    #     return super().get_queryset(request)
    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return True

    def get_list_display(self, request):
        if request.user.is_superuser:
            return ['customer_name', 'shortened_customer_address', 'formatted_amount', 'payment_method', 'modified_added_by', 'payment_status_func', 'order_status_func','custom_action12']
        else:
            return ['customer_name', 'customer_address', 'formatted_amount', 'payment_method', 'modified_added_by', 'payment_status_func', 'order_status_func','custom_action24']

    def shortened_customer_address(self, obj):
        words = obj.customer_address.split()
        if len(words) >= 2:
            return ' '.join(words[:2]) + '...'
        else:
            return obj.customer_address
    shortened_customer_address.short_description = 'Address'

    def formatted_amount(self, obj):
        return f"${obj.amount:.2f}"
    formatted_amount.short_description = 'Amount'

    def modified_added_by(self, obj):
        if obj.added_by and hasattr(obj.added_by, 'email'):
            email = obj.added_by.email
            if '@' in email:
                username, domain = email.split('@')
                return f"{username}@ ..."
            return email
        return None
    modified_added_by.short_description = 'Added By'

    # def get_exclude(self, request, obj=None):
    #     excludes = super().get_exclude(request, obj=obj) or ()
    #     return excludes + ('transaction_type',)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.transaction_type in ['Sale', 'Authorize']:
            readonly_fields += [field.name for field in Sales._meta.fields]
        return tuple(readonly_fields)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "cards":
            kwargs["queryset"] = Card.objects.filter(sales_id=request.resolver_match.kwargs['object_id'])
            # Set card field to read-only
            kwargs['widget'] = admin.widgets.AdminTextInputWidget(attrs={'readonly': 'readonly'})
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def pay(self, obj):
        payment_image_url = '/static/credit-card.png'
        payment_html = format_html(
            '<a href="{}"><img src="{}" alt="Payment" style="justify_content:center; max-height: 20px; '
            'max-width: 20px; '
            'margin-right: 5px;" /></a>',
            f"/cms/Global_Core/sales/{obj.id}/payment/", payment_image_url)
        return payment_html

    def custom_action24(self, obj):
        details_image_url = '/static/reply-message.png'
        message = obj.messages.first()
        if message and not message.is_read:
            details_image_url = '/static/notification_12299644.png'
            details_html = format_html(
                '<a href="{}?mark_as_read={}"><img src="{}" alt="View Details" style="max-height:'
                ' 20px; max-width: 20px; margin-right: 5px;" /></a>',
                f"/cms/Global_Core/sales/{obj.id}/response/", message.id, details_image_url)
        else:
            details_html = format_html(
                '<a href="{}"><img src="{}" alt="View Details" style="max-height:'
                ' 20px; max-width: 20px; margin-right: 5px;" /></a>',
                f"/cms/Global_Core/sales/{obj.id}/response/", details_image_url)

        return format_html(
            '<div style="display: flex;">'
            '{}'
            '</div>',
             details_html)

    custom_action24.short_description = 'Actions'

    def custom_action12(self, obj):
        payment_image_url = '/static/credit-card.png'
        details_image_url = '/static/reply-message.png'
        add_person_url = '/static/add-user.png'

        add_html = format_html(
            '<a href="{}"><img src="{}" alt="Payment" style="justify_content:center; max-height: 20px; '
            'max-width: 20px; '
            'margin-right: 5px;" /></a>',
            f"/cms/Global_Core/sales/{obj.id}/assign_user/", add_person_url)


        payment_html = format_html(
            '<a href="{}"><img src="{}" alt="Payment" style="justify_content:center; max-height: 20px; '
            'max-width: 20px; '
            'margin-right: 5px;" /></a>',
            f"/cms/Global_Core/sales/{obj.id}/payment/", payment_image_url)


        message = obj.messages.first()
        if message and not message.is_read:
            details_image_url = '/static/notification_12299644.png'
            details_html = format_html(
                '<a href="{}?mark_as_read={}"><img src="{}" alt="View Details" style="max-height:'
                ' 20px; max-width: 20px; margin-right: 5px;" /></a>',
                f"/cms/Global_Core/sales/{obj.id}/response/", message.id, details_image_url)
        else:
            details_html = format_html(
                '<a href="{}"><img src="{}" alt="View Details" style="max-height:'
                ' 20px; max-width: 20px; margin-right: 5px;" /></a>',
                f"/cms/Global_Core/sales/{obj.id}/response/", details_image_url)

        return format_html(
            '<div style="display: flex;">'
            '{} {} {}'
            '</div>',
             add_html, details_html, payment_html)

    custom_action12.short_description = 'Actions'

    def payment_status_func(self, obj):

        if obj.transaction_type == 'Sale':
            payment_html = '<span style="color: Black; font-weight: bold;">Sale</span>'
        elif obj.transaction_type == 'Authorize':
            payment_html = '<span style="color: green; font-weight: bold;">Authorize</span>'
        else:
            payment_html = '<span style="color: Red; font-weight: bold;">Not Processed</span>'
        return format_html(payment_html)


    payment_status_func.short_description = 'Payment Status'

    def order_status_func(self, obj):
        status_html = ""
        if obj.status == 'pending':
            status_html = '<span style="color: orange; font-weight: bold;">Pending</span>'
        elif obj.status == 'completed':
            status_html = '<span style="color: green; font-weight: bold;">Completed</span>'
        elif obj.status == 'in_process':
            status_html = '<span style="color: blue; font-weight: bold;">In Process</span>'
        return format_html(status_html)

    order_status_func.short_description = 'Order Status'

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
                 name="get_details_view"),
            path("get_data/", self.admin_site.admin_view(self.get_data),
                 name="get_data"),
            path("get_more_data/", self.admin_site.admin_view(self.get_more_data),
                 name="get_more_data"),
            path("<int:object_id>/assign_user/", self.admin_site.admin_view(self.add_user),
                 name="add_user"),
            path("chargeback/", self.admin_site.admin_view(self.charge_back),
                 name="charge_back"),
        ]
        return my_urls + urls

    def charge_back(self, request ):
        return render(request, 'chargeback.html')

    def add_user(self, request, object_id):
        user_info = Sales.objects.get(pk=object_id)
        users = CustomUser.objects.all()
        associate_users = SalesUserAssociation.objects.filter(sale=user_info)
        print(associate_users)
        context ={
            'user_info': user_info,
            'users': users,
            'associate_users': associate_users
        }
        return render(request, "add.html", context)


    def get_more_data(self, request):
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year

        # Initialize response data
        response_data = {}

        # Check if the user is a superuser
        if request.user.is_superuser:
            # Get total sales count for the current month
            total_sales_count = Sales.objects.filter(
                sales_date__month=current_month,
                sales_date__year=current_year
            ).count()

            active_users_count = CustomUser.objects.filter(is_active=True).count()
            total_revenue = Sales.objects.filter(
                sales_date__month=current_month,
                sales_date__year=current_year
            ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

            # Construct response data with totals
            response_data = {
                'total_sales_count': total_sales_count,
                'active_users_count': active_users_count,
                'total_revenue': total_revenue
            }
        else:
            # Get total sales count for the current month for the current user
            total_sales_count = Sales.objects.filter(
                sales_date__month=current_month,
                sales_date__year=current_year,
                added_by=request.user  # Assuming 'added_by' is the correct field representing the user
            ).count()

            # Get total revenue for the current month for the current user
            total_revenue = Sales.objects.filter(
                sales_date__month=current_month,
                sales_date__year=current_year,
                added_by=request.user
            ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

            # Construct response data with user-specific data
            response_data = {
                'total_sales_count': total_sales_count,
                'total_revenue': total_revenue
            }

        return JsonResponse(response_data)

    def get_data(self, request):
        # Get the current month, year, and day
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        current_day = current_date.day

        # Initialize response data
        sales_data_per_day = {}

        # Check if the user is a superuser
        if request.user.is_superuser:
            # Get sales data for each day of the month up to today for all users
            sales_per_day = Sales.objects.filter(
                Q(sales_date__month=current_month, sales_date__year=current_year) &
                Q(sales_date__lte=current_date)
            ).values('sales_date__day').annotate(
                total_sales=Count('id'), total_amount=Sum('amount')
            )
        else:
            # Get sales data for the current user for each day of the month up to today
            sales_per_day = Sales.objects.filter(
                Q(sales_date__month=current_month, sales_date__year=current_year) &
                Q(sales_date__lte=current_date) &
                Q(added_by=request.user)  # Assuming 'user' is the field linking sales to users
            ).values('sales_date__day').annotate(
                total_sales=Count('id'), total_amount=Sum('amount')
            )

        # Create a dictionary to store sales data per day
        for day in range(1, current_day + 1):
            sales_data_per_day[day] = {'total_sales': 0, 'total_amount': 0}

        # Fill in the actual sales data
        for sale in sales_per_day:
            day = sale['sales_date__day']
            sales_data_per_day[day] = {
                'total_sales': sale['total_sales'],
                'total_amount': sale['total_amount']
            }

        return JsonResponse(sales_data_per_day)

    def custom_response(self, request, object_id):
        if request.method == "POST":
            message_text = request.POST.get("message")
            if message_text:
                sales = Sales.objects.get(pk=object_id)
                message = Messages.objects.create(added_by=request.user, sale=sales, message=message_text)
                print("no i am here")
                return redirect('/cms/Global_Core/sales/')
        elif request.method == "GET" and 'mark_as_read' in request.GET:
            print("i am here bud")
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
                print("bllklklklkl")
                print(json_data)
                card_exp_month = json_data['cardExpMonth'][:2]
                card_exp_year = json_data['cardExpYear'][2:]
                if len(card_exp_month) == 1:
                    # Prepend '0' to the month to make it two digits
                    card_exp_month = '0' + card_exp_month
                fields = {
                    'security_key': get_merchant_api_key(merchant_id),
                    'ccnumber': json_data['cardNumber'],
                    'ccexp': f"{card_exp_month}{card_exp_year}",
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
                reponse = response.text
                print(response.text)
                pairs = reponse.split('&')
                response_dict = {}
                for pair in pairs:
                    key, value = pair.split('=')
                    response_dict[key] = value
                response_value = response_dict.get('response')
                print(response_value)
                if response_value == '1':
                    sales = Sales.objects.get(pk=object_id)
                    sales.transaction_type = "Sale"
                    sales.save()
                    invoice = Invoice.objects.create(
                        sale=sales,
                        payment="Sale",
                        security="2D",
                        gateway="NMI",
                        Merchant_Name="-",
                        payment_check='Yes'
                    )
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
                json_response = charge_credit_card(amount, cardNumber, expirationDate, cardCod, firstName, lastName,
                                                  company,
                                                  address, state, zip_code, merchant_id)
                transaction_type = json_response.get('transaction_type')  # Extract transaction type from xml_response
                status = json_response.get('status')

                if status == 'Success':
                    sales = Sales.objects.get(pk=object_id)
                    sales.transaction_type = transaction_type
                    invoice = Invoice.objects.create(
                        sale=sales,
                        payment=payment_method,
                        security=security,
                        gateway=gateway,
                        Merchant_Name=merchant,
                        payment_check='Yes'
                    )

                    print("Invoice has been created")
                    sales.save()
                return JsonResponse(json_response)
            elif payment_method == 'Authorize' and gateway.lower() == 'authorize.net':
                expirationDate = f"{expirationMonth}/{expirationYear}"
                json_response = authorize_credit_card(amount, cardNumber, expirationDate, cardCod, firstName, lastName,
                                                     company,
                                                     address, state, zip_code, merchant_id)
                transaction_type = json_response.get('transaction_type')
                status = json_response.get('status')

                if status == 'Success':
                    sales = Sales.objects.get(pk=object_id)
                    sales.transaction_type = transaction_type
                    invoice = Invoice.objects.create(
                        sale=sales,
                        payment=payment_method,
                        security=security,
                        gateway=gateway,
                        Merchant_Name=merchant,
                        payment_check='Yes'
                    )
                return HttpResponseRedirect(request.path)

                return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))
            # **************************  STRIPE  ******************************
            elif payment_method == 'Authorize' and gateway.lower() == 'stripe':
                try:
                    amount = amount

                    charge_status = charge_stripe(amount, merchant_id)

                    print(charge_status)
                    if charge_status == "usd":
                        sales = Sales.objects.get(pk=object_id)
                        sales.transaction_type = "Authorize"
                        sales.save()
                        invoice = Invoice.objects.create(
                            sale=sales,
                            payment=payment_method,
                            security=security,
                            gateway=gateway,
                            Merchant_Name=merchant,
                            payment_check='Yes'
                        )
                    return HttpResponseRedirect(request.path)
                except Exception as e:
                    error_message = "An error occurred: {}".format(e)
                    print("Error:", error_message)
                    return JsonResponse({'error': error_message}, status=500)
            elif payment_method == 'Sale' and gateway.lower() == 'stripe':
                try:
                    amount = amount

                    charge_status = charge_stripe(amount, merchant_id)
                    print("idiejdiej")
                    print(charge_status)
                    if charge_status == "usd":
                        sales = Sales.objects.get(pk=object_id)
                        sales.transaction_type = "Sale"
                        sales.save()
                        invoice = Invoice.objects.create(
                            sale=sales,
                            payment=payment_method,
                            security=security,
                            gateway=gateway,
                            Merchant_Name=merchant,
                            payment_check='Yes'
                        )
                    return HttpResponseRedirect(request.path)
                except Exception as e:
                    error_message = "An error occurred: {}".format(e)
                    print("Error:", error_message)
                    return HttpResponseRedirect(request.path)
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
                    reponse = response.text
                    print(response.text)
                    pairs = reponse.split('&')
                    response_dict = {}
                    for pair in pairs:
                        key, value = pair.split('=')
                        response_dict[key] = value
                    response_value = response_dict.get('response')
                    print(response_value)
                    if response_value == '1':
                        sales = Sales.objects.get(pk=object_id)
                        sales.transaction_type = "Authorize"
                        sales.save()
                        invoice = Invoice.objects.create(
                            sale=sales,
                            payment=payment_method,
                            security=security,
                            gateway=gateway,
                            Merchant_Name=merchant,
                            payment_check='Yes'
                        )
                    return HttpResponseRedirect(request.path)

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
                    reponse = response.text
                    print(response.text)
                    pairs = reponse.split('&')
                    response_dict = {}
                    for pair in pairs:
                        key, value = pair.split('=')
                        response_dict[key] = value
                    response_value = response_dict.get('response')
                    print(response_value)
                    if response_value == '1':
                        sales = Sales.objects.get(pk=object_id)
                        sales.transaction_type = "Sale"
                        sales.save()
                        invoice = Invoice.objects.create(
                            sale=sales,
                            payment=payment_method,
                            security=security,
                            gateway=gateway,
                            Merchant_Name=merchant,
                            payment_check='Yes'
                        )
                    return HttpResponseRedirect(request.path)
                except json.JSONDecodeError:
                    return redirect('/admin/Global_Core/sales/{}/payment/'.format(object_id))
            elif security == '3D' and gateway.lower() == 'nmi':
                check = get_merchant_login_key(merchant_id)
                print("****************")
                print(check)
                return redirect('/cms/Global_Core/sales/{}/payment/3D_secure/{}'.format(object_id, merchant_id))

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

class InvoiceAdmin(admin.ModelAdmin):
        list_display = ['sale', 'payment', 'security', 'gateway','Merchant_Name']



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
admin.site.register(Invoice, InvoiceAdmin)
# admin.site.unregister(Group)
