from django.urls import path
from .views import StudentUpdateView, CreateStudentView, CreateEnrollmentView

app_name = 'students'

urlpatterns = [
    path('student/<int:pk>', StudentUpdateView.as_view(), name='student_update'),
    path('create_student', CreateStudentView.as_view(), name='create_student'),
    path('enrollments/create/', CreateEnrollmentView.as_view(), name='create_enrollment'),
    path('enrollments/create/<int:course_id>/', CreateEnrollmentView.as_view(), name='create_enrollment_from_course'),
    path('enrollments/create/<int:student_id>/', CreateEnrollmentView.as_view(), name='create_enrollment_from_student'),
]
