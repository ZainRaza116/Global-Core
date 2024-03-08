from rest_framework import permissions
from django.contrib.auth.models import Group


class IsEmployeePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Print the user's groups
        print("User Groups:", request.user.groups.all())

        # Check if the user belongs to the "Employee" group
        employee_group = Group.objects.get(name='Employee')
        if employee_group in request.user.groups.all():
            print("User is an Employee")
            return True

        return False
