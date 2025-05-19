import datetime
from cProfile import label

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
        choices=[(1, "Имя Фамилия"), (2, "Имя Фамилия (убывание)"), (3, "Последние"), (4, "Ранние"),],
        widget=Select2Widget(attrs={'class': 'form-select', 'onchange': 'submit()'}),
        label="Сортировать по", required=False
    )

    display_only = forms.ChoiceField(
        choices=[(1, 'Активные'), (2,'Неактивные'), (3, "Пробники"), (4, "Должники")],
        widget=Select2Widget(attrs={'class': 'form-control', 'onchange':'submit()'}),
        label="Показать", required=False
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

    display_only = forms.ChoiceField(
        choices=[(1, 'Пробники'), (2, 'Неактивные'), (3, "Должники"), (4, "Активные"), (5, "Замороженные")],
        widget=Select2Widget(attrs={'class': 'form-control', 'onchange': 'submit()'}),
        label="Показать", required=False
    )

    order_by = forms.ChoiceField(
        choices=[(1, "Имя Фамилия"), (2, "Группа (id)"), (3, "Группа (время)"), (4, "Ранние"), ],
        widget=Select2Widget(attrs={'class': 'form-select', 'onchange': 'submit()'}),
        label="Сортировать по", required=False
    )

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        start_date = self.initial.get("date_from")
        end_date = self.initial.get("date_to")
        print('HIiiii')

        if start_date and not end_date:
            self.initial['date_to'] = start_date

        elif end_date and not start_date:
            self.initial['date_from'] = end_date


        if start_date:
            self.fields['date_to'].widget.attrs.update({'min': start_date, 'max': datetime.date.today()})

        if end_date:
            self.fields['date_from'].widget.attrs.update({'max': end_date})
            # self.fields['date_to'].widget.attrs.update({'min': start_date, 'max': datetime.date.today()})

            #
            # if end_date:
            #     payment_date_start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            #     payment_date_end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            #
            #     if payment_date_end < payment_date_start:
            #         self.initial['date_to'] = datetime.date.today().strftime('%Y-%m-%d')
            # else:
            #     self.initial['date_to'] = datetime.date.today().strftime('%Y-%m-%d')