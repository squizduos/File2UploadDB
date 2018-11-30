"""imgdownloader URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from authentitcation.views import AdminRegisterView, RegisterView, LoginView, LogoutView
from fileupload.views import DashboardView, AdminDashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('dashboard/', DashboardView.as_view(), name='dashboard2'),
    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(), name="login-view"),
    path('logout/', LogoutView.as_view(), name="login-view"),

    path('signup/admin/register',AdminRegisterView.as_view()),
    path('signup/register/<str:login_hash>', RegisterView.as_view())
]
