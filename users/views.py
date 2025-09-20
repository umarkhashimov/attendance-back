import json
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from functools import reduce
from operator import or_
from django.template.defaultfilters import first
from django.views.generic import TemplateView, UpdateView, ListView, View, CreateView
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from datetime import datetime, timedelta
from django.contrib import messages
from .filters import AdminRequired, SuperUserRequired
from .models import UsersModel, LogAdminActionsModel
from .forms import LoginForm, CustomUserCreationForm, TeacherUpdateForm, UserActionsFilterForm, SalaryMonthFilterForm, \
    UserUpdateForm, UserSetPasswordForm, UsersListFilterForm
from courses.models import CourseModel, SessionsModel
from attendance.models import AttendanceModel
from students.models import Enrollment
from payment.models import PaymentModel

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
            queryset = queryset.filter(datetime__lte=end_date + timedelta(days=1))

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


class UsersListView(SuperUserRequired, ListView):
    model = UsersModel
    template_name = 'users/users_list.html'
    context_object_name = 'users'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = UsersListFilterForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        text = self.request.GET.get('text', None)
        status = self.request.GET.get('status', None)
        role = self.request.GET.get('role', None)

        if status:
            queryset = queryset.filter(is_active=status)

        if role:
            queryset = queryset.filter(role=role)

        if text:
            words = text.split()
            conditions = []

            for word in words:
                conditions.append(Q(username__icontains=word))
                conditions.append(Q(first_name__icontains=word))
                conditions.append(Q(last_name__icontains=word))

            query = reduce(or_, conditions)
            queryset = queryset.filter(query)

        return queryset


class UserUpdateView(SuperUserRequired, UpdateView):
    model = UsersModel
    form_class = UserUpdateForm
    template_name = 'users/users_update.html'
    context_object_name = 'obj_user'
    success_url = reverse_lazy('users:users_list')

    def form_valid(self, form):
        # Here we handle the permissions data explicitly before saving
        user = form.save(commit=False)

        # Get the list of selected permissions (from POST data)
        selected_permissions = form.cleaned_data['custom_permissions']

        # Save the selected permissions to the user instance
        user.custom_permissions = selected_permissions
        user.save()
        print(form.cleaned_data)

        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # Pass the request to the form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_form'] = UserSetPasswordForm(user=self.request.user)
        return context


def reset_user_password(request, pk):
    if not request.user.is_superuser:
        raise PermissionError  # or raise PermissionDenied

    user = get_object_or_404(UsersModel, pk=pk)

    if request.method == 'POST':
        form = SetPasswordForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Пароль пользователя '{user.username}' был изменен.")
        else:
            messages.error(request, "Произошла ошибка.")
    return redirect('users:user_update', pk=pk)


class SalaryUsersListView(SuperUserRequired, ListView):
    queryset = UsersModel.objects.all().filter(role='1', is_active=True)
    template_name = 'salary/salary_users_list.html'
    context_object_name = 'users'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = UsersListFilterForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        text = self.request.GET.get('text', None)

        if text:
            words = text.split()
            conditions = []

            for word in words:
                conditions.append(Q(username__icontains=word))
                conditions.append(Q(first_name__icontains=word))
                conditions.append(Q(last_name__icontains=word))

            query = reduce(or_, conditions)
            queryset = queryset.filter(query)

        return queryset


class SalaryCourseDetailView(SuperUserRequired, View):
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
        sessions = SessionsModel.objects.filter(course=course, date__month=date.month, date__year=date.year).order_by(
            'date')

        # Get all enrollments
        enrollments = Enrollment.objects.filter(course=course).order_by('student__first_name',
                                                                        'student__last_name')

        # Get all attendance records and index them for fast lookup
        attendances = AttendanceModel.objects.filter(session__in=sessions, enrollment__in=enrollments)
        attendance_lookup = {
            (att.enrollment_id, att.session_id): att for att in attendances
        }

        # Build attendance data aligned to sessions
        attendance_data = []
        for enrollment in enrollments:
            if any(key == enrollment.id for key, value in attendance_lookup):

                student_attendance = []
                payments = PaymentModel.objects.filter(enrollment=enrollment)

                if enrollment.transferred and enrollment.transferred_from:
                    previous_payments = PaymentModel.objects.filter(enrollment=enrollment.transferred_from)
                    payments = payments.union(previous_payments)

                latest_payment_due = (
                            payments.order_by('-payed_due').values_list(
                                'payed_due', flat=True).first() or None)
                payment_check_date = enrollment.payment_due if enrollment.payment_due and enrollment.status == True else latest_payment_due


                absents = 0 # do not count as payed when exceeds 2

                for session in sessions:
                    att = attendance_lookup.get((enrollment.id, session.id))  # returns None if not found

                    if att and att.status == 0:
                        absents += 1
                    else:
                        absents = 0

                    student_attendance.append({
                        'status': att.status if att else 404,
                        'session': session,
                        'trial_attendance': att.trial_attendance if att else None,
                        'payed': True if payment_check_date and payment_check_date >= session.date and absents < 3 else False,
                    })
                    student_attendance.sort(key=lambda x: x['session'].date, reverse=True)

                price = ((course.session_cost - ((course.session_cost / 100) * enrollment.discount)) / 12)
                attendance_data.append({
                    'price_for_student': price,
                    'enrollment': enrollment,
                    'student': {'id': enrollment.student.id, 'full_name': enrollment.student.full_name},
                    'attendance': student_attendance,
                    'balance': enrollment.balance if enrollment.payment_due else None,
                })



        context.update({
            'course': course,
            'sessions': sessions.order_by('-date'),
            'attendance_data': attendance_data
        })
        return render(request, self.template_name, context)


class CustomUserCreateView(CreateView):
    model = UsersModel
    form_class = CustomUserCreationForm
    template_name = 'users/user_create.html'
    success_url = reverse_lazy('users:users_list')



# API

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from rest_framework_simplejwt.views import generics
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)