from django.urls import path
from .views import register_view, login_view, logout_view, dashboard, ExpenseListAPI,approve_expense,delete_team, update_expense_dates, user_report, admin_login_view, admin_dashboard, user_detail_report

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('user-report/', user_report, name='user_report'),
    path('api/expenses/', ExpenseListAPI.as_view(), name='expense_api'),  # ✅ API URL
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-login/', admin_login_view, name='admin_login_view'),
    path('admin/user/<int:user_id>/update-dates/', update_expense_dates, name='update_expense_dates'),


   
    path('admin/user/<int:user_id>/report/', user_detail_report, name='user_detail_report'),
    path('approve-expense/<int:user_id>/', approve_expense, name='approve_expense'),
    path('delete-team/<int:team_id>/', delete_team, name='delete_team'),
    


   
    



    

]
