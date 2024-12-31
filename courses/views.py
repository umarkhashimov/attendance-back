from users.filters import AdminRequired
from django.views.generic import DetailView,  UpdateView, View, CreateView
from django.core.exceptions import PermissionDenied
from .models import CourseModel, SessionsModel
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from datetime import datetime
from django.contrib import messages

from .filters import course_date_match, early_to_conduct_session
from students.models import Enrollment
from attendance.models import AttendanceModel
from .forms import CourseUpdateForm, CourseCreateForm, LessonsWeekdaysForm

class CourseUpdateView(AdminRequired, UpdateView):
    model = CourseModel
    template_name = "course_detail.html"
    form_class = CourseUpdateForm

    def get_success_url(self):
        return reverse('main:courses_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['obj'] = self.get_object()
        context['weekdays_form'] = LessonsWeekdaysForm(instance=self.get_object())
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
        if course.is_started == False:

            course.create_sessions()
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
        

class CreateCourseView(AdminRequired, CreateView):
    model = CourseModel
    template_name = 'create_course.html'
    form_class = CourseCreateForm

    def get_success_url(self):
        return reverse('main:courses_list')



class UpdateCourseWeekdaysView(AdminRequired, View):

    def post(self, request, pk):
        try:
            instance = get_object_or_404(CourseModel, id=pk)
            form = LessonsWeekdaysForm(self.request.POST, instance=instance)
            if form.is_valid():
                instance.weekdays = ','.join(form.cleaned_data['weekdays'])
                instance.save()
                instance.regenerate_coming_sessions()
                print(instance.weekdays)
                
            return redirect('courses:course_update', pk=pk)
        except:
            return redirect('main:main')
        
class CancelSessionView(View):

    def post(self, request, course_id):
        cause = self.request.POST.get('cancelCause').capitalize()
        today = datetime.now().date()
        course= get_object_or_404(CourseModel, id=course_id)
        session = SessionsModel.objects.update_or_create(course=course, date=today, defaults={'status': False, 'record_by_id': self.request.user.id, 'cancel_on_holiday': cause})

        # generate empty attendance based on enrollment status
        enrollments = Enrollment.objects.filter(course=course, status=True)
        for obj in enrollments:
            enrolled = Enrollment.objects.get(student__student_id=obj.student.student_id, course=course)
            AttendanceModel.objects.get_or_create(enrollment=enrolled, session=session[0])
            
        return redirect('attendance:session_detail', course_id=course_id)
        
class ConductSession(View):

    def get(self, request, course_id):
        today = datetime.now().date()
        course= get_object_or_404(CourseModel, id=course_id)
        session = SessionsModel.objects.update_or_create(course=course, date=today, defaults={'status': True, 'record_by_id': self.request.user.id})

        # generate empty attendance based on enrollment status
        enrollments = Enrollment.objects.filter(course=course, status=True)
        for obj in enrollments:
            enrolled = Enrollment.objects.get(student__student_id=obj.student.student_id, course=course)
            AttendanceModel.objects.get_or_create(enrollment=enrolled, session=session[0])


        return redirect('attendance:session_detail', course_id=course_id)
        # session = get_object_or_404(SessionsModel, id=session_id)

        # if request.user.role == '1' and not session_date_match(session):
        #     return redirect("main:main")

        # if early_to_conduct_session(session):
        #     messages.error(request, "Рано провести урок!")
        #     return redirect('attendance:session_detail', session_id=session_id)

        # if not session.status:
        #     session.conduct()

        #     enrollments = Enrollment.objects.all().filter(course=session.course, status='1')
        #     for obj in enrollments:
        #         enrolled = Enrollment.objects.get(student__student_id=obj.student.student_id, course=session.course)
        #         AttendanceModel.objects.get_or_create(enrollment=enrolled, session=session, defaults={'status': False})