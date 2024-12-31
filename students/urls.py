from django.urls import path
from .views import StudentUpdateView, CreateStudentView, CreateEnrollmentView, UpdateEnrollmentView

app_name = 'students'

urlpatterns = [
    path('student/<int:pk>', StudentUpdateView.as_view(), name='student_update'),
    path('create_student', CreateStudentView.as_view(), name='create_student'),
    path('enrollment/<int:pk>/', UpdateEnrollmentView.as_view(), name='update_enrollment'),
    path('enrollment/create/', CreateEnrollmentView.as_view(), name='create_enrollment'),
    path('enrollment/create/course/<int:course_id>/', CreateEnrollmentView.as_view(), name='create_enrollment_from_course'),
    path('enrollment/create/student/<int:student_id>/', CreateEnrollmentView.as_view(), name='create_enrollment_from_student'),
]
