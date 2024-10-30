from django.urls import path
from .views import LoginPageView, ProfileView
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

app_name = 'users'

urlpatterns = [
    path('login/', LoginPageView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('home')), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
]