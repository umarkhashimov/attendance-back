from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django import template

register = template.Library()

@register.filter
def div(value, arg):
    try:
        return Decimal(str(value)) / Decimal(str(arg))
    except (InvalidOperation, ZeroDivisionError, TypeError):
        return ""
