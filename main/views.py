from django.template.defaultfilters import first
from django.views.generic import TemplateView, ListView
from datetime import date, datetime, timedelta
from django.db.models import Q, Prefetch
from django.shortcuts import redirect
from django.urls import reverse
from urllib.parse import urlencode

from students.forms import StudentInfoForm, EnrollmentForm
from students.models import StudentModel, Enrollment
from users.filters import AdminRequired
from courses.models import SessionsModel, SubjectModel
from courses.forms import DaysMultiselectForm, CancelCauseForm
from courses.models import CourseModel, UsersModel
from .forms import CoursesListFilterForm, StudentsListFilterForm, TeachersListFilterForm, EnrollmentsListFilterForm
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
                fresh_enrolled = Enrollment.objects.filter(course=session.course, status=True, hold=False).exclude(student_id__in=attendance.values_list('enrollment__student_id', flat=True))
                for enroll in fresh_enrolled:
                    if not AttendanceModel.objects.filter(session=session, enrollment__student_id=enroll.student.id).exists():
                        AttendanceModel.objects.create(enrollment=enroll, session=session)

        conducted_sessions = SessionsModel.objects.filter(status=True, date=today).prefetch_related(Prefetch('attendancemodel_set', queryset=AttendanceModel.objects.filter(enrollment__hold=False)))

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

    def get(self, request, *args, **kwargs):
        # If no filters provided, but session has saved filters — redirect with them
        if not request.GET and request.session.get("students_filters"):
            return redirect(f"{reverse('main:students_list')}?{urlencode(request.session['students_filters'])}")

        # If GET has filters, store them
        if request.GET:
            request.session["students_filters"] = request.GET.dict()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.request.GET.copy()
        context['filter_form'] = StudentsListFilterForm(initial=data)
        context['create_student_form'] = StudentInfoForm
        context['queryset_length'] = self.get_queryset().count()
        context['overall_count'] = StudentModel.objects.all().count()
        context['all_students_names'] = StudentModel.objects.all().values_list('first_name', 'last_name')
        context['active_count'] = StudentModel.objects.filter(enrollment__status=True, enrollment__trial_lesson=False, enrollment__payment_due__isnull=False).distinct().count()
        return context

    def get_queryset(self):
        text = self.request.GET.get('text')
        teacher = self.request.GET.get('teacher')
        ordering = self.request.GET.get('order_by')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        queryset = super().get_queryset()

        if date_from:
            queryset = queryset.filter(enrollment_date__gte=date_from)

        if date_to:
            queryset = queryset.filter(enrollment_date__lte=date_to)
        elif not date_to and date_from:
            queryset = queryset.filter(enrollment_date__lte=date_from)

        # Apply search text filter
        if text:
            words = text.split()
            queryset = queryset.filter(
                Q(last_name__in=words) |
                Q(first_name__in=words) |
                Q(last_name__icontains=text) |
                Q(first_name__icontains=text) |
                Q(phone_number__icontains=text) |
                Q(additional_number__icontains=text)
            )

        # Filter by teacher
        if teacher:
            queryset = queryset.filter(courses__teacher=teacher)

        # Apply ordering
        if ordering == "1":
            queryset = queryset.order_by('first_name', 'last_name')
        elif ordering == "2":
            queryset = queryset.order_by('-first_name', '-last_name')
        elif ordering == "3":
            queryset = queryset.order_by('-id')
        elif ordering == "4":
            queryset = queryset.order_by('id')

        return queryset.distinct()


