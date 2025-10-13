from django.urls import path
from .views import StudentUpdateView, CreateStudentView, CreateEnrollmentView, UpdateEnrollmentView, \
    GroupReEnrollmentView, DeactivateEnrollmentView, UpdateEnrollmentNote, ReEnrollStudentView, autocomplete_students, \
    ArchiveStudent, UnArchiveStudent, ConvertEnrollmentToLead, AbsentStudentsList, UpdateEnrollmentAbsentNote

# API
from .views import StudentListView
app_name = 'students'

urlpatterns = [
    path('student/<int:pk>', StudentUpdateView.as_view(), name='student_update'),
    path('create_student', CreateStudentView.as_view(), name='create_student'),
    path('enrollment/<int:pk>/', UpdateEnrollmentView.as_view(), name='update_enrollment'),
    path('enrollment/create/', CreateEnrollmentView.as_view(), name='create_enrollment'),
    path('enrollment/delete/<int:enrollment_id>', DeactivateEnrollmentView.as_view(), name='delete_enrollment'),
    path('enrollment/create/course/<int:course_id>/', CreateEnrollmentView.as_view(), name='create_enrollment_from_course'),
    path('enrollment/create/student/<int:student_id>/', CreateEnrollmentView.as_view(), name='create_enrollment_from_student'),
    path('enrollment/update-note/<int:pk>/', UpdateEnrollmentNote.as_view(), name='update_enrollment_note'),
    path('enrollment/update-absent-note/<int:pk>/', UpdateEnrollmentAbsentNote.as_view(), name='update_enrollment_absent_note'),
    path('enrollment/re-enroll/<int:pk>', ReEnrollStudentView.as_view(), name='re_enroll'),
    path('enrollment/group-re-enroll/<int:group_id>', GroupReEnrollmentView.as_view(), name="group-re-enroll"),
    path('autocomplete-students/', autocomplete_students, name='autocomplete-students'),
    path('student/<int:pk>/archive', ArchiveStudent.as_view(), name='archive_student'),
    path('student/<int:pk>/unarchive', UnArchiveStudent.as_view(), name='unarchive_student'),
    path('student/<int:enrollment_id>/convert-lead', ConvertEnrollmentToLead.as_view(), name='convert_enrollment_to_lead'),
    path('student/absent-list', AbsentStudentsList.as_view(), name='absent_list'),

    # Api

    path('api/students-list/', StudentListView.as_view(), name='api-student-list'),
]
