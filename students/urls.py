from django.urls import path
from .views import StudentUpdateView, CreateStudentView

app_name = 'students'

urlpatterns = [
    path('student/<int:pk>', StudentUpdateView.as_view(), name='student_update'),
    path('create_student', CreateStudentView.as_view(), name='create_student')
]
