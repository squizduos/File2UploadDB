from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import mixins as auth_mixins
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse_lazy as reverse

from .models import User
from .serializers import UserLoginRequestSerializer

from rest_auth.models import TokenModel

import logging
logger = logging.getLogger('admin_log')


class LoginView(View):
    def create_token(self, user, *args, **kwargs):
        token, _ = TokenModel.objects.get_or_create(user=user)
        return token

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('web-dashboard-view')
        return render(request, 'login.html')

    def post(self, request):
        serializer = UserLoginRequestSerializer(data=request.POST)
        if serializer.is_valid():
            username = serializer.data.get('username')    
            password = serializer.data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                logger.info(f'[# System] User {username} successfully logged in')
                response = redirect('main-page')
                response.set_cookie('token', self.create_token(user))
                return response
            else:
                logger.info(f'[# System] User {username} trying to log in, incorrect username or password')
                return render(request, 'login.html', context={"login_errors": "Username or password is incorrect"})
        else:
            logger.info(f'[# System] Incorrect request on /login/ endpoint')
            return render(request, 'login.html', context={"login_errors": "Not all fields are provided"})


class LogoutView(auth_mixins.LoginRequiredMixin, View):
    login_url = reverse('web-login-view')

    def get(self, request):
        logger.info(f'[# System] User {request.user.username} successfully logged out')
        logout(request)
        return redirect('web-dashboard-view')


class AdminRegisterView(auth_mixins.UserPassesTestMixin, View):
    login_url = reverse('web-login-view')

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):
        return render(request, 'admin_register.html')
    

class RegisterView(View):
    login_url = reverse('web-login-view')

    def get(self, request, login_hash):
        try:
            user = User.objects.get(login_hash=login_hash)
        except Exception as e:
            logger.info(f'[# System] User with hash {login_hash} is trying to register second time, error {str(e)}')
            return redirect('web-dashboard-view')
        return render(request, 'register.html', context={'user': user, 'login_hash': login_hash})
