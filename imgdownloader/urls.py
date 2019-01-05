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
from django.views.decorators.csrf import csrf_exempt

from rest_framework import permissions

from authentitcation import views as auth_api_views, web as auth_web_views

from fileupload import views as upload_api_views, web as upload_web_views

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="UploadToDB",
      default_version='v1',
      description="Simple project to upload CSV, XLS(X) and DAT files to powerful server",
      terms_of_service="https://restapi.img-test.squizduos.ru/",
      contact=openapi.Contact(email="squizduos@gmail.com"),
      license=openapi.License(name="Commerical License"),
      url="/api/",
   ),
   url="https://restapi.img-test.squizduos.ru",
   public=True,
   permission_classes=(permissions.AllowAny, permissions.IsAdminUser, permissions.IsAuthenticated),
)

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', upload_web_views.MainPageView.as_view(), name='main-page'),

    path('web/', include([
        path('auth/', include([
            path('login/', auth_web_views.LoginView.as_view(), name="web-login-view"),
            path('logout/', auth_web_views.LogoutView.as_view(), name="web-logout-view"),
            path('register/', auth_web_views.AdminRegisterView.as_view(), name="web-register-view"),
            path(
                'set_password/<str:login_hash>/',
                auth_web_views.RegisterView.as_view(),
                name="web-set-password-view"
            ),
        ])),
        path('dashboard/', upload_web_views.DashboardView.as_view(), name='web-dashboard-view'),
        path('dashboard/admin/', upload_web_views.AdminDashboardView.as_view(), name='web-admin-dashboard-view'),
    ])),

    path('api/', include([
        path('auth/', include([
            path('login/', csrf_exempt(auth_api_views.LoginAPIView.as_view()), name='api-rest-login'),
            path('logout/', csrf_exempt(auth_api_views.LogoutAPIView.as_view()), name='api-rest-logout'),
            path('register/', auth_api_views.RegistrationByAdminView.as_view(), name='api-register'),
            path('set_password/', auth_api_views.RegistrationView.as_view(), name='api-set-password'),
        ])),
        path('upload/', include([
            path('', upload_api_views.DocumentUploadAPIView.as_view(), name='api-upload'),
            path('<document_id>/', upload_api_views.DocumentAPIView.as_view(), name='api-upload-with-id'),
        ])),
        path('utils/', include([
            path("decode_db_connection/", upload_api_views.UtilsDecodeDBString.as_view(), name="api-utils-decodeconn"),
            path("load_connections/", upload_api_views.UtilsLoadConnectionsView.as_view(), name="api-utils-loadconns"),
        ])),
    ])),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
