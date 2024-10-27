from django.urls import path
from .views import LoginPageView

app_name = 'users'

urlpatterns = [
    path('login/', LoginPageView.as_view(), name='login'),
]