from django.shortcuts import render
from django.forms import formset_factory
from .forms import SalesForm


def add_sales(request):
    SalesFormSet = formset_factory(SalesForm, can_delete=True)
    if request.method == 'POST':
        formset = SalesFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.save()
            return render(request, 'success.html')
    else:
        formset = SalesFormSet()
    return render(request, 'add_sales.html', {'formset': formset})
