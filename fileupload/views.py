from django.shortcuts import render

# Create your views here.

from django.views.generic import TemplateView, View

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

@method_decorator(csrf_exempt, name='dispatch')
class DashboardView(LoginRequiredMixin, View):
    login_url = "/login/"
    def get(self, request):
        return render(request, 'dashboard.html', context={})
    
    # def post(self, request):
    #     if not 'username' in request.POST or not 'password' in request.POST:
    #         return render(request, 'login.html', context={"login_errors": "Not all fields are provided"})
    #     username = request.POST.get('username')    
    #     password = request.POST.get('password')
    #     user = authenticate(username=username, password=password)
    #     if user:
    #         login(request, user)
    #         return redirect('home')
    #     else:
    #         return render(request, 'login.html', context={"login_errors": "Username or password is incorrect"})

@method_decorator(csrf_exempt, name='dispatch')
class AdminDashboardView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    login_url = "/login/"
    def get(self, request):
        return render(request, 'admin-dashboard.html', context={})
    