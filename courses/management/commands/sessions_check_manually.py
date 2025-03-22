from django.core.management.base import BaseCommand
from decouple import config
import requests, os, datetime

from courses.models import SessionsModel, CourseModel
from students.models import Enrollment
from attendance.models import AttendanceModel


def alert_admin_chat(text):
    url = f"https://api.telegram.org/bot{config('ADMIN_BOT_TOKEN')}/sendMessage"
    data = {"chat_id": config('ADMIN_CHAT_ID'), 'text': text}
    requests.post(url=url, data=data)

def mark_unmarked_sessions(date):
    if date:

        today = date

        marked_sessions = SessionsModel.objects.filter(date=today)

        sessions_today = CourseModel.objects.filter(status=True, weekdays__contains=str(today.weekday()))
        # Exclude courses that already have marked sessions
        marked_course_ids = marked_sessions.values_list('course', flat=True)
        unmarked_sessions_today = sessions_today.exclude(id__in=marked_course_ids)

        if len(unmarked_sessions_today) > 0:
         message = f'#отмеченовручную\n Уроки отмеченые вручную.\n\nДата: {today}\n\n'
         for course in unmarked_sessions_today:
             session, created = SessionsModel.objects.get_or_create(course=course, date=today, defaults={'status': True, 'record_by_id': None, 'topic': course.last_topic})

             if created:
                 enrollments = Enrollment.objects.filter(course=course, status=True)
                 for obj in enrollments:
                     enrolled = Enrollment.objects.get(student__student_id=obj.student.student_id, course=course)
                     AttendanceModel.objects.get_or_create(enrollment=enrolled, session=session)

                     if not obj.trial_lesson:
                         obj.substract_one_session()

                 text = f'Группа: {course}\nУчитель: #{course.teacher.username} - {course.teacher.get_full_name}\n\n'
                 message += text

         alert_admin_chat(message)


class Command(BaseCommand):
 help = "Runs the APScheduler for Django"

 def add_arguments(self, parser):
    parser.add_argument("--date",
            type=str,
            help="Date in YYYY-MM-DD format",
            required=True)

 def handle(self, *args, **options):
     date_str = options["date"]
     date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
     print(f'Checking sessions manually: {date}')
     mark_unmarked_sessions(date)