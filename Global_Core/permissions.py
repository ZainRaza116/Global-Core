from django.contrib import admin
from .models import Sales


class SalesAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_staff:
            return queryset

        return queryset.none()

    def has_add_permission(self, request):
        # Grant permission to add sales only to staff users
        return request.user.is_staff
