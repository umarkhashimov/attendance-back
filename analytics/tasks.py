from datetime import date
from django.db.models.functions import Cast
from .models import AnalyticsModel
from courses.models import CourseModel
from students.models import StudentModel, Enrollment
from payment.models import PaymentModel
from decouple import config
import requests

from datetime import datetime, time, timedelta
from django.utils import timezone
from django.db.models import Sum, FloatField, Value
from django.db.models.functions import Coalesce



def record_daily_analytics(day=None):
    url = f"https://api.telegram.org/bot{config('ADMIN_BOT_TOKEN')}/sendMessage"
    try:

        today = date.today()
        if day: today = day

        tz = timezone.get_current_timezone()
        start_local = timezone.make_aware(datetime.combine(today, time.min), tz)
        end = timezone.make_aware(datetime.combine(today + timedelta(days=1), time.min), tz)

        students = StudentModel.objects.filter(enrollment__status=True, enrollment__trial_lesson=False,
                                               enrollment__payment_due__isnull=False).distinct().count()
        enrollments = Enrollment.objects.filter(status=True, trial_lesson=False,
                                                payment_due__isnull=False).distinct().count()
        trial_enrollments = Enrollment.objects.filter(status=True, trial_lesson=True).distinct().count()

        payments_qs = PaymentModel.objects.filter(date__gte=start_local, date__lte=end)
        payments_sum = payments_qs.aggregate(total=Coalesce(Cast(Sum('amount'), FloatField()), Value(0.0, output_field=FloatField())))['total']

        new_students = StudentModel.objects.filter(archived=False, enrollment_date=today).count()
        new_enrollments = Enrollment.objects.filter(status=True, created_at__date=today).count()
        courses = CourseModel.objects.filter(status=True, archived=False).count()

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
