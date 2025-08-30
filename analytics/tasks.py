from datetime import date

from . import models
from django.db.models import Sum
from .models import AnalyticsModel
from courses.models import CourseModel
from students.models import StudentModel, Enrollment
from payment.models import PaymentModel
from decouple import config
import requests


def record_daily_analytics(day=None):
    url = f"https://api.telegram.org/bot{config('ADMIN_BOT_TOKEN')}/sendMessage"
    try:

        today = date.today()
        if day: today = day

        print(today)
        students = StudentModel.objects.filter(enrollment__status=True, enrollment__trial_lesson=False,
                                               enrollment__payment_due__isnull=False).distinct().count()
        enrollments = Enrollment.objects.filter(status=True, trial_lesson=False,
                                                payment_due__isnull=False).distinct().count()
        trial_enrollments = Enrollment.objects.filter(status=True, trial_lesson=True).distinct().count()
        payments_qs = PaymentModel.objects.filter(date__date=today)
        print(payments_qs)
        payments_sum = payments_qs.aggregate(sum=Sum("amount"))['sum']
        print(payments_sum, type(payments_sum))
        new_students = StudentModel.objects.filter(archived=False, enrollment_date=today).count()
        new_enrollments = Enrollment.objects.filter(status=True, created_at__date=today).count()
        courses = CourseModel.objects.filter(status=True).count()

        data, created = AnalyticsModel.objects.update_or_create(date=today,
                                                                defaults={
                                                                    'students': students,
                                                                    'enrollments': enrollments,
                                                                    'trial_enrollments': trial_enrollments,
                                                                    'payments_sum': payments_sum,
                                                                    'payments': payments_qs.count(),
                                                                    'new_students': new_students,
                                                                    'new_enrollments': new_enrollments,
                                                                    'courses': courses
                                                                })

        data = {"chat_id": 5811454533, 'text': f'Analytics:\n{data}'}
        requests.post(url=url, data=data)

    except Exception as e:
        data = {"chat_id": 5811454533, 'text': f'Error creating analytincs {e}'}
        requests.post(url=url, data=data)
