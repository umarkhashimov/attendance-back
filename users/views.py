from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView

from .forms import LoginForm

class LoginPageView(LoginView):
    form_class = LoginForm
    template_name = 'auth/login.html'
    redirect_authenticated_user = True