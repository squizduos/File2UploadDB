import logging
logger = logging.getLogger('admin_log')

import os
import json

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

from .forms import DocumentUpdateForm, DocumentUploadForm
from .models import Document
from .utils import file_read_from_tail
from .tasks import prepare_and_upload_file


@method_decorator(csrf_exempt, name='dispatch')
class DashboardView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        return render(request, 'dashboard.html', context={})


@method_decorator(csrf_exempt, name='dispatch')
class AdminDashboardView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    login_url = "/login/"
    def get(self, request):
        log = file_read_from_tail('log/info.log', 10000)
        return render(request, 'admin-dashboard.html', context={'log': log})


@method_decorator(csrf_exempt, name='dispatch')
class UploadToServerView(LoginRequiredMixin, View):
    login_url = "/login/"
    
    def prepare_uploaded_file(self, model):
        response = {'file_id': model.id, 'file_storage': model.file_storage, 'enabled_for_editing': ['file_type']}
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
        last_successful_load = Document.objects.filter(user=model.user, status=2).last()
        if last_successful_load:
            response['db_type'] = last_successful_load.db_type
            response['db_host'] = last_successful_load.db_host
            response['db_port'] = last_successful_load.db_port
            response['db_name'] = last_successful_load.db_name
            response['db_username'] = last_successful_load.db_username
            response['db_password'] = last_successful_load.db_password
            
        return response
    
    def post(self, request):
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            model = form.save(commit=False)
            model.user = request.user
            model.save()
            logger.info(f'New file {model.id} is successfully uploaded by user {request.user.username} and preparing to upload to DBMS')
            return JsonResponse(self.prepare_uploaded_file(model))
        else:
            logger.info(f'File uploading by user {request.user.username} error')
            return JsonResponse({"error": form.errors}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class UploadToDBView(LoginRequiredMixin, View):
    login_url = "/login/"
    
    def post(self, request):
        try:
            data = json.loads(request.body)
        except Exception as e:
            logger.info(f'File preparing by user {request.user.username} error; incorrect JSON data')
            return JsonResponse({"error": "Incorrect JSON data, error: " + str(e)}, status=400)
        try:
            document = Document.objects.get(id=data['file_id'])
        except Exception as e:
            logger.info(f'File preparing #{data["file_id"]} by user {request.user.username} error; file not found')
            return JsonResponse({"error": "File not found"}, status=404)
        if data['file_header_line'] == 'not applicable':
            data['file_header_line'] = ""
        if data['file_separator'] == 'not applicable':
            data['file_separator'] = ""
        form = DocumentUpdateForm(data, instance=document)
        if form.is_valid():
            model = form.save(commit=False)
            model.user = request.user
            model.save()
            prepare_and_upload_file.delay(model.id)
            logger.info(f'File {model.id} uploading to DBMS is started by {request.user.username}')
            return JsonResponse({"status": "uploading"})
        else:
            logger.info(f'File uploading by user {request.user.username} error')
            return JsonResponse({"error": form.errors}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class UploadToDBCheckStatusView(LoginRequiredMixin, View):
    login_url = "/login/"
    
    def get(self, request, file_id):
        try:
            document = Document.objects.get(id=file_id)
        except Exception as e:
            logger.info(f'File checking status #{data["file_id"]} by user {request.user.username} error; file not found')
            return JsonResponse({"error": "File not found"}, status=404)
        if document.status == 0:
            return JsonResponse({"status": 0, "percent": 0})
        if document.status == 1:
            return JsonResponse({"status": 1, "percent": document.uploading_percent})
        if document.status == 2:
            return JsonResponse({"status": 2, "percent": 100})
        if document.status == -1:
            return JsonResponse({"status": -1, "error": document.error})
            
@method_decorator(csrf_exempt, name='dispatch')
class UploadToServerCancelView(LoginRequiredMixin, View):
    login_url = "/login/"
    
    def get(self, request, file_id):
        try:
            document = Document.objects.get(id=file_id)
        except Exception as e:
            logger.info(f'File checking status #{file_id} by user {request.user.username} error; file not found')
            return JsonResponse({"error": "File not found, error: " + str(e)}, status=404)
        try:
            document.delete()
            logger.info(f'File upload #{file_id} cancelled by user {request.user.username}')
            return JsonResponse({"error": "File deleted successfully"}, status=200)
        except Exception as e:
            logger.info(f'File upload #{file_id} cancelling by user {request.user.username} error {str(e)}')
            return JsonResponse({"error": str(e)}, status=400)
