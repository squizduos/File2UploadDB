import json

from django.http import JsonResponse, Http404
from django.core.exceptions import PermissionDenied

from rest_framework import views
from rest_framework.response import Response
from rest_framework import authentication, permissions, parsers

from . import serializers
from .models import Document
from .tasks import DocumentTask

from imgdownloader.exceptions import get_exception_definition

from drf_yasg.utils import swagger_auto_schema


import logging
logger = logging.getLogger('admin_log')


class BaseUploadAPIView(views.APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    model = Document

    def has_permission(self, request, obj):
        if request.user and request.user.is_authenticated:
            return True if request.user.is_superuser or obj.user == request.user else False
        else:
            return False
    
    def launch_task(self, obj: Document):
        new_task = DocumentTask()
        task_run = new_task.delay(obj.id)
        obj.task_id = task_run.task_id
        obj.save()

    def get_object(self, request, pk):
        try:
            obj = self.model.objects.get(pk=pk) 
        except self.model.DoesNotExist:
            raise Http404
        else:
            if not self.has_permission(request, obj):
                raise PermissionDenied
            return obj


class DocumentUploadAPIView(BaseUploadAPIView): 
    parser_classes = (parsers.MultiPartParser, )

    @swagger_auto_schema(
        request_body=serializers.DocumentUploadRequestSerializer,
        responses={
            201: serializers.DocumentUploadResponseSerializer,
            400: "Validation errors",
        },        
        tags=['upload_db']
    )
    def post(self, request, format=None):
        """
        Uploads new document to server and returns detected info about it.

         - Authorization: Token <token>
         - Access scope: users
        """
        request_serializer = serializers.DocumentUploadRequestSerializer(
            data=request.data,
            original_filename=request.data['document'].name,
            user=request.user
        )
        if request_serializer.is_valid():
            document = request_serializer.save()
            response_serializer = serializers.DocumentUploadResponseSerializer(document)
            logger.info(
                f'[# Document {document.id}] File is successfully uploaded to server '
                f'by user {document.user.username} and preparing to load on DBMS'
            )
            return Response(response_serializer.data, status=201)
        else:
            logger.info(
                f'[# Document {document.id}] File uploading by user {request.user.username} failed; '
                f'data validation failed, errors are: {json.dumps(request_serializer.errors)}'
            )
            return Response(request_serializer.errors, status=400)


class DocumentAPIView(BaseUploadAPIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            200: serializers.DocumentStatusSerializer,
            403: get_exception_definition(403),
            404: get_exception_definition(404),
        },        
        tags=['upload_db']
    )
    def get(self, request, document_id, format=None):
        """
        Uploads new document to server and returns detected info about it.

         - Authorization: Token <token>
         - Access scope: users
        """
        document = self.get_object(request, document_id)
        response_serializer = serializers.DocumentStatusSerializer(document)
        return JsonResponse(response_serializer.data, status=200)
    
    @swagger_auto_schema(
        request_body=serializers.DocumentUpdateSerializer,
        responses={
            201: serializers.DocumentStatusSerializer,
            400: "Validation errors",
            403: get_exception_definition(403),
            404: get_exception_definition(404),
        },        
        tags=['upload_db']
    )
    def put(self, request, document_id, format=None):
        """
        Launches uploading file to DBMS with selected_parameters.

         - Authorization: Token <token>
         - Access scope: users
        """
        document = self.get_object(request, document_id)
        request_serializer = serializers.DocumentUpdateSerializer(document, data=request.data)
        if request_serializer.is_valid():
            document = request_serializer.save()
            self.launch_task(document)
            logger.info(f'[# Document {document_id}] File uploading to DBMS is started by {request.user.username}')
            response_serializer = serializers.DocumentStatusSerializer(document)
            return Response(response_serializer.data, status=200)
        else:
            return Response(request_serializer.errors, status=400)

    @swagger_auto_schema(
        request_body=None,
        responses={
            200: "{'deleted': 'true'}",
            400: "Validation errors",
            403: get_exception_definition(403),
            404: get_exception_definition(404),
        },        
        tags=['upload_db']
    )
    def delete(self, request, document_id, format=None):
        """
        Deletes file from server.

         - Authorization: Token <token>
         - Access scope: users
        """
        document = self.get_object(request, document_id)
        document.document.delete()
        logger.info(f'[# Document {document_id}]File #{document_id} deleted by user {request.user.username}')
        return JsonResponse({"deleted": True}, status=200)


class UtilsDecodeDBString(views.APIView):
    permission_classes = (permissions.AllowAny,)

    model = Document

    @swagger_auto_schema(
        request_body=serializers.DecodeDBConnectionRequestSerializer,
        responses={
            200: serializers.DecodeDBConnectionResponseSerializer,
            403: get_exception_definition(403),
            404: get_exception_definition(404),
        },        
        tags=['utils']
    )
    def post(self, request, format=None):
        """
        Decodes connection string.

         - Authorization: none
         - Access scope: anyone
        """
        request_serializer = serializers.DecodeDBConnectionRequestSerializer(data=request.data)
        if request_serializer.is_valid():
            response = self.model.decode_db_connection(request_serializer.data['db_connection'])
            response_serializer = serializers.DecodeDBConnectionResponseSerializer(response)
            return JsonResponse(response_serializer.data, status=200)
        else:
            return Response(request_serializer.errors, status=400)


class UtilsLoadConnectionsView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication,)

    model = Document

    @swagger_auto_schema(
        request_body=None,
        responses={
            200: serializers.ListDBConnectionsResponseSerializer,
        },        
        tags=['utils']
    )
    def get(self, request, format=None):
        """
        Returns list of connections, that are available to user.

         - Authorization: Token <token>
         - Access scope: users
        """
        db_connections = list(
            Document.objects.filter(
                user=request.user,
                status=2
            ).values_list(
                'db_connection',
                flat=True
            ).distinct()
        ) + ['new-pg', 'new-or']
        response = {
            'connections': [
                self.model.name_db_connection(conn) for conn in db_connections
            ]
        }
        response_serializer = serializers.ListDBConnectionsResponseSerializer(response)
        return JsonResponse(response_serializer.data, status=200)
