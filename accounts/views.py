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
    
        


#admin_view new
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Expense, Team
from .forms import TeamForm
from django.contrib.auth import get_user_model
from django.db.models import Q
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
            'approved': all_approved,
        })

    paginator = Paginator(user_data, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    teams = Team.objects.prefetch_related('members').all()
    team_form = TeamForm()

    # ✅ Exclude users already in any team (member or lead)
    assigned_users = set()
    for team in teams:
        assigned_users.update(team.members.all())
        if team.team_lead:
            assigned_users.add(team.team_lead)

    eligible_members = User.objects.exclude(id__in=[u.id for u in assigned_users])
    eligible_leads = eligible_members

    return render(request, 'accounts/admin_dashboard.html', {
        'user_data': page_obj,
        'teams': teams,
        'team_form': team_form,
        'eligible_members': eligible_members,
        'eligible_leads': eligible_leads,
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



from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from datetime import date
from .models import Expense
"""
@require_POST
def approve_expense(request, user_id):
    today = date.today()

    # Approve only past expenses
    updated_count = Expense.objects.filter(
        user_id=user_id,
        is_approved=False,
        date__lt=today
    ).update(is_approved=True)

    # Get user info
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    

    
    print(">>> DEBUG: Approving expenses for:", user.username, user.email)
    print(">>> DEBUG: Updated count:", updated_count)

    # Send email to user always (chahe record update ho ya pehle se approved ho)
    send_mail(
        subject='Your Expenses Are Approved!',
        message=f"Hello {user.username},\n\nYour expenses have been approved by the admin.",
        from_email='admin@myexpenses.com',  # match with DEFAULT_FROM_EMAIL
        recipient_list=[user.email],
        fail_silently=False,
    )
    
    print(">>> DEBUG: Email sent to:", user.email)

    return redirect('/accounts/admin-dashboard/?approved=true')
"""

@require_POST
def approve_expense(request, user_id):
    today = date.today()

    updated_count = Expense.objects.filter(
        user_id=user_id,
        is_approved=False,
        date__lt=today
    ).update(is_approved=True)

    # Get user info
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)

    # Send email to user
    send_mail(
        subject="Your Expenses Are Approved!",
        message=f"Hello {user.username},\n\nYour expenses have been approved by the admin.",
        from_email="admin@myexpenses.com",   # or use DEFAULT_FROM_EMAIL
        recipient_list=[user.email],         # this is where YOPmail works!
        fail_silently=False,
    )

    return redirect("/accounts/admin-dashboard/?approved=true")






# delete team.
from django.shortcuts import get_object_or_404, redirect
from .models import Team
from django.contrib import messages

def delete_team(request, team_id):
    if request.method == 'POST':
        team = get_object_or_404(Team, id=team_id)
        team.delete()
        messages.success(request, f'Team "{team.name}" has been deleted.')
    return redirect('admin_dashboard')


#saving team
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
User = get_user_model()

def make_admin(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = User.objects.get(id=user_id)
        user.is_staff = True
        user.is_superuser = True
        user.save()
    return redirect('admin_dashboard')


# saving team
"""
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from .models import Team
from django.views.decorators.http import require_POST


@require_POST
def create_team(request):
    form = TeamForm(request.POST)
    if form.is_valid():
     team = form.save(commit=False)
     team.team_lead = form.cleaned_data['team_lead']
     team.save()
     form.save_m2m()

"""
# create team

from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from .forms import TeamForm
from .models import Team
from django.contrib import messages  # ✅ import messages
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

@require_POST
def create_team(request):
    form = TeamForm(request.POST)
    if form.is_valid():
        team = form.save(commit=False)
        team.team_lead = form.cleaned_data['team_lead']
        team.save()
        form.save_m2m()   # members relation save

        # 🔹 Get Team Lead and Members
        lead = team.team_lead
        members = team.members.all()

        # 🔹 Send email to Team Lead
        if lead and lead.email:
            send_mail(
                subject="You are assigned as Team Lead!",
                message=f"Hello {lead.username},\n\nYou are now the Team Lead of '{team.name}'.",
                from_email="admin@myexpenses.com",
                recipient_list=[lead.email],
                fail_silently=False,
            )

        # 🔹 Send email to Team Members
        for member in members:
            if member.email:   # avoid empty emails
                send_mail(
                    subject="You have been added to a new Team",
                    message=f"Hello {member.username},\n\nYou have been added to the team '{team.name}' under the lead {lead.username}.",
                    from_email="admin@myexpenses.com",
                    recipient_list=[member.email],
                    fail_silently=False,
                )

        messages.success(request, f"✅ Team '{team.name}' has been created successfully!")
    else:
        messages.error(request, "❌ Failed to create team. Please check the form.")

    return redirect('admin_dashboard')




"""
@require_POST
def create_team(request):
    form = TeamForm(request.POST)
    if form.is_valid():
        team = form.save(commit=False)
        team.team_lead = form.cleaned_data['team_lead']
        team.save()
        form.save_m2m()
        messages.success(request, f"✅ Team '{team.name}' has been created successfully!")
    else:
        messages.error(request, "❌ Failed to create team. Please check the form.")
    return redirect('admin_dashboard')
"""




# remove member from team
@require_POST
def remove_team_members(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    members_to_remove = request.POST.getlist('members_to_remove')

    for member_username in members_to_remove:
        user = User.objects.get(username=member_username)
        team.members.remove(user)

    messages.success(request, f"Selected members removed from team '{team.name}'.")
    return redirect('admin_dashboard')
