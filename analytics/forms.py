from django import forms
import datetime
from .models import AnalyticsModel
from django_select2.forms import Select2Widget

FIELDS = [
    "payments_sum",
    "payments",
    "students",
    "enrollments",
    "trial_enrollments",
    "new_students",
    "new_enrollments",
    "courses",
]

class AnalyticsFilterForm(forms.Form):
    date_from = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date', 'onchange': 'submit()', 'class': 'form-control', 'max': datetime.date.today()}),
        required=False, label="С")

    date_to = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date', 'onchange': 'submit()', 'class': 'form-control', 'max': datetime.date.today()}),
        required=False, label="До")

    show = forms.ChoiceField(
        choices={f: str(AnalyticsModel._meta.get_field(f).verbose_name) for f in FIELDS},
        widget=Select2Widget(attrs={'class': 'form-control','onchange': 'submit()'}), label="Показать", required=False
    )

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        start_date = self.initial.get("date_from")
        end_date = self.initial.get("date_to")

        # if start_date and not end_date:
        #     self.initial['date_to'] = start_date

        # elif end_date and not start_date:
        #     self.initial['date_from'] = end_date

        if start_date:
            self.fields['date_to'].widget.attrs.update({'min': start_date, 'max': datetime.date.today()})

        if end_date:
            self.fields['date_from'].widget.attrs.update({'max': end_date})