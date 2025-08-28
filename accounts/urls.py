from django.urls import path
from .views import register_view, login_view, logout_view, dashboard
from . import views


urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/',    login_view,    name='login'),
    path('logout/',   logout_view,   name='logout'),
    path('dashboard/', dashboard,    name='dashboard'),
    path('user-report/', views.user_report, name='user_report'),
    
]
