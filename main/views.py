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
        # Extract and validate date only once
        t = request.GET.get('date', '')
        self.today = date.today()

        if t:
            try:
                parsed_date = datetime.strptime(t, '%Y-%m-%d').date()
                # Don't allow future dates unless admin
                if request.user.role != '1' and parsed_date > self.today:
                    parsed_date = self.today
                self.today = parsed_date
            except ValueError:
                return redirect('main:main')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = self.today

        # Dates for navigation
        context['prev_date'] = today - timedelta(days=1)
        context['next_date'] = date.today() if today == date.today() else today + timedelta(days=1)

        # Query: all sessions marked today
        marked_sessions = SessionsModel.objects.filter(date=today)

        # Courses scheduled today (based on weekday) and not yet marked
        sessions_today = CourseModel.objects.filter(
            status=True,
            weekdays__contains=str(today.weekday())
        ).exclude(
            id__in=marked_sessions.values_list('course', flat=True)
        )

        # Filter by teacher if not admin
        if self.request.user.role == '1':
            teacher_id = self.request.user.id
            courses = CourseModel.objects.filter(status=True, teacher_id=teacher_id).order_by('id')
            sessions_today = sessions_today.filter(teacher_id=teacher_id)
            marked_sessions = marked_sessions.filter(course__teacher_id=teacher_id)
        else:
            courses = CourseModel.objects.filter(status=True).order_by('id')

        # Get today's conducted sessions and prefetch attendance
        conducted_sessions = SessionsModel.objects.filter(
            status=True, date=today
        ).prefetch_related('attendancemodel_set', 'course')

        # Prepare attendance entries for students not marked yet
        attendance_bulk_create = []
        for session in conducted_sessions:
            existing_student_ids = AttendanceModel.objects.filter(session=session).values_list('enrollment__student_id', flat=True)
            fresh_enrolled = Enrollment.objects.filter(
                course=session.course, status=True
            ).exclude(student_id__in=existing_student_ids)

            for enroll in fresh_enrolled:
                attendance_bulk_create.append(
                    AttendanceModel(enrollment=enroll, session=session)
                )

        # Bulk create attendance records
        if attendance_bulk_create:
            AttendanceModel.objects.bulk_create(attendance_bulk_create)

        # Re-fetch conducted_sessions if necessary
        conducted_sessions = SessionsModel.objects.filter(
            status=True, date=today
        ).prefetch_related('attendancemodel_set')

        # Final context
        context.update({
            'today': date.today().strftime("%Y-%m-%d"),
            'filter_date': today.strftime("%Y-%m-%d"),
            'conducted_sessions': conducted_sessions,
            'sessions_today': sessions_today.order_by("lesson_time"),
            'marked_sessions': marked_sessions.order_by('course__lesson_time'),
            'cancel_cause_form': CancelCauseForm,
        })
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
        context['active_students_count'] = StudentModel.objects.filter(enrollment__status=True, enrollment__trial_lesson=False).distinct().count()
        return context

    def get_queryset(self):
        text = self.request.GET.get('text')
        teacher = self.request.GET.get('teacher')
        ordering = self.request.GET.get('order_by')
        enrollment_month = self.request.GET.get('enrollment_month')

        queryset = super().get_queryset()

        if enrollment_month:
            year, month = map(int, enrollment_month.split('-'))
            queryset = queryset.filter(enrollment__enrolled_at__year=year, enrollment__enrolled_at__month=month).distinct().order_by('enrollment__enrolled_at')

        if text:
            words= text.split()
            queryset = queryset.filter(Q(last_name__in=words) | Q(first_name__in=words) | Q(last_name__icontains=text) | Q(phone_number__icontains=text) | Q(additional_number__icontains=text))
        if teacher:
            queryset = queryset.filter(courses__teacher=teacher).distinct()

        if ordering:
            if ordering == "1":
                queryset = queryset.order_by('first_name', 'last_name')
            elif ordering == "2":
                queryset = queryset.filter(enrollment__payment_due__lt=datetime.today().date(), courses__isnull=False, enrollment__trial_lesson=False, enrollment__status=True).order_by('first_name', 'last_name').distinct()
            elif ordering == "3":
                thirty_days_ago = datetime.now() - timedelta(days=30)
                queryset = queryset.filter(enrollment_date__gte=thirty_days_ago).order_by('-id')
            elif ordering == '4':
                thirty_days_ago = datetime.now() - timedelta(days=60)
                queryset = queryset.filter(enrollment_date__gte=thirty_days_ago).order_by('-id')
            elif ordering == "5":
                queryset = queryset.filter(Q(courses__isnull=True) | Q(enrollment__status=False)).exclude(enrollment__status=True).order_by('first_name', 'last_name').distinct()
            elif ordering == "8":
                queryset = queryset.filter(Q(courses__isnull=False) | Q(enrollment__status=True)).exclude(enrollment__status=False).order_by('first_name', 'last_name').distinct()
            elif ordering == "6":
                queryset = queryset.order_by('-id')
            elif ordering == "7":
                queryset = queryset.order_by('id')

        return queryset
    
class TeachersListView(AdminRequired, ListView):
    queryset = UsersModel.objects.all().filter(role='1', is_active=True).order_by('first_name', 'last_name').prefetch_related('coursemodel_set')
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
        return context


class CoursesListView(AdminRequired, ListView):
    queryset = CourseModel.objects.all().exclude(subject__show_separately=True)
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
        if subject:
            queryset = CourseModel.objects.filter(subject=subject)

        if days:
            if days == "1":
                queryset = queryset.filter(weekdays__contains='0,2,4')
            elif days == "2":
                queryset = queryset.filter(weekdays__contains='1,3,5')
            elif days == "3":
                queryset = queryset.exclude(Q(weekdays__contains="0,2,4") | Q(weekdays__contains="1,3,5"))
        if teacher:
            queryset = queryset.filter(teacher_id=teacher)

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
    