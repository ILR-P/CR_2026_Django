from django.shortcuts import render, redirect
from .forms import UnitForm

def add_unit(request):
    if request.method == 'POST':
        form = UnitForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('/unit')
    else:
        form = UnitForm()

    return render(request, 'army/unit_form.html', {'form': form})