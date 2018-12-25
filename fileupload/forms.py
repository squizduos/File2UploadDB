from django import forms

from authentitcation.models import User
from .models import Document

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document', )

class DocumentUpdateForm(forms.ModelForm):
    class Meta:
        model = Document
        exclude = ('original_filename', 'document', 'user', 'error', 'status', 'uploading_percent')