class TeachersListView(AdminRequired, ListView):
    queryset = UsersModel.objects.all().filter(role='1', is_active=True).order_by('first_name', 'last_name').prefetch_related('coursemodel_set')
    template_name = 'teachers_list.html'
    context_object_name = 'teachers'
    ordering = ['first_name', 'last_name']
    paginate_by = 30

    def get(self, request, *args, **kwargs):
        # If no filters provided, but session has saved filters — redirect with them
        if not request.GET and request.session.get("teachers_filters"):
            return redirect(f"{reverse('main:teachers_list')}?{urlencode(request.session['teachers_filters'])}")

        # If GET has filters, store them
        if request.GET:
            request.session["teachers_filters"] = request.GET.dict()

        return super().get(request, *args, **kwargs)

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
    queryset = CourseModel.objects.all().exclude(Q(subject__show_separately=True) | Q(archived=True))
    template_name = "courses_list.html"
    context_object_name = 'courses'
    paginate_by = 30
    ordering = ['teacher', 'lesson_time']

    def get(self, request, *args, **kwargs):
        # If no filters provided, but session has saved filters — redirect with them
        # If GET has filters, store them
        if request.GET:
            request.session["courses_filters"] = request.GET.dict()

        if not request.GET and request.session.get("courses_filters"):
            return redirect(f"{reverse('main:courses_list')}?{urlencode(request.session['courses_filters'])}")

        request.session["courses_filters"] = request.GET.dict()


        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        course_name = self.request.GET.get('course_name')
        days =  self.request.GET.get('weekdays')
        teacher = self.request.GET.get('teacher')
        subject = self.request.GET.get('subject')
        sort_by = self.request.GET.get('sort_by')

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

        if sort_by:
            if sort_by == "1":
                queryset = queryset.order_by("lesson_time")
            if sort_by == "6":
                queryset = queryset.order_by("-lesson_time")
            elif sort_by == "2":
                queryset = queryset.order_by("subject__name")
            elif sort_by == "3":
                days15 = datetime.today() - timedelta(days=15)
                queryset = queryset.filter(created_at__gte=days15)
            elif sort_by == "4":
                days30 = datetime.today() - timedelta(days=30)
                queryset = queryset.filter(created_at__gte=days30)
            elif sort_by == "5":
                queryset = queryset.order_by("teacher__first_name", "teacher__last_name", "teacher__username")

        return queryset.exclude(archived=True)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teachers"] = UsersModel.objects.all().filter(role='1')
        context['filter_form'] = CoursesListFilterForm(self.request.GET)
        days = self.request.GET.getlist('weekdays')
        context["days_form"] = DaysMultiselectForm(initial={'weekdays': days})
        context['subjects'] = SubjectModel.objects.all()
        return context


class EnrollmentsListView(AdminRequired, ListView):
    model = Enrollment
    template_name = 'enrollments_list.html'
    context_object_name = 'enrollments'
    ordering = ['-id']
    paginate_by = 30

    def get(self, request, *args, **kwargs):
        # If no filters provided, but session has saved filters — redirect with them
        if not request.GET and request.session.get("enrollments_filters"):
            return redirect(f"{reverse('main:enrollments_list')}?{urlencode(request.session['enrollments_filters'])}")

        # If GET has filters, store them
        if request.GET:
            request.session["enrollments_filters"] = request.GET.dict()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.request.GET.copy()
        context['filter_form'] = EnrollmentsListFilterForm(initial=data)
        context['queryset_length'] = self.get_queryset().count()
        context['overall_count'] = Enrollment.objects.all().count()
        context['active_count'] = Enrollment.objects.filter(status=True, trial_lesson=False, payment_due__isnull=False).distinct().count()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        student = self.request.GET.get('student', None)
        course = self.request.GET.get('course', None)
        enrolled_by = self.request.GET.get('enrolled_by', None)
        date_from = self.request.GET.get('date_from', None)
        date_to = self.request.GET.get('date_to', None)
        display_only = self.request.GET.get('display_only', None)
        order_by = self.request.GET.get('order_by', None)

        if student:
            queryset = queryset.filter(student=student)

        if course:
            queryset = queryset.filter(course=course)

        if enrolled_by:
            queryset = queryset.filter(enrolled_by=enrolled_by)

        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)

        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        elif not date_to and date_from:
            queryset = queryset.filter(created_at__lte=date_from)


        if display_only:
            if display_only == '1':
                queryset = queryset.filter(trial_lesson=True, status=True)
            elif display_only == '2':
                queryset = queryset.filter(status=False)
            elif display_only == '3':
                queryset = queryset.filter(Q(payment_due__lt=datetime.today().date()) | Q(payment_due__isnull=True), status=True)
            elif display_only == '4':
                queryset = queryset.filter(payment_due__isnull=False).exclude(Q(trial_lesson=True) | Q(status=False))
            elif display_only == '5':
                if date_from:
                    queryset = queryset.filter(Q(transferred_from__isnull=True) | Q(transferred_from__created_at__gte=date_from), payment_due__isnull=False).exclude(Q(trial_lesson=True) | Q(status=False))
            elif display_only == '6':
                queryset = queryset.filter(hold=True)

        if order_by:
            if order_by == '1':
                queryset = queryset.order_by('student__first_name', 'student__last_name')
            elif order_by == '2':
                queryset = queryset.order_by('course__id', 'student__first_name', 'student__last_name')
            elif order_by == '3':
                queryset = queryset.order_by('course__lesson_time', 'course__id', 'student__first_name', 'student__last_name')
            elif order_by == '4':
                queryset = queryset.order_by('-created_at')
            elif order_by == '5':
                queryset = queryset.order_by('-enrolled_at')

        return queryset