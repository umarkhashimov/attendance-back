from datetime import date

from django.db.models import Sum
from .models import AnalyticsModel
from courses.models import CourseModel
from students.models import StudentModel, Enrollment
from payment.models import PaymentModel
from decouple import config
import requests

def record_daily_analytics():
    today = date.today()
    students = StudentModel.objects.filter(enrollment__status=True, enrollment__trial_lesson=False, enrollment__payment_due__isnull=False).distinct().count()
    enrollments = Enrollment.objects.filter(status=True, trial_lesson=False, payment_due__isnull=False).distinct().count()
    trial_enrollments = Enrollment.objects.filter(status=True, trial_lesson=True).distinct().count()
    payments = PaymentModel.objects.filter(date__date=today)
    payments_sum = payments.aggregate(s=Sum("amount"))["s"] or 0
    new_students = StudentModel.objects.filter(archived=False, enrollment_date=today).count()
    new_enrollments = Enrollment.objects.filter(status=True, created_at__date=today).count()
    courses = CourseModel.objects.filter(status=True).count()

    data, created = AnalyticsModel.objects.update_or_create(date=today,
                                            students=students,
                                            enrollments=enrollments,
                                            trial_enrollments=trial_enrollments,
                                            payments_sum=float(payments_sum),
                                            payments=payments.count(),
                                            new_students=new_students,
                                            new_enrollments=new_enrollments,
                                            courses=courses,
                                            )

    url = f"https://api.telegram.org/bot{config('ADMIN_BOT_TOKEN')}/sendMessage"
    data = {"chat_id": 5811454533, 'text': data}
    requests.post(url=url, data=data)