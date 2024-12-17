from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse

from .filters import AdminRequired
from .models import UsersModel
from .forms import LoginForm, TeacherUpdateForm

class LoginPageView(LoginView):
    form_class = LoginForm
    template_name = 'auth/login.html'
    redirect_authenticated_user = True

class ProfileView(TemplateView):
    template_name = 'auth/profile.html'

class TeacherUpdateView(AdminRequired, UpdateView):
    model = UsersModel
    template_name = 'teacher_update.html'
    form_class = TeacherUpdateForm

    def get_success_url(self):
        return reverse('main:teachers_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.get_object()
        context['teacher'] = teacher
        return context
