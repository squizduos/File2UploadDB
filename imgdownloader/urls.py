"""imgdownloader URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.conf import settings
from authentitcation.views import AdminRegisterView, RegisterView, LoginView, LogoutView
from authentitcation import api_views as auth_api_views
from fileupload.views import DashboardView, AdminDashboardView, UploadToServerView, UploadToDBView, UploadedFileView
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="UploadToDB",
      default_version='v1',
      description="Simple project to upload CSV, XLS(X) and DAT files to powerful server",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

from fileupload.views import DashboardView, AdminDashboardView, UploadToServerView, UploadToDBView, UploadedFileView, UtilsDecodeDBString, UtilsLoadConnectionsView

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),


    path('admin/', admin.site.urls),

    path('', DashboardView.as_view(), name='dashboard'),
    path('dashboard/', DashboardView.as_view(), name='dashboard2'),

    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin-dashboard'),

    path('login/', LoginView.as_view(), name="login-view"),
    path('logout/', LogoutView.as_view(), name="login-view"),
    path('signup/admin/register',AdminRegisterView.as_view()),
    path('signup/register/<str:login_hash>', RegisterView.as_view()),

    path('api/',include([
        path('auth/', include([
            path('login/', obtain_jwt_token),
            path('refresh/', refresh_jwt_token),
            path('verify/', verify_jwt_token),
            path('register/', UploadToDBView, name='api-register'),
            path('protected/register', auth_api_views.RegistrationByAdminView, name='api-register'),
        ])),
        path('upload/', UploadToServerView.as_view(), name='api-upload'),
        path('work/', UploadToDBView.as_view(), name="api-start-work"),
        path('work/<file_id>/', UploadedFileView.as_view(), name='api-work-file'),
        path('utils/', include([
            path("decode_db_connection/", UtilsDecodeDBString.as_view(), name="api-utils-decodeconn"),
            path("load_connections/", UtilsLoadConnectionsView.as_view(), name="api-utils-loadconns"),
        ])),
        # path('login/', UploadToDBView.as_view(), name='api-login'),
        # path('logout/', UploadToDBView.as_view(), name='api-login'),
        # path('admin/register', UploadToDBView.as_view(), name='api-login'),
        # path('register/', UploadToDBView.as_view(), name='api-login'),
    ])),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
