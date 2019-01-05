from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import mixins as auth_mixins
from django.contrib.auth import logout

from .models import User

import logging
logger = logging.getLogger('admin_log')


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('web-dashboard-view')
        return render(request, 'login.html')


class LogoutView(auth_mixins.LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        logger.info(f'[# System] User {request.user.username} successfully logged out')
        logout(request)
        return redirect('web-dashboard-view')


class AdminRegisterView(auth_mixins.UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):
        return render(request, 'admin_register.html')
    

class RegisterView(View):
    def get(self, request, login_hash):
        try:
            user = User.objects.get(login_hash=login_hash)
        except Exception as e:
            logger.info(f'[# System] User with hash {login_hash} is trying to register second time, error {str(e)}')
            return redirect('web-dashboard-view')
        return render(request, 'register.html', context={'user': user, 'login_hash': login_hash})
