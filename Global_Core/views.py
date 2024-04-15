
import requests
import json

from django.db.models import Count, Sum, F
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils.datetime_safe import datetime
from django.utils.functional import SimpleLazyObject
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from rest_framework.views import APIView
from .models import *
from .authorizepayment import authorize_credit_card, charge_credit_card
import lxml.etree as ET
import stripe
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse
from paypalrestsdk import Payment
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Sales, CustomUser
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from .serializers import WithdrawalRequestSerializer
from django.db.models.functions import TruncDate
#          ************ APIs *********************
def get_merchants(request):
    gateway_id = request.GET.get('gateway_id')
    if gateway_id:
        merchants = Merchants.objects.filter(merchant_link_id=gateway_id).values_list('Company_Name__company_name',
                                                                                      flat=True)
        return JsonResponse(list(merchants), safe=False)
    else:
        return JsonResponse([], safe=False)

class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'invoice.html'
    context_object_name = 'invoice_object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice_object = self.get_object()
        gateway = invoice_object.gateway
        sale_object = invoice_object.sale
        selected_card = sale_object.cards.filter(card_to_be_used=True).first()
        date = datetime.now().date()
        sale_id = sale_object.id
        payment = invoice_object.payment

        context["object_id"] = sale_id
        context["gateway"] = gateway
        context["invoice_id"] = self.kwargs.get('invoice_id')
        context["date"] = date
        context["sale"] = sale_object
        context["cards"] = selected_card
        context["payment_method"] = payment

        return context


@require_POST
def mark_as_read(request, message_id):
        message = Messages.objects.get(pk=message_id)
        message.is_read = True
        message.save()
        return JsonResponse({'success': True})


@csrf_exempt
def add_associate_user(request, sale_id, user_id):
    sale = get_object_or_404(Sales, pk=sale_id)
    user = get_object_or_404(CustomUser, pk=user_id)
    if user == sale.added_by:
        return JsonResponse({'status': 'error', 'message': 'The Owner of the sale cannot be added as an associated user'},
                            status=400)
    # Check if the association already exists
    if not SalesUserAssociation.objects.filter(sale=sale, user=user).exists():
        SalesUserAssociation.objects.create(sale=sale, user=user)
        return JsonResponse({'status': 'success', 'message': 'User added successfully'}, status=201)
    else:
        return JsonResponse({'status': 'error', 'message': 'User is already associated with this sale'}, status=400)

@csrf_exempt
def delete_associate_user(request, sale_id, user_id):
    sale = get_object_or_404(Sales, pk=sale_id)
    user = get_object_or_404(CustomUser, pk=user_id)

    # Check if the association exists
    association = SalesUserAssociation.objects.filter(sale=sale, user=user)
    if association.exists():
        association.delete()
        return JsonResponse({'status': 'success', 'message': 'User deleted successfully'}, status=200)
    else:
        return JsonResponse({'status': 'error', 'message': 'User is not associated with this sale'}, status=400)


