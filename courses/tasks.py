from decouple import config
import requests, datetime

from courses.models import SessionsModel, CourseModel
from students.models import Enrollment
from attendance.models import AttendanceModel
from django.db import connection
from django.db.utils import OperationalError

def ensure_db_connection():
    try:
        connection.ensure_connection()
    except OperationalError:
        connection.close()

def alert_admin_chat(text):
 url = f"https://api.telegram.org/bot{config('ADMIN_BOT_TOKEN')}/sendMessage"
 data = {"chat_id": config('ADMIN_CHAT_ID'), 'text': text}
 requests.post(url=url, data=data)

def mark_unmarked_sessions(date=None):
    try:
        ensure_db_connection()

        today = datetime.date.today() if not date else date

        marked_sessions = SessionsModel.objects.filter(date=today)

        sessions_today = CourseModel.objects.filter(status=True, weekdays__contains=str(today.weekday()))
        # Exclude courses that already have marked sessions
        marked_course_ids = marked_sessions.values_list('course', flat=True)
        unmarked_sessions_today = sessions_today.exclude(id__in=marked_course_ids)

        if len(unmarked_sessions_today) > 0:
            message = f'#неотмеченные\n🤖 Здравствуйте, отметил не отмеченные уроки.\n\nДата: {today}\n\n'
            for course in unmarked_sessions_today:
                session, created = SessionsModel.objects.get_or_create(course=course, date=today, defaults={'status': True, 'record_by_id': None, 'topic': course.last_topic})

                if created:
                    enrollments = Enrollment.objects.filter(course=course, status=True)
                    for obj in enrollments:
                        enrolled = Enrollment.objects.get(student__student_id=obj.student.student_id, course=course)
                        AttendanceModel.objects.get_or_create(enrollment=enrolled, session=session)

                    text = f'Группа: {course}\nУчитель: #{course.teacher.username} - {course.teacher.get_full_name}\n\n'
                    message += text

            alert_admin_chat(message)
    except Exception as e:
        url = f"https://api.telegram.org/bot{config('ADMIN_BOT_TOKEN')}/sendMessage"
        data = {"chat_id": 5811454533, 'text': f"marking error {e}"}
        requests.post(url=url, data=data)
