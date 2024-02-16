from django.urls import path
from . import views

urlpatterns = [
    path('enter_payment_details/', views.charge_credit_card_view, name='enter_payment_details'),
]