class SalesByCardNumberAPIView(APIView):
    def get(self, request):
        card_number = request.GET.get('card_number')
        amount = request.GET.get('amount')
        start_date = request.GET.get('range_from')
        end_date = request.GET.get('range_to')
        auth = request.GET.get('auth')
        if not (card_number or amount or (start_date and end_date) or auth):
            return Response({'error': 'Please provide card number, amount, Auth, or date range'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            sales = Sales.objects.all()

            if card_number:
                sales = sales.filter(cards__card_no__endswith=card_number, cards__card_to_be_used=True)
            if auth:
                sales = sales.filter(transaction_type=auth)
            if amount:
                # Search by amount
                sales = sales.filter(amount=float(amount))

            if start_date and end_date:
                # Search by date range
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                sales = sales.filter(sales_date__range=[start_datetime, end_datetime])
            sales = sales.filter(transaction_type__in=['Sale', 'Authorize', 'Charge Back'])

            if sales.exists():
                sales_data = []
                for sale in sales:
                    bank_account = BankAccount.objects.filter(sales=sale, account_to_be_used=True).first()
                    last_invoice = Invoice.objects.filter(sale_id=sale.id, payment_check='Yes').order_by('-id').first()
                    card_number = Card.objects.filter(sales=sale, card_to_be_used=True).first()
                    print(last_invoice)
                    sales_data.append({
                        'id': sale.id,
                        'provider_name': sale.provider_name,
                        'sales_date': sale.sales_date,
                        'customer_name': sale.customer_name,
                        'customer_address': sale.customer_address,
                        'customer_email': sale.customer_email,
                        'amount': sale.amount,
                        'payment_method': sale.payment_method,
                        'status': sale.status,
                        'reason': sale.reason,
                        'transaction_type': sale.transaction_type,
                        'description': sale.description,
                        'authorization': sale.authorization.url if sale.authorization else None,
                        'bank_account': {
                            'account_name': bank_account.account_name,
                            'checking_acc': bank_account.checking_acc,
                            'routing_no': bank_account.routing_no,
                            'checking_no': bank_account.checking_no,
                            'account_address': bank_account.account_address
                        } if bank_account else None,
                        'last_invoice': {
                            'invoice_id': last_invoice.id,
                            'payment': last_invoice.payment,
                            'security': last_invoice.security,
                            'gateway': last_invoice.gateway,
                            'Merchant_Name': last_invoice.Merchant_Name,
                            'payment_check': last_invoice.payment_check
                        } if last_invoice else None,
                        'card_number': {
                            'card_id': card_number.id,
                            'card_number': card_number.card_no,
                        } if last_invoice else None
                    })
                return Response({'sales': sales_data})
            else:
                return Response({'error': 'No sales found matching the criteria'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ChangeTransactionTypeAPIView(APIView):
    def post(self, request):
        try:
            sale_id = request.data.get('sale_id')
            sale = Sales.objects.get(id=sale_id)
            sale_amount = sale.amount
            commission_adjustment = 0
            user = sale.added_by
            target = float(user.target)
            commission = float(user.commission)
            print(sale_amount)
            sales_on_same_day = Sales.objects.filter(added_by=user, sales_date=sale.sales_date)
            total_sales_on_same_day = sales_on_same_day.aggregate(total_sales=Sum('amount'))['total_sales']
            print(total_sales_on_same_day)
            total_sale = total_sales_on_same_day - sale_amount
            if total_sale == 0:
                slabs_hit_after_change = sale_amount//target
            else:
                slabs_hit_after_change = total_sale // target
            commission_adjustment = (slabs_hit_after_change * commission) + 25
            wallet = user.wallet
            print(f"total_sale: {total_sale}")
            print(f"slab_hit_after_change: {slabs_hit_after_change}")
            print(f"target: {target}")
            print(f"commission: {commission}")
            print(f"Commision Adjustment: {commission_adjustment}")

            wallet.value = wallet.value - commission_adjustment
            wallet.save()
            print(f"Wallet After: {wallet.value}")
            sale.transaction_type = 'Charge Back'
            sale.save()
            return Response({'message': 'Transaction type changed to Charge Back successfully',
                             'commission_adjustment': commission_adjustment},
                            status=status.HTTP_200_OK)

        except Sales.DoesNotExist:
            return Response({'error': 'Sale not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def chargeback_view(request):
    return render(request, 'chargeback.html')


def chargeback_view(request):
    return render(request, 'chargeback.html')


class WalletAPIView(APIView):
    def get(self, request):
        try:
            user = request.user
            target = float(user.target)
            commision = float(user.commission)
            wallet = user.wallet
            current_wallet_value = float(wallet.value)
            print(current_wallet_value)
            distinct_dates = Sales.objects.filter(added_by=user).values('sales_date').distinct()
            total_sales = current_wallet_value
            sales_by_day = []

            for date in distinct_dates:
                total_amount = Sales.objects.filter(added_by=user, sales_date=date['sales_date']) \
                    .filter(wallet_check=False) \
                    .aggregate(total_amount=Sum('amount'))['total_amount']

                if total_amount:
                    sales_by_day.append({
                        'date': date['sales_date'],
                        'total_amount': total_amount
                    })
                    bonus_commission = 0
                    if total_amount >= target:
                        slab_hits = total_amount // target
                        bonus_commission = slab_hits * commision

                        # Update wallet and mark sales as checked
                        wallet.value = str(current_wallet_value + bonus_commission)
                        wallet.save()
                        total_sales = current_wallet_value + bonus_commission
                        Sales.objects.filter(added_by=user, sales_date=date['sales_date'], wallet_check=False) \
                            .update(wallet_check=True)

            return Response({
                'sales_by_day': sales_by_day,
                'Total_Commision': total_sales,
                'target': target,
                'commision': commision
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
print("")


class WithdrawalRequestAPIView(APIView):
    def post(self, request):
        request.data['user'] = request.user.id
        serializer = WithdrawalRequestSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            withdrawal_amount = serializer.validated_data['amount']
            wallet_value = request.user.wallet.value

            if withdrawal_amount > wallet_value:
                raise ValidationError("Withdrawal amount cannot exceed the wallet value.")

            serializer.save(user=request.user)
            print("Done")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)