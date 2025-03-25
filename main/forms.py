import datetime
from cProfile import label

from django import forms
from django_select2.forms import Select2Widget, Select2MultipleWidget, ModelSelect2Widget

from users.models import UsersModel
from courses.models import WEEKDAY_CHOICES, SubjectModel

class CoursesListFilterForm(forms.Form):
    teacher = forms.ModelChoiceField(
        queryset=UsersModel.objects.filter(role='1', is_active=True),
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
        required=False, label="Курс"
    )

class StudentsListFilterForm(forms.Form):
    text = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control shadow-none rounded-1 py-0', 'onchange': 'submit()'}),
        required=False, label="Имя/Номер"
    )

    teacher = forms.ModelChoiceField(
        queryset=UsersModel.objects.filter(role='1', is_active=True),
        widget=Select2Widget(attrs={'class': 'form-select', 'onchange': 'submit()'}),
        required=False, label="Учитель"
    )

    order_by = forms.ChoiceField(
        choices=[(1, "Имя Фамилия"), (2, "Должники"), (3, "Новые за 30 дней"), (4, "Новые за 60 дней"), (5, "Активные"), (8, "Не активные"), (6, "Последние"), (7, "Ранние"),],
        widget=forms.Select(attrs={'class': 'form-select', 'onchange': 'submit()'}),
        label="Сортировать по", required=False
    )

    enrollment_month = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'month', 'class': 'form-control', 'onchange': 'submit()'}),
        label="Выбрать месяц",
        input_formats=['%Y-%m']  # Required to parse '2025-04' format
    )

class TeachersListFilterForm(forms.Form):
    text = forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={'class': 'form-control shadow-none rounded-1 py-0', 'onchange': 'submit()'}),
        required=False, label="Имя пользователя / Имя / Фамилия"
    )