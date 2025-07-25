from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.views.generic import TemplateView, UpdateView, ListView, DetailView, View
from django.urls import reverse, reverse_lazy
from datetime import datetime, timedelta
from .filters import AdminRequired, SuperUserRequired
from .models import UsersModel, LogAdminActionsModel
from .forms import LoginForm, TeacherUpdateForm, UserActionsFilterForm, SalaryMonthFilterForm
from courses.models import CourseModel, SessionsModel
from attendance.models import AttendanceModel
from students.models import Enrollment
class LoginPageView(LoginView):
    form_class = LoginForm
    template_name = 'auth/login.html'
    redirect_authenticated_user = True

class ProfileView(TemplateView):
    template_name = 'auth/profile.html'

class TeacherUpdateView(AdminRequired, UpdateView):
    model = UsersModel
    template_name = 'teacher_update.html'
    form_class = TeacherUpdateForm

    def get_success_url(self):
        return reverse('main:teachers_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.get_object()
        context['teacher'] = teacher
        return context

class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'auth/update_password.html'  # Create this template
    success_url = reverse_lazy('users:profile')  # Redirect after success
    success_message = "Пароль успешно обновлен!"

class AdminActionsView(SuperUserRequired, ListView):
    template_name = 'admin_actions.html'
    model = LogAdminActionsModel
    context_object_name = 'actions'
    ordering = ['-id']
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = self.request.GET.copy()
        context['filter_form'] = UserActionsFilterForm(initial=data)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.GET.get('user', None)
        content_type = self.request.GET.get('content_type', None)
        start_date = self.request.GET.get('date_start', None)
        end_date = self.request.GET.get('date_end', None)
        sort_by = self.request.GET.get('sort_by', None)
        action_type = self.request.GET.get('action_type', None)

        if user:
            queryset = queryset.filter(user_id=user)

        if content_type:
            queryset = queryset.filter(content_type=content_type)

        if action_type:
            queryset = queryset.filter(action_number=action_type)

        if start_date:
            queryset = queryset.filter(datetime__gt=start_date)

        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            queryset = queryset.filter(datetime__lte=end_date+timedelta(days=1))

        if sort_by:
            if sort_by == '1':
                queryset = queryset.order_by('-id')
            elif sort_by == '2':
                queryset = queryset.order_by('id')
            elif sort_by == '3':
                queryset = queryset.order_by('user__username')
            elif sort_by == '4':
                queryset = queryset.order_by('action_number')
        else:
            queryset = queryset.order_by('-id')


        return queryset


class UsersListView(ListView):
    model = UsersModel
    template_name = 'users/users_list.html'
    context_object_name = 'users'


class SalaryUsersListView(ListView):
    queryset = UsersModel.objects.all().filter(role='1', is_active=True)
    template_name = 'salary/salary_users_list.html'
    context_object_name = 'users'


class SalaryCourseDetailView(View):
    template_name = 'salary/salary_course_detail.html'

    def get(self, request, course_id):
        course = CourseModel.objects.get(id=course_id)
        month = request.GET.get('month', None)
        date = datetime.today()
        if month and self.request.user.role != '1':
            date = datetime.strptime(month, '%Y-%m').date()


        context = {
            'course': course,
            'filter_form': SalaryMonthFilterForm(initial={'month': date.strftime("%Y-%m")}),
            'month': date.strftime("%Y-%m"),
        }

        # Get the course and its sessions sorted by date
        course = CourseModel.objects.get(id=course_id)
        sessions = SessionsModel.objects.filter(course=course, date__month=date.month, date__year=date.year).order_by('-date')

        # Get all enrollments
        enrollments = Enrollment.objects.filter(course=course, status=True).order_by('student__first_name',
                                                                                     'student__last_name')

        # Get all attendance records and index them for fast lookup
        attendances = AttendanceModel.objects.filter(session__in=sessions, enrollment__in=enrollments)
        attendance_lookup = {
            (att.enrollment_id, att.session_id): att for att in attendances
        }

        # Build attendance data aligned to sessions
        attendance_data = []
        for enrollment in enrollments:
            student_attendance = []
            for session in sessions:
                att = attendance_lookup.get((enrollment.id, session.id))  # returns None if not found
                student_attendance.append({
                    'status': att.status if att else 404,
                    'homework_grade': att.homework_grade if att else None,
                    'participation_grade': att.participation_grade if att else None,
                    'session': session,
                    'trial_attendance': att.trial_attendance if att else None,
                })
            attendance_data.append({
                'student': enrollment.student.full_name,
                'attendance': student_attendance
            })

        context.update({
            'course': course,
            'sessions': sessions,
            'attendance_data': attendance_data
        })
        return render(request, self.template_name, context)