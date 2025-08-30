"""
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from expenses.models import Expense
from expenses.forms import ExpenseForm
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'accounts/dashboard.html', {'form': form})
"""


