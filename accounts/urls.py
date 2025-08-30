from django.urls import path
from .views import register_view, login_view, logout_view, dashboard, ExpenseListAPI, user_report

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('user-report/', user_report, name='user_report'),
    path('api/expenses/', ExpenseListAPI.as_view(), name='expense_api'),  # ✅ API URL
]
