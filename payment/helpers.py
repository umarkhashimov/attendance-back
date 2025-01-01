import math

def calculate_payment_amount(enrollment, count):
    cost = enrollment.course.session_cost
    discount = enrollment.discount


    cost_by_count = cost * count
    discount_amount = (cost_by_count / 100) * discount
    overall = cost_by_count - discount_amount

    return float(overall)

