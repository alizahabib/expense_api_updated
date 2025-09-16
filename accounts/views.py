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


from django.shortcuts import render
from .forms import ExpenseForm
from .models import Expense
from django.contrib.auth.decorators import login_required
import datetime

@login_required
def dashboard(request):
    saved = False  # ✅ for SweetAlert success

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user

            # ✅ Date-based approval logic
            if expense.date < datetime.date.today():
                expense.is_approved = False  # Needs admin approval
            else:
                expense.is_approved = True  # Auto approved

            expense.save()
            saved = True
            form = ExpenseForm()  # Clear form after save
    else:
        form = ExpenseForm()

    # ✅ Show only approved expenses to the user
    expenses = Expense.objects.filter(user=request.user, is_approved=True).order_by('-date')

    return render(request, 'accounts/dashboard.html', {
        'form': form,
        'user': request.user,
        'expenses': expenses,
        'saved': saved,
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
        
        # 🔽 Sort the expenses by date in ascending order
    expenses = expenses.order_by('date')    
    
    
     # Pagination: 5 expenses per page
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('accounts/partials/expense_table.html', {'page_obj': page_obj})
        return JsonResponse({'html': html})


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
        'page_obj': page_obj,
        'total_amount': total_amount,
        'category': category,
        'start_date': start_date,
        'end_date': end_date,
        'highest_category': highest_category['category'] if highest_category else None,
        'category_count': expenses.count(),
        'categories': categories,  #  sent to template
    }

    return render(request, 'accounts/user_report.html', context)





# for swagger
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
    
        
"""
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

"""

"""
from datetime import date
from django.db.models import Sum
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.shortcuts import render
from .models import Expense

User = get_user_model()

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    today = date.today()
    users = User.objects.all()
    user_reports = []

    for user in users:
        all_expenses = Expense.objects.filter(user=user)

        approved_expenses = all_expenses.filter(is_approved=True)
        total = approved_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        count = approved_expenses.count()

        # Show approve button if user has any past-dated unapproved expense
        has_past_unapproved = all_expenses.filter(is_approved=False, date__lt=today).exists()

        user_reports.append({
            'user': user,
            'total_expenses': total,
            'expense_count': count,
            'show_approve': has_past_unapproved,
        })

    return render(request, 'accounts/admin_dashboard.html', {
        'user_reports': user_reports
    })

"""



# views.py
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Expense, Team, User
from .forms import TeamForm

def admin_dashboard(request):
    users = User.objects.all()
    user_data = []

    for user in users:
        expenses = Expense.objects.filter(user=user)
        total = sum(e.amount for e in expenses)
        entry_count = expenses.count()
        all_approved = not expenses.filter(is_approved=False).exists()

        user_data.append({
            'user': user,
            'total': total,
            'entry_count': entry_count,
            'approved': all_approved
        })

    # ✅ PAGINATE the FINAL LIST (user_data), not the queryset
    paginator = Paginator(user_data, 5)  # 5 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    teams = Team.objects.prefetch_related('members').all()
    team_form = TeamForm()

    return render(request, 'accounts/admin_dashboard.html', {
        'user_data': page_obj,      # ✅ now paginated
        'teams': teams,
        'team_form': team_form,
    })





from django.db.models import Sum, Count
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Expense, CustomUser
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import JsonResponse


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
    
        # Pagination
    paginator = Paginator(expenses, 5)  # 5 expenses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('accounts/partials/expense_table.html', {
            'page_obj': page_obj,
        }, request=request)
        return JsonResponse({'table_html': html})


    return render(request, 'accounts/user_detail_report.html', {
        'report_owner': user,
        'page_obj': page_obj,
        'expenses': expenses,
        'total': total,
        'entry_count': entry_count,
        'top_category': top_category,
        'categories': categories,
        'selected_category': category,
        'start_date': start_date,
        'end_date': end_date,
    })



# giving admin the right to change the date of the user expense item.

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




# to hold the expense record when the flag is FALSE before approving.

from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from .models import Expense
from datetime import date


@require_POST
def approve_expense(request, user_id):
    today = date.today()
    Expense.objects.filter(user_id=user_id, is_approved=False, date__lt=today).update(is_approved=True)
    return redirect('/accounts/admin-dashboard/?approved=true')




from django.shortcuts import get_object_or_404, redirect
from .models import Team
from django.contrib import messages

def delete_team(request, team_id):
    if request.method == 'POST':
        team = get_object_or_404(Team, id=team_id)
        team.delete()
        messages.success(request, f'Team "{team.name}" has been deleted.')
    return redirect('admin_dashboard')






