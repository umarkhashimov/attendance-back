from users.filters import AdminRequired
from django.views.generic import DetailView,  UpdateView, View
from django.core.exceptions import PermissionDenied
from .models import CourseModel, SessionsModel
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from datetime import datetime


from students.models import Enrollment
from attendance.models import AttendanceModel
from .forms import CourseUpdateForm

class CourseUpdateView(AdminRequired, UpdateView):
    model = CourseModel
    template_name = "course_detail.html"
    form_class = CourseUpdateForm

    def get_success_url(self):
        return reverse('main:courses_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['obj'] = self.get_object()
        return context


class CourseDetailView(DetailView):
    model = CourseModel
    template_name = 'course_sessions_list.html'
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
    
class StartCourseView(AdminRequired, View):
    def get(self, request, pk):
        return redirect("courses:course_update", pk=pk)

    def post(self, request, pk):
        course = CourseModel.objects.get(id=pk)
        course.create_sessions()
        print('Success')
        return redirect("courses:course_update", pk=pk)
    
class RedirectCourseToCloseSession(View):
    
    def get(self, request, course_id):
        today = datetime.now().date()
        course = CourseModel.objects.get(id=course_id)

        if course.is_started:

            closest_session = (
                SessionsModel.objects.filter(date__gte=today, course_id=course.id)
                .order_by('date')
                .first()
            )
            if not closest_session:
                closest_session = (
                    SessionsModel.objects.filter(date__lt=today, course_id=course.id)
                    .order_by('-date')
                    .first()
                )
            print(closest_session)
            return redirect('attendance:session_detail', session_id=closest_session.id)
        
        else:
            return redirect("main:main")
        

class ConductSession(View):

    def get(self, request, session_id):
        session = get_object_or_404(SessionsModel, id=session_id)
        if not session.conducted:
            session.conduct()

            enrollments = Enrollment.objects.all().filter(course=session.course, status='1')
            for obj in enrollments:
                enrolled = Enrollment.objects.get(student__student_id=obj.student.student_id, course=session.course)
                AttendanceModel.objects.update_or_create(enrollment=enrolled, session=session, defaults={'status': False})

        return redirect('attendance:session_detail', session_id=session_id)

        