from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import RegisterForm, LoginForm

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None and user.is_active:
                login(request, user)
                return render(request, 'accounts/login.html', {
                    'form': form,
                    'login_success': True,  # 👈 Trigger alert
                    'user': user
                })
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('register')


from django.shortcuts import render, redirect
from expenses.forms import ExpenseForm
from django.contrib.auth.decorators import login_required
from .forms import ExpenseForm
from .models import Expense


@login_required
def dashboard(request):
    saved = False  # ✅ Add this line

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            saved = True  # ✅ Flag for alert
            form = ExpenseForm()  # clear form after save
    else:
        form = ExpenseForm()

    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    return render(request, 'accounts/dashboard.html', {
        'form': form,
        'user': request.user,
        'expenses': expenses,
        'saved': saved,  # ✅ send flag to template
    })




from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils.dateparse import parse_date
from .models import Expense

@login_required
def user_report(request):
    expenses = Expense.objects.filter(user=request.user)

    # Get unique categories for dropdown
    categories = Expense.objects.filter(user=request.user).values_list('category', flat=True).distinct()

    # Filters
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if category:
        expenses = expenses.filter(category=category)
    if start_date:
        expenses = expenses.filter(date__gte=parse_date(start_date))
    if end_date:
        expenses = expenses.filter(date__lte=parse_date(end_date))

    total_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    highest_category = (
        Expense.objects.filter(user=request.user)
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
        .first()
    )

    context = {
        'expenses': expenses,
        'total_amount': total_amount,
        'category': category,
        'start_date': start_date,
        'end_date': end_date,
        'highest_category': highest_category['category'] if highest_category else None,
        'category_count': expenses.count(),
        'categories': categories,  # 🔥 sent to template
    }

    return render(request, 'accounts/user_report.html', context)