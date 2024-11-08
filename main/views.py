from django.views.generic import TemplateView, ListView
from datetime import date
from courses.models import CourseModel, SessionsModel
from students.models import StudentModel

from users.filters import AdminRequired
from courses.models import SessionsModel
from users.models import UsersModel

class MainPageView(TemplateView):
    template_name = 'main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        sessions_today = SessionsModel.objects.filter(date=today)
        if self.request.user.role == '1':
            courses = CourseModel.objects.all().filter(teacher__id=self.request.user.id)
            courses_with_today_sessions = CourseModel.objects.filter(teacher__id=self.request.user.id, id__in=sessions_today.values_list('course_id', flat=True)).distinct()
        else:
            courses = CourseModel.objects.all()
            courses_with_today_sessions = CourseModel.objects.filter(id__in=sessions_today.values_list('course_id', flat=True)).distinct()

        context["courses"] = courses
        context['sessions_today'] = courses_with_today_sessions
        return context
    

class StudentsListView(AdminRequired, ListView):
    model = StudentModel
    template_name = 'students_list.html'
    context_object_name = 'students'


    
class TeachersListView(AdminRequired, ListView):
    queryset = UsersModel.objects.all().filter(role='1')
    template_name = 'teachers_list.html'
    context_object_name = 'teachers'
    
class CoursesListView(AdminRequired, ListView):
    queryset = CourseModel.objects.all()
    template_name = "courses_list.html"
    context_object_name = 'courses'