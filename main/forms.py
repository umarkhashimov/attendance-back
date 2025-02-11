from django import forms
from django_select2.forms import Select2Widget, Select2MultipleWidget, ModelSelect2Widget

from users.models import UsersModel
from courses.models import WEEKDAY_CHOICES, SubjectModel

class CoursesListFilterForm(forms.Form):
    teacher = forms.ModelChoiceField(
        queryset=UsersModel.objects.filter(role='1'),
        widget=Select2Widget(attrs={'class':'form-select', 'onchange':'submit()'}),
        required=False, label="Учитель"
    )

    weekdays = forms.ChoiceField(
        choices=[(1, "Нечетные"), (2, "Четные"), (3, "Другие")],
        widget=Select2Widget(attrs={'class': 'form-control', 'onchange':'submit()'}),
        required=False, label="Дни"
    )

    subject = forms.ModelChoiceField(
        queryset=SubjectModel.objects.all(),
        widget=Select2Widget(attrs={'class':'form-control', 'onchange':'submit()', 'id':'subjectFilter'}),
        required=False
    )