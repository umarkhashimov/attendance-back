from django.urls import path
from .views import MainPageView, CourseDetailView

app_name = 'main'

urlpatterns = [
    path('', MainPageView.as_view(), name='main'),
    path('course/<int:pk>', CourseDetailView.as_view(), name='course_detail'),
]