from django.urls import path
from .views import CourseUpdateView, CourseDetailView, StartCourseView

app_name = 'courses'

urlpatterns = [
    path('course_sessions/<int:pk>', CourseDetailView.as_view(), name='course_sessions'),
    path('course/<int:pk>', CourseUpdateView.as_view(), name='course_update'),
    path('course_start/<int:pk>', StartCourseView.as_view(), name='course_start'),
]
