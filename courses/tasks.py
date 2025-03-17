from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import datetime

from .models import SessionsModel, CourseModel
from students.models import Enrollment
from attendance.models import AttendanceModel

def mark_unmarked_sessions():
    today = datetime.date.today()

    marked_sessions = SessionsModel.objects.filter(date=today)

    sessions_today = CourseModel.objects.filter(status=True, weekdays__contains=str(today.weekday()))
    # Exclude courses that already have marked sessions
    marked_course_ids = marked_sessions.values_list('course', flat=True)
    unmarked_sessions_today = sessions_today.exclude(id__in=marked_course_ids)

    for course in unmarked_sessions_today:
        session, created = SessionsModel.objects.get_or_create(course=course, date=today, defaults={'status': True, 'record_by_id': None, 'topic': course.last_topic})

        if created:
            # generate empty attendance based on enrollment status
            enrollments = Enrollment.objects.filter(course=course, status=True)
            for obj in enrollments:
                enrolled = Enrollment.objects.get(student__student_id=obj.student.student_id, course=course)
                AttendanceModel.objects.get_or_create(enrollment=enrolled, session=session)

                if not obj.trial_lesson:
                    obj.substract_one_session()

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(mark_unmarked_sessions, CronTrigger(hour=23, minute=00))  # 11 PM
    # scheduler.add_job(my_scheduled_task, IntervalTrigger(seconds=2))  # 11 PM
    scheduler.start()

