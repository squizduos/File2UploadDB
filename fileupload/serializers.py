import os

from rest_framework import serializers

from .models import Document, ACCEPTED_EXTENSIONS

import logging
logger = logging.getLogger('admin_log')


class DocumentUploadRequestSerializer(serializers.ModelSerializer):
    def __init__(self,  *args, original_filename="example.csv", user=None, **kwargs):
        super(DocumentUploadRequestSerializer, self).__init__(*args, **kwargs)
        self.original_filename = original_filename
        self.user = user

    def validate(self, data):
        """
        Check file extension.
        """
        filename, extension = os.path.splitext(data['document'].name)
        if not extension[1:].upper() in ACCEPTED_EXTENSIONS:
            extensions = ", ".join([ex for ex in ACCEPTED_EXTENSIONS])
            raise serializers.ValidationError(f"Can upload only files in next formats: {extensions}")
        return data

    class Meta:
        model = Document
        fields = ['document', ]

    def create(self, validated_data):
        validated_data.update(
            original_filename=self.original_filename,
            user=self.user
        )
        model = self.Meta.model(**validated_data)
        model.save()
        return model


class DocumentUploadResponseSerializer(serializers.ModelSerializer):
    def get_file_id(self, obj):
        return obj.id

    def get_file_storage(self, obj):
        return obj.file_storage

    def get_file_path(self, obj):
        return obj.document.path

    def get_file_name(self, obj):
        return os.path.basename(obj.document.name)            

    def get_file_type(self, obj):
        if obj.get_file_extension() not in ACCEPTED_EXTENSIONS:
            return 'CSV'
        return obj.get_file_extension()

    def get_file_header_line(self, obj):
        return 'not applicable' if obj.get_file_extension() in ["DTA"] else ""
    
    def get_file_separator(self, obj):
        return 'not applicable' if obj.get_file_extension() in ["XLS", "XLSX", "DTA"] else ""

    def get_table_name(self, obj):
        return obj.get_filename_witout_extension()
    
    def get_enabled_for_editing(self, obj):
        enabled = obj.get_enabled_for_editing_by_default()
        if obj.get_file_extension() in ["CSV", "XLS", "XLSX"]:
            enabled.append("file_header_line")
        if obj.get_file_extension() in ["CSV"]:
            enabled.append("file_separator")
        return enabled

    enabled_for_editing = serializers.SerializerMethodField()
    file_id = serializers.SerializerMethodField()
    file_storage = serializers.SerializerMethodField()
    file_path = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    file_header_line = serializers.SerializerMethodField()
    file_separator = serializers.SerializerMethodField()
    table_name = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'file_id',
            'file_storage',
            'file_path',
            'file_name',
            'file_type',
            'file_header_line',
            'file_separator',
            'table_name',
            'enabled_for_editing'
        ]


class DocumentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'file_type',
            'file_header_line',
            'file_separator',
            'table_name',
            'db_type',
            'db_username',
            'db_password',
            'db_host',
            'db_port',
            'db_sid',
            'db_name'
        ]


class DocumentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['status', 'error', 'percent']
        read_only_fields = ['status', 'error', 'percent']


class DocumentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id']
        read_only_fields = ['id']


class DecodeDBConnectionRequestSerializer(serializers.Serializer):
    db_connection = serializers.CharField()


class DecodeDBConnectionResponseSerializer(serializers.Serializer):
    db_type = serializers.CharField(max_length=100)
    db_username = serializers.CharField(max_length=100)
    db_password = serializers.CharField(max_length=100)
    db_host = serializers.CharField(max_length=100)
    db_port = serializers.CharField(max_length=100)
    db_sid = serializers.CharField(max_length=100)
    db_name = serializers.CharField(max_length=100)


class DBConnectionsResponseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    value = serializers.CharField(max_length=100)


class ListDBConnectionsResponseSerializer(serializers.Serializer):
    connections = DBConnectionsResponseSerializer(many=True)
