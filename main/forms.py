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

    weekdays = forms.MultipleChoiceField(
        choices=WEEKDAY_CHOICES,
        widget=Select2MultipleWidget(attrs={'class': 'form-control multiplechoices', 'onchange':'submit()'}),
        required=False, label="Дни"
    )

    subject = forms.ModelChoiceField(
        queryset=SubjectModel.objects.all(),
        widget=Select2Widget(attrs={'class':'form-control', 'onchange':'submit()', 'id':'subjectFilter'}),
        required=False
    )