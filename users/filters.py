from django.shortcuts import redirect
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.decorators import method_decorator
from .models import UsersModel

class AdminRequired(UserPassesTestMixin):

    def test_func(self):
        user = UsersModel.objects.get(id=self.request.user.id)
        return user.role == '2'

    def handle_no_permission(self):
        return redirect('main:main')  