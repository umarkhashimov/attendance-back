from courses.models import SessionsModel
from students.models import Enrollment
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from courses.models import SessionsModel
from .models import AttendanceModel, STATUS_CHOICES

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
        return redirect('courses:course_sessions', pk=session.course.id)