from django.urls import path
from . import views

urlpatterns = [
    path('enter_payment_details/', views.enter_payment_details, name='enter_payment_details'),
]
