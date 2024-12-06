from django.views.generic import TemplateView, ListView
from datetime import date
from courses.models import CourseModel, SessionsModel
from students.models import StudentModel
from django.core.paginator import Paginator

from users.filters import AdminRequired
from courses.models import SessionsModel, WEEKDAY_CHOICES, SubjectModel
from users.models import UsersModel

class MainPageView(TemplateView):
    template_name = 'main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        sessions_today = SessionsModel.objects.filter(date=today)
        courses = CourseModel.objects.all().filter(is_started=True, finished=False).order_by('id')

        if self.request.user.role == '1':
            courses = courses.filter(teacher__id=self.request.user.id)
            sessions_today = sessions_today.filter(course__teacher__id=self.request.user.id)


        paginator = Paginator(courses, 10)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)


        context["page_obj"] = page_obj
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
    paginate_by = 10


    def get_queryset(self):
        course_name = self.request.GET.get('course_name')
        day = self.request.GET.get('day')
        teacher = self.request.GET.get('teacher')
        subject = self.request.GET.get('subject')

        queryset = super().get_queryset()
        
        if course_name:
            queryset = queryset.filter(course_name__icontains=course_name)
        if day:
            queryset = queryset.filter(weekdays__contains=day)
        if teacher:
            queryset = queryset.filter(teacher_id=teacher)
        if subject:
            queryset = queryset.filter(subject_id=subject)


        return queryset
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teachers"] = UsersModel.objects.all().filter(role='1')
        context["days"] = WEEKDAY_CHOICES
        context['subjects'] = SubjectModel.objects.all()
        return context
    