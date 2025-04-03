from datetime import date, timedelta
import datetime

def calculate_payment_amount(enrollment, count):
    cost = enrollment.course.session_cost # 940000 - 12
    discount = enrollment.discount
    

    cost_by_count = cost * count
    discount_amount = (cost_by_count / 100) * discount
    overall = cost_by_count - discount_amount

    return float(overall)

def calculate_payment_due_date(enrollment, iterate_balance=None, count_from=None):
    weekdays = [x for x in enrollment.course.weekdays]

    due_date = current_date = date.today() if count_from is None else count_from

    # iterator = enrollment.balance if iterate_balance is None else iterate_balance
    iterator = 12
    iterations = 0
    while iterations < iterator:
        if str(current_date.weekday()) in weekdays:
            due_date = current_date
            iterations += 1
        current_date += timedelta(days=1)

    return due_date


def next_closest_session_date(course, today=None):
    today = today + timedelta(days=1) if today else date.today()
    weekdays = [x for x in course.weekdays]

    next_date = None
    max_iterations = 7
    while next_date is None and max_iterations > 0:
        if str(today.weekday()) in weekdays:
            return today
        today = today + timedelta(days=1)
        max_iterations -= 1

    return date.today()