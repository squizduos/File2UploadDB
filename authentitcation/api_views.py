from .models import User
from .serializers import RegistrationSerializer, AdminRegistrationSerializer

from django.http import Http404

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser

from .tasks import send_registration_email

from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_STRING, TYPE_ARRAY
from drf_yasg.utils import swagger_auto_schema

class RegistrationByAdminView(mixins.CreateModelMixin, GenericViewSet):
    @swagger_auto_schema(responses={200: Schema(type=TYPE_OBJECT)})
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (IsAdminUser,)
    serializer_class = AdminRegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save(user=self.request.user)
        send_registration_email.delay(user.id)