from django.urls import path
from .views import MainPageView, StudentsListView,   TeachersListView, CoursesListView

app_name = 'main'

urlpatterns = [
    path('', MainPageView.as_view(), name='main'),
    path('students', StudentsListView.as_view(), name='students_list'),
    path('teachers/', TeachersListView.as_view(), name='teachers_list'),
    path('courses/', CoursesListView.as_view(), name='courses_list'),
]
