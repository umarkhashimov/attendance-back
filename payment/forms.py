from django import forms
from django_select2.forms import Select2Widget
import datetime

from users.models import UsersModel
from courses.models import CourseModel
from students.models import StudentModel
from .models import PaymentModel

class CreatePaymentForm(forms.ModelForm):
    MONTHS_CHOICES = [
        (0, "Поурочно"),
        (1, "1 Месяц"),
        (2, "2 Месяца"),
        (3, "3 Месяца"),
        (4, "4 Месяца"),
        (5, "5 Месяца"),
        (6, "6 Месяца"),
        (7, "7 Месяца"),
        (8, "8 Месяца"),
        (9, "9 Месяца"),
        (10, "10 Месяца"),
        (11, "11 Месяца"),
        (12, "12 Месяца"),
    ]
    months = forms.ChoiceField(choices=MONTHS_CHOICES, label="Оплатить за", widget=forms.Select(attrs={'class': 'form-control'}))
    lessons_count = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control', 'hidden':'', 'oninput': "customLessonsOninput(this)"}), label='Кол-во уроков',required=False)
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    automatic_date = forms.BooleanField(widget=forms.CheckboxInput(attrs={'type': 'checkbox'}), required=False)

    class Meta:
        model = PaymentModel
        fields = ['months', 'amount', 'payment_type']

        widgets = {
            'months': forms.Select(attrs={'class':'form-control ordinary mt-2'}),
            'amount': forms.NumberInput(attrs={'readonly':True}),
            'payment_type': forms.Select(attrs={'class':'form-select ordinary mt-2'}),
        }


class PaymentHistoryFilterForm(forms.Form):
    teacher = forms.ModelChoiceField(queryset=UsersModel.objects.filter(role='1', is_active=True), required=False, label="Учитель", widget=Select2Widget(attrs={'class':'form-control mt-2', 'onchange': 'submit()'}))
    course = forms.ModelChoiceField(queryset=CourseModel.objects.all(), required=False, label="Курс", widget=Select2Widget(attrs={'class':'form-control mt-2', 'onchange': 'submit()'}))
    student = forms.ModelChoiceField(queryset=StudentModel.objects.all(), required=False, label="Студет", widget=Select2Widget(attrs={'class':'form-control mt-2', 'onchange': 'submit()'}))
    sort_by = forms.ChoiceField(choices=[(1, "Последние"),(2, "Ранние"),(3, "Удаленные"),(4, "Кол-во месяц")], required=False, label="Сортировать по", widget=Select2Widget(attrs={'class':'form-control mt-2', 'onchange': 'submit()'}))
    payment_date_start = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'onchange': 'submit()', 'class': 'form-control', 'max':datetime.date.today()}), required=False, label="С")
    payment_date_end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'onchange': 'submit()', 'class': 'form-control', 'max':datetime.date.today()}), required=False, label="До")

    def __init__(self, teacher_id=None, course_id=None, student_id=None,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        if course_id:
            if teacher_id:
                course = CourseModel.objects.filter(id=course_id)
                if course and str(course.first().teacher.id) != str(teacher_id):
                    self.initial['teacher'] = None

        if teacher_id and not course_id:
            courses_by_teacher = CourseModel.objects.filter(teacher=teacher_id)
            self.fields['course'].queryset = courses_by_teacher

        if course_id and not student_id:
            students_by_courses = StudentModel.objects.filter(enrollment__course_id=course_id)
            self.fields['student'].queryset = students_by_courses

        start_date = self.initial.get("payment_date_start")
        end_date = self.initial.get("payment_date_end")

        if start_date:
            self.fields['payment_date_end'].widget.attrs.update({'min': start_date, 'max': datetime.date.today()})

            if end_date:
                payment_date_start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                payment_date_end = datetime.datetime.strptime(end_date, '%Y-%m-%d')

                if payment_date_end < payment_date_start:
                    self.initial['payment_date_end'] = datetime.date.today().strftime('%Y-%m-%d')
            else:
                self.initial['payment_date_end'] = datetime.date.today().strftime('%Y-%m-%d')

class UpdatePaymentDatesForm(forms.ModelForm):
    factual_date = forms.DateTimeField(widget=forms.DateInput(attrs={'type': 'date'}), required=False, label="Фактическая дата оплаты")
    manual_due_date = forms.BooleanField(widget=forms.CheckboxInput(attrs={'type': 'checkbox', 'onchange': 'custom_due_date_toggle(this)'}), required=False, label="Конец посчитать автоматически")

    class Meta:
        model = PaymentModel
        fields = ['payed_from', 'payed_due', 'manual_due_date', 'payment_type', 'factual_date', 'manual_due_date']
        widgets = {
            'payed_from': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'payed_due': forms.DateInput(attrs={'type': 'date',}, format='%Y-%m-%d'),
            'factual_date': forms.DateInput( format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and instance.date:
            self.fields['factual_date'].initial = instance.date.strftime('%Y-%m-%d')

class TrialStudentsFilterForm(forms.Form):
    weekdays = forms.ChoiceField(
        choices=[(1, "Нечетные"), (2, "Четные"), (3, "Другие")],
        widget=Select2Widget(attrs={'class': 'form-control', 'onchange': 'submit()'}),
        required=False, label="Дни"
    )
