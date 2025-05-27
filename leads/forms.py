from django import forms
from django_select2.forms import Select2Widget
import datetime

from courses.models import CourseModel, SubjectModel
from users.models import UsersModel
from .models import LeadsModel
from students.models import StudentModel

class LeadForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=StudentModel.objects.all(),
                                     widget=Select2Widget(attrs={'class': 'form-control'}),required=False, label='Выберите ученика')
    select_student = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'onclick': 'toggleStudentInputType(this)'}), label='Создать нового ученика', initial=True)

    class Meta:
        model = LeadsModel
        fields = ['weekdays', 'subject', 'lesson_time', 'teacher', 'arrival_date', 'note']
        widgets = {
            'teacher': Select2Widget(attrs={'class': 'form-control'}),
            'subject': Select2Widget(attrs={'class': 'form-control'}),
            'weekdays': Select2Widget(attrs={'class': 'form-control'}),
            'lesson_time': forms.TimeInput(
                format='%H:%M',
                attrs={
                    'class': 'form-control',
                    'placeholder': 'HH:MM',
                    'type': 'time',
                    'id': 'LessonTimePicker',
                }
            ),
            'arrival_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'id': 'datePicker',
                }
            )
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add attributes to all fields

        if self.fields['select_student'].initial == False:
            self.fields['student'].required = True

        for field_name, field in self.fields.items():
            if field_name not in ['lesson_time', 'select_student']:
                field.widget.attrs.update({
                    "class": "form-control",  # Add Bootstrap class
                    "placeholder": ' ',  # Optional: Use label as placeholder
                })



class LeadsListFilterForm(forms.Form):
    student = forms.ModelChoiceField(queryset=StudentModel.objects.all(),
                                     widget=Select2Widget(attrs={'class': 'form-control', 'onchange': 'submit()'}),
                                     required=False, label="Ученик")

    weekdays = forms.ChoiceField(
        choices=[(1, "Нечетные"), (2, "Четные"), (3, "Другие")],
        widget=Select2Widget(attrs={'class': 'form-control', 'onchange': 'submit()'}),
        required=False, label="Дни"
    )

    teacher = forms.ModelChoiceField(queryset=UsersModel.objects.filter(role='1', is_active=True),
                                     widget=Select2Widget(attrs={'class': 'form-control', 'onchange': 'submit()'}),
                                     required=False, label="Учитель")

    status = forms.ChoiceField(choices=[(1, "Ожидание"), (2, "Обработан"), (3, "Отменен")],
                               widget=Select2Widget(attrs={'class': 'form-control', 'onchange': 'submit()'}),
                               required=False, label="Статус")

    subject = forms.ModelChoiceField(queryset=SubjectModel.objects.all(),
                                     widget=Select2Widget(attrs={'class': 'form-control', 'onchange': 'submit()'}),
                                     required=False, label="Предмет")

    created_by = forms.ModelChoiceField(UsersModel.objects.filter(role='2', is_active=True),
                                        widget=Select2Widget(attrs={'class': 'form-control', 'onchange': 'submit()'}),
                                        required=False, label="Кем создан")

    date_from = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date', 'onchange': 'submit()', 'class': 'form-control', 'max': datetime.date.today()}),
        required=False, label="С")

    date_to = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date', 'onchange': 'submit()', 'class': 'form-control', 'max': datetime.date.today()}),
        required=False, label="До")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        start_date = self.initial.get("date_from")
        end_date = self.initial.get("date_to")

        if start_date and not end_date:
            self.initial['date_to'] = start_date

        elif end_date and not start_date:
            self.initial['date_from'] = end_date

        if start_date:
            self.fields['date_to'].widget.attrs.update({'min': start_date, 'max': datetime.date.today()})

        if end_date:
            self.fields['date_from'].widget.attrs.update({'max': end_date})


class LeadUpdateForm(forms.ModelForm):

    class Meta:
        model = LeadsModel
        fields = ['weekdays', 'subject', 'lesson_time', 'teacher', 'arrival_date', 'note']
        widgets = {
            'teacher': Select2Widget(attrs={'class': 'form-control'}),
            'subject': Select2Widget(attrs={'class': 'form-control'}),
            'weekdays': Select2Widget(attrs={'class': 'form-control'}),
            'lesson_time': forms.TimeInput(
                format='%H:%M',
                attrs={
                    'class': 'form-control',
                    'placeholder': 'HH:MM',
                    'type': 'time',
                    'id': 'LessonTimePicker',
                }
            ),
            'arrival_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'id': 'datePicker',
                }
            )
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add attributes to all fields


        for field_name, field in self.fields.items():
            if field_name not in ['lesson_time', 'select_student']:
                field.widget.attrs.update({
                    "class": "form-control",  # Add Bootstrap class
                    "placeholder": ' ',  # Optional: Use label as placeholder
                })