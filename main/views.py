from django.views.generic import TemplateView, DetailView
from django.core.exceptions import PermissionDenied
from datetime import date
from django.utils import timezone
from courses.models import CourseModel, SessionsModel
from students.models import Enrollment, StudentModel
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View


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
    
class SessionDetailView(DetailView):
    model = SessionsModel
    template_name = 'session_detail.html'
    context_object_name = 'session'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_superuser and obj.course.teacher != self.request.user:
            raise PermissionDenied()  # Raises a 403 error if the teacher is not assigned to the course
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_object()
        context['students'] = Enrollment.objects.all().filter(course=session.course)
        return context
    

class RecordAttendanceView(View):
    template_name = 'session_detail.html'

    def get(self, request, session_id):
        session = get_object_or_404(SessionsModel, id=session_id)
        enrollments = Enrollment.objects.all().filter(course=session.course)
        existing_records = AttendanceModel.objects.all().filter(session=session).values_list('enrollment__student_id', flat=True)

        # Fetch attendance records for the specified session
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
        return redirect('main:session_detail', session_id=session.id)
        # AttendanceFormSet = modelformset_factory(AttendanceModel, form=AttendanceForm, extra=0, can_delete=False)
        # formset = AttendanceFormSet(request.POST)
        
        # if formset.is_valid():
        #     # Save attendance records for the session
        #     formset.save()
        #     return redirect('course_detail', pk=session.course.pk)  # Adjust the redirect as needed
        # context = {
        #     'session': session,
        #     'formset': formset,
        # }
        # return render(request, self.template_name, context)




# def record_attendance(request, session_id):
#     session = get_object_or_404(SessionsModel, id=session_id)
#     enrolled_students = Enrollment.objects.filter(course=session.course)

#     # Check if attendance records already exist for this session
#     existing_records = AttendanceModel.objects.filter(session=session)

#     AttendanceFormSet = modelformset_factory(AttendanceModel, fields='__all__', extra=0)

#     if request.method == 'POST':
#         formset = AttendanceFormSet(request.POST, queryset=existing_records)
        
#         if formset.is_valid():
#             formset.save()
#             return redirect('main:main')  # Redirect as needed
#     else:
#         # Create attendance records if they don't exist for this session
#         if not existing_records.exists():
#             AttendanceModel.objects.bulk_create([
#                 AttendanceModel(enrollment=enrollment, session=session, status='0')  # Default to 'Absent'
#                 for enrollment in enrolled_students
#             ])
#             existing_records = AttendanceModel.objects.filter(session=session)

#         formset = AttendanceFormSet(queryset=existing_records)

#     return render(request, 'session_detail.html', {'formset': formset, 'session': session})
