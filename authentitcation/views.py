import logging

from drf_yasg.utils import swagger_auto_schema
from rest_auth import serializers as rest_auth_serializers
from rest_auth import views as rest_auth_views
from rest_framework import authentication, permissions
from rest_framework import views
from rest_framework.response import Response

from . import serializers
from .models import User
from .tasks import send_registration_email

logger = logging.getLogger('admin_log')


class LoginAPIView(rest_auth_views.LoginView):
    @swagger_auto_schema(
        request_body=serializers.UserLoginRequestSerializer,
        responses={
            200: rest_auth_serializers.TokenSerializer,
            400: "Validation and login errors",
            500: "Server errors"
        },
        security=[],
        tags=['auth']
    )
    def post(self, request, *args, **kwargs):
        """
        Login user.

         - Authorization: none
         - Access scope: anyone
        """
        response = super(LoginAPIView, self).post(request, *args, **kwargs)
        if response.status_code == 200:
            logger.info(f'[# System] User {request.data["username"]} successfully logged in')
        elif "username" in request.data:
            logger.info(f'[# System] User {request.data["username"]} trying to log in, incorrect username or password')
        else:
            logger.info(f'[# System] Some user failed to log in; incorrect login request')
        return response


class LogoutAPIView(rest_auth_views.LogoutView):
    @swagger_auto_schema(
        operation_description="""
        Calls Django logout method and delete the Token object assigned to the current User object.
        WARNING: method works only while ACCOUNT_LOGOUT_ON_GET option enabled in settings.
        By default, this option is disabled.

         - Authorization: Token, Session
         - Access scope: users
        """,
        responses={
            200: '{"detail": "Successfully logged out."}',
            400: "Validation and logout errors",
            500: "Server errors"
        },
        tags=['auth']
    )
    def get(self, request, *args, **kwargs):
        response = super(LogoutAPIView, self).get(request, *args, **kwargs)
        if response.status_code == 200:
            logger.info(f'[# System] User {request.user.username} successfully logged out')
        else:
            logger.info(f'[# System] Some user failed to log out; incorrect logout request')
        return response

    @swagger_auto_schema(
        responses={
            200: '{"detail": "Successfully logged out."}',
            400: "Validation and logout errors",
            500: "Server errors"
        },
        tags=['auth']
    )
    def post(self, request, *args, **kwargs):
        """
        Calls Django logout method and delete the Token object assigned to the current User object.

         - Authorization: Token, Session
         - Access scope: users
        """
        response = super(LogoutAPIView, self).post(request, *args, **kwargs)
        if response.status_code == 200:
            logger.info(f'[# System] User {request.user.username} successfully logged out')
        else:
            logger.info(f'[# System] Some user failed to log out; incorrect logout request')
        return response


class RegistrationByAdminView(views.APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)

    @swagger_auto_schema(
        request_body=serializers.UserCreateRequestSerializer,
        responses={
            201: serializers.UserRegisterResponseSerializer,
            400: "Validation errors",
            500: "Server errors"
        },
        tags=['auth']
    )
    def post(self, request, format=None):
        """
        Registers new user by site administrator.

         - Authorization: Token <token>
         - Access scope: only admins
        """
        serializer = serializers.UserCreateRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                send_registration_email.delay(user.id)
            except Exception as e:
                logger.info(
                    f'[# System] User {serializer.data} can\'t be registered, error {e}'
                )
                return Response({'non_field_errors': [str(e)]}, status=400)
            logger.info(f'[# System] User {serializer.data.get("username")} is successfully registered')
            return Response({'registered': True}, status=201)
        else:
            logger.info(f'[# System] Incorrect request on AdminRegister API endpoint')
            return Response(serializer.errors, status=400)


class RegistrationView(views.APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        request_body=serializers.UserSetPasswordRequestSerializer,
        responses={
            200: serializers.UserRegisterResponseSerializer,
            400: "Validation errors",
            500: "Server errors"
        },
        security=[],
        tags=['auth']
    )
    def post(self, request, format=None):
        """
        Set password for new user by login_hash.

         - Authorization: not required
         - Access scope: anyone
        """
        serializer = serializers.UserSetPasswordRequestSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            user = User.objects.get(login_hash=serializer.data.get("login_hash"))
            user.set_password(serializer.data.get("password"))
            user.login_hash = ""
            user.save()
            logger.info(f'[# System] User {user.username} password is successfully set')
            return Response({'registered': True}, status=200)
        else:
            logger.info(f'[# System] Incorrect request on Register API endpoint, errors {serializer.errors}')
            return Response(serializer.errors, status=400)
