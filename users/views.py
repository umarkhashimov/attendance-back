from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView, UpdateView, ListView
from django.urls import reverse, reverse_lazy

from .filters import AdminRequired, SuperUserRequired
from .models import UsersModel, LogAdminActionsModel
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

class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'auth/update_password.html'  # Create this template
    success_url = reverse_lazy('users:profile')  # Redirect after success
    success_message = "Пароль успешно обновлен!"

class AdminActionsView(SuperUserRequired, ListView):
    template_name = 'admin_actions.html'
    model = LogAdminActionsModel
    context_object_name = 'actions'
    ordering = ['-id']
    paginate_by = 30