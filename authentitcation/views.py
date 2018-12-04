from django.shortcuts import render

# Create your views here.

from django.views.generic import TemplateView, View

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


from .models import User
from .utils import send_registration_email

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'login.html')
    
    def post(self, request):
        if not 'username' in request.POST or not 'password' in request.POST:
            return render(request, 'login.html', context={"login_errors": "Not all fields are provided"})
        username = request.POST.get('username')    
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', context={"login_errors": "Username or password is incorrect"})

@method_decorator(csrf_exempt, name='dispatch')
class AdminRegisterView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):
        return render(request, 'admin_register.html')

    def post(self, request):
        if not 'username' in request.POST or not 'email' in request.POST:
            return render(request, 'admin_register.html', context={"register_errors": "Not all fields are provided"})
        username = request.POST.get('username')    
        email = request.POST.get('email')            
        try:
            user = User.objects.create_user(username=username, email=email)
        except Exception as e:
            return render(request, 'admin_register.html', context={"register_errors": "This user is already exist or have incorrect data."})
        try:
            send_registration_email(user)
        except Exception as e:
            return render(request, 'admin_register.html', context={"register_errors": "Can not send mail."})
        return render(request, 'admin_register.html', context={"success_message": "User is successfully added!"})

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def get(self, request, login_hash):
        try:
            user = User.objects.get(login_hash=login_hash)
        except:
            return render(request, 'login.html', context={"login_errors": "User was registered successfully; please login using login and password"})
        return render(request, 'register.html', context={'user': user})

    def post(self, request, login_hash):
        if not 'password' in request.POST or not 'confirm-password' in request.POST:
            return render(request, 'register.html', context={"register_errors": "Not all fields are provided"})
        # login_hash = request.POST.get('login_hash')    
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        try:
            user = User.objects.get(login_hash=login_hash)
        except:
            return render(request, 'login.html', context={"login_errors": "User was registered successfully; please login using login and password"})
        if password != confirm_password:
            return render(request, 'register.html', context={"register_errors": "Password and password confirmation are not match", "user": user})
        user.set_password(password)
        user.login_hash = ''
        user.save()
        login(request, user)
        return redirect('dashboard')


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(LoginRequiredMixin, View):
    login_url = "/login/"
    def get(self, request):
        logout(request)
        return redirect('dashboard')
