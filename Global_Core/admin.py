from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import *
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.models import Group
from django.contrib.admin import AdminSite


get_user_model()


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

class CardInline(admin.TabularInline):
    model = Card
    extra = 1


class SalesAdmin(admin.ModelAdmin):
    inlines = [CardInline]
    change_form_template = 'admin/sales/change_form.html'

    list_display = ['customer_name', "customer_address", "amount", "payment_method", "added_by" , "custom_action"]


    def custom_action(self, obj):

            return format_html('<a class="button" href="{}">Enter Payment Details</a>', f"/admin/enter_payment_details/{obj.id}/")

    custom_action.allow_tags = True  # Only for Django versions < 1.9
    custom_action.short_description = 'Payment'
    def enter_payment_details(self, request, sales_id):
        try:
            sales_instance = Sales.objects.get(pk=sales_id)
        except Sales.DoesNotExist:
            messages.error(request, "Sales entry not found.")
            return HttpResponseRedirect(reverse('admin:sales_sales_changelist'))  # Redirect to sales change list or any other page

        # Here, you can render your payment details form using the sales_instance
        # For example:
        # form = PaymentDetailsForm(initial={'sales_instance': sales_instance})

        return HttpResponseRedirect(reverse('admin:sales_sales_change', args=[sales_id]))

    enter_payment_details.short_description = "Enter Payment Details"

    # def get_urls(self):
    #     urls = super().get_urls()
    #     custom_urls = [
    #         path('enter_payment_details/<int:sales_id>/', self.enter_payment_details, name='enter_payment_details'),
    #     ]
    #     return custom_urls + urls
    #
    # # class Media:
    # #     js = ('admin/js/custom_admin.js',)


    def enter_payment_details(self, request, queryset):
        # Your custom action logic here
        # You can render a custom template for entering payment details
        # or redirect to a specific URL where you have implemented the form
        return HttpResponse("This is a placeholder for entering payment details.")

    actions = [enter_payment_details]


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
admin.site.register(Accounts)
admin.site.register(Merchants, MerchantsAdmin)
# admin.site.register(Sales)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Dashboard)
