from django.urls import path
from . import views

urlpatterns = [
    path('enter_payment_details/', views.charge_credit_card_view, name='enter_payment_details'),
    path('charge/', views.charge, name='charge'),
    path('capture_Stripe/', views.capture_payment_stripe, name='test'),
    path('checkout', views.checkout, name='checkout'),
    path('create_payment_paypal' , views.create_payment_paypal , name='create_payment_paypal'),
    path('test' , views.test , name='test'),
    # path('nmi', views.NMI, name='NMI')
    path('square_payment', views.square_payment , name='square_payment'),
    path("get_merchants/", views.get_merchants, name="get_merchants"),
    # path('admin/Global_Core/sales/<int:object_id>/details/', views.get_details_view, name='get_details'),
    path('customer_invoice/<int:invoice_id>/', views.invoice, name='test'),
    path('mark_as_read/<int:message_id>/', views.mark_as_read, name='mark_as_read'),
]