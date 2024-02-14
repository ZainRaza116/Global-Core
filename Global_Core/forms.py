from django import forms
from .models import Sales
from django.contrib import admin

from django.forms.models import inlineformset_factory
from .models import Sales, Card


class CardInline(admin.TabularInline):
    model = Card
    extra = 1  # Number of extra forms to display

class SalesAdmin(admin.ModelAdmin):
    inlines = [CardInline]

admin.site.register(Sales, SalesAdmin)
