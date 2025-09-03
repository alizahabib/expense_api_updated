from django.shortcuts import render
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

# For Users-Login

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


# For Admin-Login

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm
from django.contrib import messages

def admin_login_view(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None and user.is_superuser:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Only admins can log in here.')

    return render(request, 'accounts/login.html', {'form': form})





def logout_view(request):
    logout(request)
    return redirect('register')


from expenses.forms import ExpenseForm
from django.contrib.auth.decorators import login_required
from .forms import ExpenseForm
from .models import Expense


@login_required
def dashboard(request):
    saved = False 

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
        'categories': categories,  #  sent to template
    }

    return render(request, 'accounts/user_report.html', context)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Expense
from .serializers import ExpenseSerializer

class ExpenseListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        expenses = Expense.objects.filter(user=request.user)
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)
    
    
    
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.contrib.auth import get_user_model
from .models import Expense

User = get_user_model()

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    users = User.objects.all()
    user_reports = []

    for user in users:
        expenses = Expense.objects.filter(user=user)
        total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        user_reports.append({
            'user': user,
            'total_expenses': total,
            'expense_count': expenses.count(),
        })

    return render(request, 'accounts/admin_dashboard.html', {
        'user_reports': user_reports
    })


from django.db.models import Sum, Count
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Expense, CustomUser

@user_passes_test(lambda u: u.is_superuser)
def user_detail_report(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    expenses = Expense.objects.filter(user=user).order_by('-date')

    # Get filter values
    category = request.GET.get('category', 'all')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Apply filters
    if category != 'all':
        expenses = expenses.filter(category=category)
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)

    # Total amount
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Entry count
    entry_count = expenses.count()

    # Top Category
    top_category_data = (
        expenses.values('category')
        .annotate(total_spent=Sum('amount'))
        .order_by('-total_spent')
        .first()
    )
    top_category = top_category_data['category'] if top_category_data else None

    # All categories for dropdown
    categories = Expense.objects.values_list('category', flat=True).distinct()

    return render(request, 'accounts/user_detail_report.html', {
        'report_owner': user,
        'expenses': expenses,
        'total': total,
        'entry_count': entry_count,
        'top_category': top_category,
        'categories': categories,
        'selected_category': category,
        'start_date': start_date,
        'end_date': end_date,
    })



from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from .models import Expense

@user_passes_test(lambda u: u.is_superuser)
def update_expense_dates(request, user_id):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('date_'):
                expense_id = key.split('_')[1]
                try:
                    expense = Expense.objects.get(id=expense_id, user_id=user_id)
                    expense.date = value
                    expense.save()  # ✅ saves date change to DB
                except Expense.DoesNotExist:
                    continue
    return redirect('user_detail_report', user_id=user_id)
