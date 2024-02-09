from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.contrib.auth import get_user_model


CustomUser = get_user_model()


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'salary', 'target', 'hiring_date']
    ordering = ['email']


admin.site.register(Dashboard)
admin.site.register(CustomUser, CustomUserAdmin)



class MerchantsAdmin(admin.ModelAdmin):
    list_display = ['merchant', 'merchant_dba', 'account_type', 'merchant_type']


admin.site.register(Merchants, MerchantsAdmin)
admin.site.register(Sales)


class LinksAdmin(admin.ModelAdmin):
    list_display = ['merchant_link', 'link', 'amount']


admin.site.register(Links, LinksAdmin)

admin.site.register(Accounts)
admin.site.register(Employee)


class ExpensesAdmin(admin.ModelAdmin):
    list_display = ['date_incurred', 'title', 'amount', 'expenses_type']


admin.site.register(Expenses, ExpensesAdmin)
admin.site.register(Company)