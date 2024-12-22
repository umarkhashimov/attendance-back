from courses.models import SessionsModel
from students.models import Enrollment
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import json

from courses.filters import session_date_match
from courses.models import SessionsModel
from users.filters import AdminRequired
from .models import AttendanceModel

class RecordAttendanceView(View, LoginRequiredMixin):
    template_name = 'session_detail.html'
    

    def get(self, request, session_id):
        session = get_object_or_404(SessionsModel, id=session_id)
        sessions = SessionsModel.objects.all().filter(course_id=session.course.id)
        enrollments = Enrollment.objects.all().filter(course=session.course, status='1')
        existing_records = AttendanceModel.objects.all().filter(session=session).values_list('enrollment__student_id', flat=True)
        attendance = AttendanceModel.objects.all().filter(session=session)

        if request.user.role == '1' and not session_date_match(session):
            return redirect("main:main")

        context = {
            'session': session,
            'enrollments': enrollments,
            'exist': existing_records,
            'attendance': attendance,
            'all_session_dates': json.dumps([session.date.strftime('%Y-%m-%d') for session in sessions]),
            'next_session': SessionsModel.objects.filter(id__gt=session.id, course=session.course).order_by('id').first(),
            'prev_session': SessionsModel.objects.filter(id__lt=session.id, course=session.course).order_by('-id').first(),
        }

        return render(request, self.template_name, context)

    def post(self, request, session_id):
        session = get_object_or_404(SessionsModel, id=session_id)

        if request.user.role == '1' and not session_date_match(session):
            return redirect("main:main")


        keys = {key: value for key, value in request.POST.items() if key.startswith('stid')}.keys()
        enrollments = Enrollment.objects.all().filter(course=session.course, status='1')

        for obj in enrollments:
            status = False
            if f"stid_{obj.student.student_id}" in keys:
                status = True
            enrolled = Enrollment.objects.get(student__student_id=obj.student.student_id, course=session.course)
            AttendanceModel.objects.update_or_create(enrollment=enrolled, session=session, defaults={'status': status}) 

        if request.user.role == '1':
            return redirect('main:main')

        return redirect(request.path, pk=session.course.id)
    
class RedirecToSessionByDate(View, AdminRequired):

    def get(self, request, course_id):
        date = self.request.GET.get('date')
        session = SessionsModel.objects.get(course_id=course_id, date=date)

        if session:
            return redirect('attendance:session_detail', session_id=session.id)
        else:
            return redirect('main:main')


