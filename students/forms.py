from django.forms import ModelForm
from django import forms
from django_select2.forms import Select2Widget
from .models import StudentModel, Enrollment

class StudentInfoForm(ModelForm):
    
    class Meta:
        model = StudentModel
        exclude = ['courses']


class EnrollmentForm(ModelForm):
    
    student = forms.ModelChoiceField(
        queryset=StudentModel.objects.all(),
        widget=Select2Widget(),
    )

    class Meta:
        model = Enrollment
        fields = ['course', 'student', 'balance', 'discount', 'trial_lesson']


class UpdateEnrollmentForm(ModelForm):
    

    class Meta:
        model = Enrollment
        fields = ['balance', 'discount', 'hold', 'trial_lesson', 'status']

