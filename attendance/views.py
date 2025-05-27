from students.models import Enrollment
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from courses.filters import course_date_match
from courses.models import SessionsModel, CourseModel
from .models import AttendanceModel
from datetime import datetime
from payment.helpers import last_closest_session_date
    

class GetSessionView(View):

    def post(self, request, course_id, session_id, session_date):
        course = get_object_or_404(CourseModel, id=course_id)
        session = get_object_or_404(SessionsModel, id=session_id, date=session_date)

        if request.user.role == '1' and not course_date_match(course=course):
            return redirect("main:main")

        keys = {key: value for key, value in request.POST.items()}.keys()
        attendances = AttendanceModel.objects.all().filter(session=session)

        session.topic = request.POST.get('topic', '')
        session.save()
        session.course.set_topic()

        for obj in attendances:


            if f"stid_{obj.enrollment.student.student_id}" in keys:

                status = request.POST.get(str(f'stid_{obj.enrollment.student.student_id}'), None)
                if status in ['1', '2', '0']:
                    obj.status = int(status)
                    if obj.status in [1,2]:
                        if (obj.enrollment.trial_lesson and not obj.trial_attendance) and session.date == datetime.today().date():
                            if not obj.enrollment.trail_used_once:
                                obj.trial_attendance = obj.enrollment.trial_lesson

                            if obj.enrollment.trial_lesson and not obj.enrollment.trail_used_once:
                                obj.enrollment.trail_used_once = True
                                obj.enrollment.trail_used_once_date = datetime.today().date()
                            else:
                                obj.enrollment.trial_lesson = False

                                if not obj.enrollment.payment_due:
                                    print('last session date calculate')
                                    obj.enrollment.payment_due = last_closest_session_date(obj.enrollment.course)

                            obj.save()
                            obj.enrollment.save()

                        attendance_grade = request.POST.get(str(f'ga_{obj.enrollment.student.student_id}'), None)
                        homework_grade = request.POST.get(str(f'ghw_{obj.enrollment.student.student_id}'), None)
                        obj.participation_grade = attendance_grade if attendance_grade else None
                        obj.homework_grade = homework_grade if homework_grade else None

            obj.save()

        return redirect('/?date=' + session_date)