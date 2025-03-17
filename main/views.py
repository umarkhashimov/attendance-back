from django.template.defaultfilters import first
from django.views.generic import TemplateView, ListView
from datetime import date, datetime, timedelta
from django.db.models import Q
from django.shortcuts import redirect

from students.forms import StudentInfoForm
from students.models import StudentModel, Enrollment
from users.filters import AdminRequired
from courses.models import SessionsModel, SubjectModel
from courses.forms import DaysMultiselectForm, CancelCauseForm, CourseUpdateForm
from courses.models import CourseModel, UsersModel
from .forms import CoursesListFilterForm, StudentsListFilterForm, TeachersListFilterForm
from attendance.models import AttendanceModel
class MainPageView(TemplateView):
    template_name = 'main.html'

    def dispatch(self, request, *args, **kwargs):
        # Condition to redirect

        t = self.request.GET.get('date', '')
        if t:
            try:
                today = datetime.strptime(t, '%Y-%m-%d').date()
            except ValueError:
                return redirect('main:main')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        t = self.request.GET.get('date')
        today = date.today()
        if t and self.request.user.role != '1':
            today = datetime.strptime(t, '%Y-%m-%d').date()
            if today > date.today():
                today = date.today()
        context['prev_date'] = today - timedelta(days=1)
        context['next_date'] = date.today() if today == date.today() else today + timedelta(days=1)

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

        # attendance data test

        conducted_sessions = SessionsModel.objects.filter(status=True, date=today).prefetch_related('attendancemodel_set')

        for session in conducted_sessions:
            if session.date == today:
                attendance = AttendanceModel.objects.all().filter(session=session)
                fresh_enrolled = Enrollment.objects.filter(course=session.course, status=True).exclude(student_id__in=attendance.values_list('enrollment__student_id', flat=True))
                for enroll in fresh_enrolled:
                    if not AttendanceModel.objects.filter(session=session, enrollment__student_id=enroll.student.id).exists():
                        AttendanceModel.objects.create(enrollment=enroll, session=session)

        conducted_sessions = SessionsModel.objects.filter(status=True, date=today).prefetch_related('attendancemodel_set')

        context['today'] = date.today().strftime("%Y-%m-%d")
        context['filter_date'] = today.strftime("%Y-%m-%d")
        context["conducted_sessions"] = conducted_sessions
        context['sessions_today'] = sessions_today.order_by("lesson_time")
        context['marked_sessions'] = marked_sessions.order_by('course__lesson_time')
        context['cancel_cause_form'] = CancelCauseForm
        return context
    

class StudentsListView(AdminRequired, ListView):
    model = StudentModel
    template_name = 'students_list.html'
    context_object_name = 'students'
    paginate_by = 30
    ordering = ['first_name', 'last_name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = StudentsListFilterForm(self.request.GET)
        context['create_student_form'] = StudentInfoForm
        context['queryset_length'] = self.get_queryset().count()
        return context

    def get_queryset(self):
        text = self.request.GET.get('text')
        teacher = self.request.GET.get('teacher')
        ordering = self.request.GET.get('order_by')

        queryset = super().get_queryset()

        if text:
            words= text.split()
            queryset = queryset.filter(Q(last_name__in=words) | Q(first_name__in=words) | Q(last_name__icontains=text) | Q(phone_number__icontains=text) | Q(additional_number__icontains=text))
        if teacher:
            queryset = queryset.filter(courses__teacher=teacher).distinct()
        if ordering:
            if ordering == "1":
                queryset = queryset.order_by('first_name', 'last_name')
            elif ordering == "2":
                queryset = queryset.filter(enrollment__balance__lte=0, courses__isnull=False, enrollment__trial_lesson=False, enrollment__status=True).order_by('first_name', 'last_name').distinct()
            elif ordering == "3":
                thirty_days_ago = datetime.now() - timedelta(days=30)
                queryset = queryset.filter(enrollment_date__gte=thirty_days_ago).order_by('-id')
            elif ordering == '4':
                thirty_days_ago = datetime.now() - timedelta(days=60)
                queryset = queryset.filter(enrollment_date__gte=thirty_days_ago).order_by('-id')
            elif ordering == "5":
                queryset = queryset.filter(Q(courses__isnull=True) | Q(enrollment__status=False)).exclude(enrollment__status=True).order_by('first_name', 'last_name').distinct()
            elif ordering == "6":
                queryset = queryset.order_by('-id')
            elif ordering == "7":
                queryset = queryset.order_by('id')

        return queryset
    
class TeachersListView(AdminRequired, ListView):
    queryset = UsersModel.objects.all().filter(role='1')
    template_name = 'teachers_list.html'
    context_object_name = 'teachers'
    ordering = ['first_name', 'last_name']
    paginate_by = 30

    def get_queryset(self):
        text = self.request.GET.get('text')
        queryset = super().get_queryset()
        if text:
            queryset = queryset.filter(Q(username__icontains=text) | Q(first_name__icontains=text) | Q(last_name__icontains=text))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = TeachersListFilterForm(self.request.GET)

        teachers = self.queryset.order_by('first_name', 'last_name')

        teacher_enrollments = {}

        for teacher in teachers:
            courses = CourseModel.objects.filter(teacher=teacher).distinct().order_by('weekdays',
                                                                                                        'lesson_time')
            if len(courses) > 0:
                teacher_enrollments[teacher] = {
                    course: list(Enrollment.objects.filter(course=course, status=True))
                    for course in courses
                }

        context['teacher_enrollments']=teacher_enrollments
        return context


class CoursesListView(AdminRequired, ListView):
    queryset = CourseModel.objects.all()
    template_name = "courses_list.html"
    context_object_name = 'courses'
    paginate_by = 30
    ordering = ['teacher', 'lesson_time']

    def get_queryset(self):
        course_name = self.request.GET.get('course_name')
        days =  self.request.GET.get('weekdays')
        teacher = self.request.GET.get('teacher')
        subject = self.request.GET.get('subject')

        queryset = super().get_queryset()
        
        if days:
            if days == "1":
                queryset = queryset.filter(weekdays__contains='0,2,4')
            elif days == "2":
                queryset = queryset.filter(weekdays__contains='1,3,5')
            elif days == "3":
                queryset = queryset.exclude(Q(weekdays__contains="0,2,4") | Q(weekdays__contains="1,3,5"))
        if teacher:
            queryset = queryset.filter(teacher_id=teacher)
        if subject:
            queryset = queryset.filter(subject_id=subject)

        return queryset
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teachers"] = UsersModel.objects.all().filter(role='1')
        context['filter_form'] = CoursesListFilterForm(self.request.GET)
        days = self.request.GET.getlist('weekdays')
        context["days_form"] = DaysMultiselectForm(initial={'weekdays': days})
        context['subjects'] = SubjectModel.objects.all()
        context["create_course_form"] = CourseUpdateForm
        return context
    