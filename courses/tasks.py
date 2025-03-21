from multiprocessing.pool import job_counter

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from decouple import config
import requests, os, datetime
from pyexpat.errors import messages

from .models import SessionsModel, CourseModel
from students.models import Enrollment
from attendance.models import AttendanceModel

def alert_admin_chat(text):
    url = f"https://api.telegram.org/bot{config('ADMIN_BOT_TOKEN')}/sendMessage"
    data = {"chat_id": config('ADMIN_CHAT_ID'), 'text': text}
    requests.post(url=url, data=data)

def mark_unmarked_sessions():
    today = datetime.date.today()

    marked_sessions = SessionsModel.objects.filter(date=today)

    sessions_today = CourseModel.objects.filter(status=True, weekdays__contains=str(today.weekday()))
    # Exclude courses that already have marked sessions
    marked_course_ids = marked_sessions.values_list('course', flat=True)
    unmarked_sessions_today = sessions_today.exclude(id__in=marked_course_ids)

    if len(unmarked_sessions_today) > 0:
        message = f'#неотмеченные\n🤖 Здравствуйте, отметил не отмеченные уроки за сегодня.\n\nДата: {today}\n\n'
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

def send_test_message():
    url = f"https://api.telegram.org/bot{config('ADMIN_BOT_TOKEN')}/sendMessage"
    data = {"chat_id": 5811454533, 'text': f"scheduler is working!\ndatetime: {datetime.datetime.now()}"}
    requests.post(url=url, data=data)

def start():
    if os.environ.get('RUN_MAIN') == 'true':
        scheduler = BackgroundScheduler()
        scheduler.add_job(mark_unmarked_sessions, CronTrigger(hour=23, minute=00))  # 11 PM
        # scheduler.add_job(send_test_message, IntervalTrigger(seconds=10), max_instances=1)  # 11 PM
        scheduler.add_job(send_test_message, CronTrigger(hour=2, minute=2))  # 11 PM
        scheduler.start()

