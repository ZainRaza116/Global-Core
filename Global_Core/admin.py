from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.models import Group


get_user_model()


class CustomUserAdminForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)

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


class SalesAdmin(admin.ModelAdmin):
    list_display = ('name', 'added_by')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser and request.user.groups.filter(name='Employee').exists():
            qs = qs.filter(added_by=request.user)
        return qs


class MerchantsAdmin(admin.ModelAdmin):
    list_display = ['merchant', 'merchant_dba', 'account_type', 'merchant_type']


class LinksAdmin(admin.ModelAdmin):
    list_display = ['merchant_link', 'link', 'amount']


class ExpensesAdmin(admin.ModelAdmin):
    list_display = ['date_incurred', 'title', 'amount', 'expenses_type']


class SalesAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_staff:
            return queryset
        return queryset.none()

    def has_add_permission(self, request):
        return request.user.is_staff


admin.site.register(Sales, SalesAdmin)
admin.site.register(Expenses, ExpensesAdmin)
admin.site.register(Company)
admin.site.register(Links, LinksAdmin)
admin.site.register(Accounts)
admin.site.register(Merchants, MerchantsAdmin)
# admin.site.register(Sales)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Dashboard)
