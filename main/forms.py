import datetime
from datetime import date
from cProfile import label
from random import choices

from django import forms
from django_select2.forms import Select2Widget, Select2MultipleWidget, ModelSelect2Widget

from students.models import StudentModel
from users.models import UsersModel
from courses.models import WEEKDAY_CHOICES, SubjectModel, CourseModel


class CoursesListFilterForm(forms.Form):
    teacher = forms.ModelChoiceField(
        queryset=UsersModel.objects.filter(role='1', is_active=True),
        widget=Select2Widget(attrs={'class':'form-select', 'onchange':'submit()'}),
        required=False, label="Учитель"
    )

    weekdays = forms.ChoiceField(
        choices=[('', "--"), (1, "Нечетные"), (2, "Четные"), (3, "Другие")],
        widget=forms.Select(attrs={'class': 'form-select', 'onchange':'submit()'}),
        required=False, label="Дни"
    )

    subject = forms.ModelChoiceField(
        queryset=SubjectModel.objects.all(),
        widget=Select2Widget(attrs={'class':'form-control', 'onchange':'submit()', 'id':'subjectFilter'}),
        required=False, label="Курс"
    )

    sort_by = forms.ChoiceField(choices=[('', '--'), ('3', 'Новые (15д)'), ('4', 'Новые (30д)'),('1',"Время урока"), ('6', 'Время урока (убыв.)'), ('2', 'Предмет'), ('5', 'Учитель')],
                                widget=forms.Select(attrs={'class':'form-select', 'onchange':'submit()', 'id':'sortByFilter'}),
                                required=False, label="Сортировка")

    display = forms.ChoiceField(
        choices=[(1, 'Существующие'), (2, "Архив"), (3, 'Все') ],
        widget=forms.Select(attrs={'class': 'form-select', 'onchange': 'submit()'}),
        required=False, label="Показать"
    )

class StudentsListFilterForm(forms.Form):
    text = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control shadow-none rounded-1 py-0', 'onchange': 'submit()'}),
        required=False, label="Имя/Номер"
    )

    teacher = forms.ModelChoiceField(
        queryset=UsersModel.objects.filter(role='1', is_active=True),
        widget=Select2Widget(attrs={'class': 'form-select', 'onchange': 'submit()'}),
        required=False, label="Учитель"
    )

    order_by = forms.ChoiceField(
        choices=[(1, "Имя Фамилия"), (2, "Имя Фамилия (убывание)"), (3, "Последние"), (4, "Ранние"),],
        widget=forms.Select(attrs={'class': 'form-select', 'onchange': 'submit()'}),
        label="Сортировать по", required=False
    )

    enrollment_month = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'month', 'class': 'form-control', 'onchange': 'submit()'}),
        label="Выбрать месяц",
        input_formats=['%Y-%m']  # Required to parse '2025-04' format
    )

    date_from = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date', 'onchange': 'submit()', 'class': 'form-control', 'max': date.today().isoformat()}),
        required=False, label="С")

    date_to = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date', 'onchange': 'submit()', 'class': 'form-control', 'max': date.today().isoformat()}),
        required=False, label="До")

    display = forms.ChoiceField(
        choices=[(2, 'Активные'), (3, "Архив"), (1, 'Все')],
        widget=forms.Select(attrs={'class': 'form-select', 'onchange': 'submit()'}),
        required=False, label="Показать"
    )

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        start_date = self.initial.get("date_from")
        end_date = self.initial.get("date_to")

        if start_date and not end_date:
            self.initial['date_to'] = start_date

        elif end_date and not start_date:
            self.initial['date_from'] = end_date


        if start_date:
            self.fields['date_to'].widget.attrs.update({'min': start_date, 'max': date.today().isoformat()})

        if end_date:
            self.fields['date_from'].widget.attrs.update({'max': end_date})

class TeachersListFilterForm(forms.Form):
    text = forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={'class': 'form-control shadow-none rounded-1 py-0', 'onchange': 'submit()'}),
        required=False, label="Имя пользователя / Имя / Фамилия"
    )

class EnrollmentsListFilterForm(forms.Form):
    student = forms.ModelChoiceField(queryset=StudentModel.objects.all(),
                                     widget=Select2Widget(attrs={'class': 'form-control', 'onchange':'submit()'}),
                                     required=False, label="Ученик")

    course = forms.ModelChoiceField(queryset=CourseModel.objects.all(),
                                    widget=Select2Widget(attrs={'class': 'form-control', 'onchange':'submit()'}),
                                    required=False, label="Группа")

    enrolled_by = forms.ModelChoiceField(queryset=UsersModel.objects.filter(role='2'),
                                         widget=Select2Widget(attrs={'class': 'form-control', 'onchange':'submit()'}),
                                         required=False, label="Кем записан")

    date_from = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date', 'onchange': 'submit()', 'class': 'form-control', 'max': datetime.date.today()}),
                                         required=False, label="С")
    date_to = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date', 'onchange': 'submit()', 'class': 'form-control', 'max': datetime.date.today()}),
                                       required=False, label="До")

    DISPLAY_CHOICES = [(4, "Активные"),(1, 'Пробники'), (2, 'Неактивные'), (3, "Должники"), (6, "Замороженные")]
    display_only = forms.ChoiceField(
        choices=DISPLAY_CHOICES,
        widget=Select2Widget(attrs={'class': 'form-control', 'onchange': 'submit()'}),
        label="Показать", required=False
    )

    order_by = forms.ChoiceField(
        choices=[(1, "Имя Фамилия"), (2, "Группа (id)"), (3, "Группа (время)"), (4, "Дата записи (создания)"), (5, "Дата Записи") ],
        widget=Select2Widget(attrs={'class': 'form-select', 'onchange': 'submit()'}),
        label="Сортировать по", required=False
    )

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        start_date = self.initial.get("date_from")
        end_date = self.initial.get("date_to")

        if start_date and not end_date:
            self.initial['date_to'] = start_date

        elif end_date and not start_date:
            self.initial['date_from'] = end_date

        if start_date:
            self.fields['date_to'].widget.attrs.update({'min': start_date, 'max': datetime.date.today()})
            self.fields['display_only'].choices = [(5, "Активные (новые)")] + self.DISPLAY_CHOICES

        if end_date:
            self.fields['date_from'].widget.attrs.update({'max': end_date})

