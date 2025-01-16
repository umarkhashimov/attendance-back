from django.views.generic import TemplateView, ListView
from datetime import date
from courses.models import CourseModel, SessionsModel
from students.models import StudentModel
from django.core.paginator import Paginator
from django.db.models import Q

from users.filters import AdminRequired
from courses.models import SessionsModel, WEEKDAY_CHOICES, SubjectModel
from courses.forms import DaysMultiselectForm
from users.models import UsersModel

class MainPageView(TemplateView):
    template_name = 'main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()

        # Get sessions already marked today
        marked_sessions = SessionsModel.objects.filter(date=today)

        # Get courses scheduled for today based on weekdays
        sessions_today = CourseModel.objects.filter(status=True, weekdays__contains=str(today.weekday()))

        # Exclude courses that already have marked sessions
        marked_course_ids = marked_sessions.values_list('course', flat=True)
        sessions_today = sessions_today.exclude(id__in=marked_course_ids)

        # Get all marked courses
        courses = CourseModel.objects.all().filter(status=True).order_by('id')

        if self.request.user.role == '1':
            courses = courses.filter(teacher__id=self.request.user.id)
            sessions_today = sessions_today.filter(teacher__id=self.request.user.id)
            marked_sessions = marked_sessions.filter(course__in=courses)
            print(marked_sessions.values_list('course_id', flat=True))


        paginator = Paginator(courses, 20)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context["page_obj"] = page_obj
        context['sessions_today'] = sessions_today
        context['marked_sessions'] = marked_sessions
        return context
    

class StudentsListView(AdminRequired, ListView):
    model = StudentModel
    template_name = 'students_list.html'
    context_object_name = 'students'
    paginate_by = 20
    
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
        days =  self.request.GET.getlist('weekdays')
        teacher = self.request.GET.get('teacher')
        subject = self.request.GET.get('subject')

        queryset = super().get_queryset()
        
        if course_name:
            queryset = queryset.filter(course_name__icontains=course_name)
        if days:
            queryset = queryset.filter(weekdays__contains=','.join(days))
        if teacher:
            queryset = queryset.filter(teacher_id=teacher)
        if subject:
            queryset = queryset.filter(subject_id=subject)

        return queryset
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teachers"] = UsersModel.objects.all().filter(role='1')
        days = self.request.GET.getlist('weekdays')
        context["days_form"] = DaysMultiselectForm(initial={'weekdays': days})
        context['subjects'] = SubjectModel.objects.all()
        return context
    