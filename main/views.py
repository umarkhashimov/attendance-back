from django.views.generic import TemplateView, DetailView, ListView, UpdateView
from django.core.exceptions import PermissionDenied
from datetime import date
from django.urls import reverse
from django.utils import timezone
from courses.models import CourseModel, SessionsModel
from students.models import Enrollment, StudentModel
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from users.filters import AdminRequired
from courses.models import SessionsModel
from attendance.models import AttendanceModel, STATUS_CHOICES
from attendance.forms import AttendanceStatusForm
from django.forms import formset_factory

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
    

class CourseDetailView(DetailView):
    model = CourseModel
    template_name = 'course_detail.html'
    context_object_name = 'course'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_superuser and obj.teacher != self.request.user:
            raise PermissionDenied()  # Raises a 403 error if the teacher is not assigned to the course
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['sessions'] = SessionsModel.objects.all().filter(course=course)
        return context
    

class RecordAttendanceView(View, LoginRequiredMixin):
    template_name = 'session_detail.html'
    

    def get(self, request, session_id):
        session = get_object_or_404(SessionsModel, id=session_id)
        enrollments = Enrollment.objects.all().filter(course=session.course)
        existing_records = AttendanceModel.objects.all().filter(session=session).values_list('enrollment__student_id', flat=True)
        attendance = AttendanceModel.objects.all().filter(session=session)
        
        context = {
            'session': session,
            'enrollments': enrollments,
            'exist': existing_records,
            'attendance': attendance,
            'status_choices':  STATUS_CHOICES
        }
        return render(request, self.template_name, context)

    def post(self, request, session_id):
        session = get_object_or_404(SessionsModel, id=session_id)
        for key, value in request.POST.items():
            if str(key).startswith('stid'):
                stid = str(key).split('_')[1]
                enrolled = Enrollment.objects.get(student__student_id=stid, course=session.course)
                AttendanceModel.objects.update_or_create(enrollment=enrolled, session=session, defaults={'status': value})                
                print(key, stid, value)
        return redirect('main:course_detail', pk=session.course.id)


class StudentsListView(AdminRequired, ListView):
    model = StudentModel
    template_name = 'students_list.html'
    context_object_name = 'students'


class StudentUpdateView(AdminRequired, UpdateView):
    model = StudentModel
    template_name = 'student_update.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse('main:students_list')