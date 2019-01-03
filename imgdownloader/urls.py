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
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from authentitcation.views import AdminRegisterView, RegisterView, LoginView, LogoutView
from fileupload.views import DashboardView, AdminDashboardView, UploadToServerView, UploadToDBView, UploadedFileView, UtilsDecodeDBString

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', DashboardView.as_view(), name='dashboard'),
    path('dashboard/', DashboardView.as_view(), name='dashboard2'),

    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin-dashboard'),

    path('login/', LoginView.as_view(), name="login-view"),
    path('logout/', LogoutView.as_view(), name="login-view"),
    path('signup/admin/register',AdminRegisterView.as_view()),
    path('signup/register/<str:login_hash>', RegisterView.as_view()),

    path('api/',include([
        path('upload/', UploadToServerView.as_view(), name='api-upload'),
        path('work/', UploadToDBView.as_view(), name="api-start-work"),
        path('work/<file_id>/', UploadedFileView.as_view(), name='api-work-file'),
        path('utils/', include([
            path("decode_db_connection/", UtilsDecodeDBString.as_view(), name="api-utils-decodeconn"),
        ])),
        # path('login/', UploadToDBView.as_view(), name='api-login'),
        # path('logout/', UploadToDBView.as_view(), name='api-login'),
        # path('admin/register', UploadToDBView.as_view(), name='api-login'),
        # path('register/', UploadToDBView.as_view(), name='api-login'),
    ])),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
