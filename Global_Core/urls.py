from django.urls import path
from . import views
from .views import InvoiceDetailView
from .views import SalesByCardNumberAPIView
from .views import ChangeTransactionTypeAPIView
urlpatterns = [
    path("get_merchants/", views.get_merchants, name="get_merchants"),
    # path('admin/Global_Core/sales/<int:object_id>/details/', views.get_details_view, name='get_details'),
    path('customer_invoice/<int:pk>/', InvoiceDetailView.as_view(), name='test'),
    path('mark_as_read/<int:message_id>/', views.mark_as_read, name='mark_as_read'),
    path('api/sales/<int:sale_id>/add_user/<int:user_id>/', views.add_associate_user, name='add_associate_user'),
    path('api/sales/<int:sale_id>/delete_user/<int:user_id>/', views.delete_associate_user,
         name='delete_associate_user'),
    path('get_sales_by_card_number/', SalesByCardNumberAPIView.as_view(), name='get_sales_by_card_number'),
    path('cms/Global_Core/chargeback/', views.chargeback_view, name='chargeback'),
    path('Global_Core/chargeback/paymentmethod', ChangeTransactionTypeAPIView.as_view(), name='chargebackpayment'),
]