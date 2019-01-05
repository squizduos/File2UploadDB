from django.views.generic import View

from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy as reverse

from .utils import file_read_from_tail

import logging
logger = logging.getLogger('admin_log')


class MainPageView(View):
    def get(self, request):
        return redirect('web-dashboard-view')


class DashboardView(LoginRequiredMixin, View):
    login_url = reverse('web-login-view')

    def get(self, request):
        return render(request, 'dashboard.html', context={})


class AdminDashboardView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    login_url = reverse('web-login-view')

    def get(self, request):
        log = file_read_from_tail('log/info.log', 10000)
        return render(request, 'admin-dashboard.html', context={'log': log})
