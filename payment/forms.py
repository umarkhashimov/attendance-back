from calendar import month
from django import forms
from django.shortcuts import get_object_or_404
from django_select2.forms import Select2Widget
import datetime

from users.models import UsersModel
from courses.models import CourseModel
from students.models import StudentModel
from .models import PaymentModel

class CreatePaymentForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    class Meta:
        model = PaymentModel
        fields = ['months', 'amount']

        widgets = {
            'months': Select2Widget(attrs={'class':'form-control mt-2'}),
            'amount': forms.NumberInput(attrs={'readonly':True}),
        }

class ConfirmPaymentForm(forms.ModelForm):
    class Meta:
        model = PaymentModel
        fields = ['enrollment', 'months', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set all fields to use a text widget for read-only display
        for field in self.fields.values():
            field.widget.attrs['readonly'] = True
            field.widget.attrs['class'] = 'readonly'  # Optional: for custom styling
            field.disabled = True

class PaymentHistoryFilterForm(forms.Form):
    teacher = forms.ModelChoiceField(queryset=UsersModel.objects.filter(role='1'), required=False, label="Учитель", widget=forms.Select(attrs={'class':'form-control mt-2', 'onchange': 'submit()'}))
    course = forms.ModelChoiceField(queryset=CourseModel.objects.all(), required=False, label="Курс", widget=forms.Select(attrs={'class':'form-control mt-2', 'onchange': 'submit()'}))
    student = forms.ModelChoiceField(queryset=StudentModel.objects.all(), required=False, label="Студет", widget=forms.Select(attrs={'class':'form-control mt-2', 'onchange': 'submit()'}))
    sort_by = forms.ChoiceField(choices=[(1, "Последние"),(2, "Ранние"),(3, "Удаленные"),(4, "Кол-во месяц")], required=False, label="Сортировать по", widget=forms.Select(attrs={'class':'form-control mt-2', 'onchange': 'submit()'}))
    payment_date_start = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'onchange': 'submit()', 'class': 'form-control', 'max':datetime.date.today()}), required=False, label="С")
    payment_date_end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'onchange': 'submit()', 'class': 'form-control', 'max':datetime.date.today()}), required=False, label="До")

    def __init__(self, teacher_id=None, course_id=None,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if teacher_id:
        #     self.fields['course'].queryset = CourseModel.objects.filter(teacher=teacher_id)
        #
        # if course_id:
        #     self.fields['student'].queryset = StudentModel.objects.filter(enrollment__course=course_id).distinct()
        #     # self.fields['teacher'].widget.attrs.update({'disabled': True})
        # elif teacher_id:
        #     self.fields['student'].queryset = StudentModel.objects.filter(enrollment__course__teacher=teacher_id).distinct()
        #

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

