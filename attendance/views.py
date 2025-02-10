from students.models import Enrollment
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from courses.filters import course_date_match
from courses.models import SessionsModel, CourseModel
from courses.forms import CancelCauseForm, SessionTopicFieldForm
from users.filters import AdminRequired
from .models import AttendanceModel
from datetime import datetime 

class NewSessionView(View, LoginRequiredMixin):
    template_name = 'session_detail.html'
    
    def get(self, request, course_id):
        course = get_object_or_404(CourseModel, id=course_id)

        if request.user.role == '1' and not course_date_match(course):
            return redirect("main:main")
        
        today = datetime.now().date()
        session = SessionsModel.objects.filter(course=course, date=today)
        
        if session.exists():
            obj = SessionsModel.objects.get(course=course, date=today)
            return redirect('attendance:session_detail', course_id=course_id, session_id=obj.id)
        

        sessions = SessionsModel.objects.filter(course=course)

        context = {
            'session': session,
            'course': course,
            'all_session_dates': sessions,
            'today': today,
            'cancel_cause_form': CancelCauseForm(),
            # 'enrollments': enrollments,
            # 'exist': existing_records,
        }

        if session:
            context.update({
                'prev_session': SessionsModel.objects.filter(id__lt=session.id, course=session.course).order_by('-id').first(),
                'next_session': SessionsModel.objects.filter(id__gt=session.id, course=session.course).order_by('id').first(),
            })

        return render(request, self.template_name, context)
    
class RedirecToSessionByDate(View, AdminRequired):

    def get(self, request, course_id):
        date = self.request.GET.get('date')
        session = SessionsModel.objects.get(course_id=course_id, date=date)

        if session:
            return redirect('attendance:session_detail', session_id=session.id)
        else:
            return redirect('main:main')


class GetSessionView(View):
    template_name = 'session_detail.html'

    def get(self, request, course_id, session_id):
        course = get_object_or_404(CourseModel, id=course_id)
        session = get_object_or_404(SessionsModel, id=session_id)

        if request.user.role == '1' and not course_date_match(course):
            return redirect("main:main")
        
        attendance = AttendanceModel.objects.all().filter(session=session)
        sessions = SessionsModel.objects.filter(course=course)
       
        if session.date == datetime.today().date():
            fresh_enrolled = Enrollment.objects.filter(course=session.course, status=True).exclude(student_id__in=attendance.values_list('enrollment__student_id', flat=True))
            for enroll in fresh_enrolled:
                if not AttendanceModel.objects.filter(session=session, enrollment__student_id=enroll.student.id).exists():
                    AttendanceModel.objects.create(enrollment=enroll, session=session)

            attendance = AttendanceModel.objects.all().filter(session=session)

        context = {
            'session': session,
            'course': course,
            'attendance': attendance,
            'all_session_dates': sessions,
            'cancel_cause_form': CancelCauseForm,
            'session_topic': SessionTopicFieldForm(instance=session)
        }

        if session:
            context.update({
                'prev_session': SessionsModel.objects.filter(id__lt=session.id, course=session.course).order_by('-id').first(),
                'next_session': SessionsModel.objects.filter(id__gt=session.id, course=session.course).order_by('id').first(),
            })

        return render(request, self.template_name, context)
    

    def post(self, request, course_id, session_id):
        course = get_object_or_404(CourseModel, id=course_id)
        session = get_object_or_404(SessionsModel, id=session_id)

        if request.user.role == '1' and not course_date_match(course=course):
            return redirect("main:main")

        keys = {key: value for key, value in request.POST.items()}.keys()
        attendances = AttendanceModel.objects.all().filter(session=session)

        session.topic = request.POST.get('topic', '')
        session.save()

        for obj in attendances:

            if f"stid_{obj.enrollment.student.student_id}" in keys:

                status = request.POST.get(str(f'stid_{obj.enrollment.student.student_id}'), None)
                if status == 'present':
                    attendance_grade = request.POST.get(str(f'ga_{obj.enrollment.student.student_id}'), None)
                    homework_grade = request.POST.get(str(f'ghw_{obj.enrollment.student.student_id}'), None)
                    obj.participation_grade = attendance_grade if attendance_grade else None
                    obj.homework_grade = homework_grade if homework_grade else None
                    obj.status = 1
                elif status == 'absent':
                    obj.status = 0

            obj.save()

        if request.user.role == '1':
            return redirect('main:main')

        return redirect(request.path, pk=session.course.id)