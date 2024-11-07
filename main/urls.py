from django.urls import path
from .views import MainPageView, CourseDetailView, RecordAttendanceView, StudentsListView, StudentUpdateView,  TeachersListView, CoursesListView, CourseUpdateView

app_name = 'main'

urlpatterns = [
    path('', MainPageView.as_view(), name='main'),
    path('course_sessions/<int:pk>', CourseDetailView.as_view(), name='course_sessions'),
    path('session/<int:session_id>', RecordAttendanceView.as_view(), name='session_detail'),
    path('students', StudentsListView.as_view(), name='students_list'),
    path('student/<int:pk>', StudentUpdateView.as_view(), name='student_update'),
    path('teachers/', TeachersListView.as_view(), name='teachers_list'),
    path('courses/', CoursesListView.as_view(), name='courses_list'),
    path('course/<int:pk>', CourseUpdateView.as_view(), name='course_update'),

]
