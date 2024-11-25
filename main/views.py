from django.views.generic import TemplateView, ListView
from datetime import date
from courses.models import CourseModel, SessionsModel
from students.models import StudentModel

from users.filters import AdminRequired
from courses.models import SessionsModel, WEEKDAY_CHOICES
from users.models import UsersModel

class MainPageView(TemplateView):
    template_name = 'main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        sessions_today = SessionsModel.objects.filter(date=today)
        courses = CourseModel.objects.all()

        if self.request.user.role == '1':
            courses = CourseModel.objects.all().filter(teacher__id=self.request.user.id)
            sessions_today = SessionsModel.objects.filter(date=today, course__teacher__id=self.request.user.id)

        context["courses"] = courses
        context['sessions_today'] = sessions_today
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

    def get_queryset(self):
        course_name = self.request.GET.get('course_name')
        day = self.request.GET.get('day')
        teacher = self.request.GET.get('teacher')

        queryset = super().get_queryset()
        
        if course_name:
            queryset = queryset.filter(course_name__icontains=course_name)
        if day:
            queryset = queryset.filter(weekdays__contains=day)
        if teacher:
            queryset = queryset.filter(teacher_id=teacher)

        return queryset
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teachers"] = UsersModel.objects.all().filter(role='1')
        context["days"] = WEEKDAY_CHOICES
        return context
    