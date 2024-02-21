from django.urls import path
from . import views

urlpatterns = [
    path('enter_payment_details/', views.charge_credit_card_view, name='enter_payment_details'),
    path('charge/', views.charge, name='charge'),
    path('capture_Stripe/', views.capture_payment_stripe, name='test'),
    path ('checkout', views.checkout, name='checkout'),
    path ('create_payment_paypal' , views.create_payment_paypal , name='create_payment_paypal'),
    path('test' , views.test , name='test'),
    path('nmi', views.NMI, name='NMI')
]
