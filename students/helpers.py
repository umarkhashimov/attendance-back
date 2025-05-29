from datetime import datetime, date, timedelta

from courses.models import CourseModel


def calculate_balance(enrollment) -> int:
    current_date = date.today()
    weekdays = [x for x in enrollment.course.weekdays]

    if enrollment.payment_due:
        due_date = enrollment.payment_due
        balance = 0
        if current_date <= due_date:
            while current_date <= due_date:
                if str(current_date.weekday()) in weekdays:
                    balance += 1
                current_date += timedelta(days=1)
        else:
            while due_date < current_date:
                if str(due_date.weekday()) in weekdays:
                    balance -= 1
                due_date += timedelta(days=1)
        return balance
    else:
        return 0
