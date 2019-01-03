import os
import json

from django.views.generic import View

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.serializers import serialize

from .forms import DocumentUpdateForm, DocumentUploadForm
from .models import Document
from .utils import file_read_from_tail, decode_db_connection, encode_db_connection
from .tasks import DocumentTask

from celery.result import AsyncResult

import logging
logger = logging.getLogger('admin_log')


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
        response = {}
        response['enabled_for_editing'] = ['file_type']

        response['file_id'] = model.id, 
        response['file_storage'] = model.file_storage
        response['file_path'] = model.document.path
        response['file_name'] = os.path.basename(model.document.name)
        filename, extension = os.path.splitext(model.original_filename)
        if extension.upper() in ['.CSV', '.XLS', '.XLSX', '.DTA']:
            response['file_type'] = extension.upper()[1:]
        else:
            response['file_type'] = 'CSV'
        if response['file_type'] == 'CSV':
            response['file_header_line'] = ""
            response['file_separator'] = ""
            response['enabled_for_editing'].append('file_header_line')
            response['enabled_for_editing'].append('file_separator')
        elif response['file_type'] == 'XLS':
            response['file_header_line'] = ""
            response['enabled_for_editing'].append('file_header_line')
            response['file_separator'] = 'not applicable'
        elif response['file_type'] == 'XLSX':
            response['file_header_line'] = ""
            response['enabled_for_editing'].append('file_header_line')
            response['file_separator'] = 'not applicable'
        elif response['file_type'] == 'DTA':
            response['file_header_line'] = 'not applicable'
            response['file_separator'] = 'not applicable'
        response['table_name'] = filename
        response['db_connection'] = []
        db_connections = list(Document.objects.filter(user=model.user, status=2).values_list('db_connection', flat=True).distinct())
        for conn in db_connections:
            fields = decode_db_connection(conn)
            response['db_connection'].append({"name": f"{fields['db_type']} ({fields['db_host']}), by user {fields['db_username']}, to db {fields['db_name'] if fields['db_type'] == 'PostgreSQL' else fields['db_sid']}", "value": conn})
        response['enabled_for_editing'] += ["table_name", "db_type", "db_host", "db_port", "db_username", "db_password", "db_name", "file_id"]
        return response

    def post(self, request):
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            model = form.save(commit=False)
            model.user = request.user
            model.original_filename = request.FILES['document'].name
            model.save()
            logger.info(
                f'File {model.id} is successfully uploaded by user {model.user.username} and preparing to load on DBMS'
            )
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

        form = DocumentUpdateForm(data, instance=document)
        if form.is_valid():
            model = form.save(commit=False)
            model.user = request.user
            model.save()
            # Running task
            new_task = DocumentTask()
            task_run = new_task.delay(model.id)
            model.task_id = task_run.task_id
            model.save()
            logger.info(f'File {model.id} uploading to DBMS is started by {request.user.username}')
            return JsonResponse({"status": "uploading"})
        else:
            logger.info(f'File uploading by user {request.user.username} error')
            return JsonResponse({"error": form.errors}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class UploadedFileView(LoginRequiredMixin, View):
    login_url = "/login/"
    
    def get(self, request, file_id):
        try:
            document = Document.objects.get(id=file_id)
        except Exception as e:
            logger.info(f'File checking status #{data["file_id"]} by user {request.user.username} error; file not found')
            return JsonResponse({"status": -1, "error": "File not found"}, status=404)
        response = {"status": document.status, "error": document.error, "percent": document.percent}
        return JsonResponse(response)

    def delete(self, request, file_id):
        try:
            document = Document.objects.get(id=file_id)
        except Exception as e:
            logger.info(f'File checking status #{file_id} by user {request.user.username} error; file not found')
            return JsonResponse({"error": "File not found, error: " + str(e)}, status=404)
        try:
            document.document.delete()
            logger.info(f'File upload #{file_id} cancelled by user {request.user.username}')
            return JsonResponse({"error": "File deleted successfully"}, status=200)
        except Exception as e:
            logger.info(f'File upload #{file_id} cancelling by user {request.user.username} error {str(e)}')
            return JsonResponse({"error": str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class UtilsDecodeDBString(LoginRequiredMixin, View):
    login_url = "/login/"
    def post(self, request):
        if "db_connection" in request.POST:
            return JsonResponse(decode_db_connection(request.POST["db_connection"]))
        else:
            return JsonResponse({"error": "No db_connection provided"}, status=400)


