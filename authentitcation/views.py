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


from .models import User

@method_decorator(csrf_exempt, name='dispatch')
class LoginPageView(TemplateView):
    template_name = "signup.html"


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        if not 'username' in request.POST or not 'email' in request.POST or not 'password' in request.POST:
            return render(request, 'signup.html', context={"register_errors": "Not all fields are provided"})
        username = request.POST.get('username')    
        email = request.POST.get('email')            
        password = request.POST.get('password')
        user = User.objects.create_user(username=username, email=email, password=password)
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('home')

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        if not 'username' in request.POST or not 'password' in request.POST:
            return render(request, 'signup.html', context={"login_errors": "Not all fields are provided"})
        username = request.POST.get('username')    
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'signup.html', context={"login_errors": "Username or password is incorrect"})
            


@csrf_exempt
@login_required
def HomeView(request):
    return HttpResponse('Successfully!')
