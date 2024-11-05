from django.urls import path
from .views import MainPageView, CourseDetailView, RecordAttendanceView, StudentsListView, StudentUpdateView

app_name = 'main'

urlpatterns = [
    path('', MainPageView.as_view(), name='main'),
    path('course/<int:pk>', CourseDetailView.as_view(), name='course_detail'),
    path('session/<int:session_id>', RecordAttendanceView.as_view(), name='session_detail'),
    path('students', StudentsListView.as_view(), name='students_list'),
    path('student/<int:pk>', StudentUpdateView.as_view(), name='student_update')
]
