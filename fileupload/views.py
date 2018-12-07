import logging
logger = logging.getLogger('admin_log')

import os

from django.shortcuts import render

# Create your views here.

from django.views.generic import TemplateView, View

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms.models import model_to_dict

from .forms import DocumentForm
from .utils import file_read_from_tail


@method_decorator(csrf_exempt, name='dispatch')
class DashboardView(LoginRequiredMixin, View):
    login_url = "/login/"

    def prepare_uploaded_file(self, model):
        response = {'file_storage': model.storage, 'enabled_for_editing': ['file_type']}
        response['file_path'] = model.document.path
        response['file_name'] = os.path.basename(model.document.name)
        if response['file_name'].split('.')[-1].upper() in ['CSV', 'XLS', 'XLSX', 'DTA']:
            response['file_type'] = response['file_name'].split('.')[-1].upper() 
        else:
            response['file_type'] == 'CSV'
        if response['file_type'] == 'CSV':
            response['enabled_for_editing'].append('file_header_line')
            response['enabled_for_editing'].append('file_separator')
        elif response['file_type'] == 'XLS':
            response['enabled_for_editing'].append('file_header_line')
            response['file_separator'] = 'not applicable'
        elif response['file_type'] == 'XLSX':
            response['enabled_for_editing'].append('file_header_line')
            response['file_separator'] = 'not applicable'
        elif response['file_type'] == 'DTA':
            response['file_header_line'] = 'not applicable'
            response['file_separator'] = 'not applicable'
        return response

    def get(self, request):
        return render(request, 'dashboard.html', context={})
    
    def post(self, request):
        if request.method == 'POST':
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                model = form.save()
                logger.info(f'New file {{model.id}} is successfully uploaded by user {{request.user.username}} and preparing to upload to DBMS')
                return JsonResponse(self.prepare_uploaded_file(model))
            else:
                logger.info(f'File uploading by user {{request.user.username}} error')
                return JsonResponse({"error": form.errors})
        else:
            logger.info(f'Incorrect request at /dashboard/ endpoint')
            return JsonResponse({'error': 'Call via POST this method'})


@method_decorator(csrf_exempt, name='dispatch')
class AdminDashboardView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    login_url = "/login/"
    def get(self, request):
        log = file_read_from_tail('info.log', 10000)
        return render(request, 'admin-dashboard.html', context={'log': log})
    