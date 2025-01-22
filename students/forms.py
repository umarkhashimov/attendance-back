from django.forms import ModelForm

from .models import StudentModel, Enrollment

class StudentInfoForm(ModelForm):
    
    class Meta:
        model = StudentModel
        exclude = ['courses']


class EnrollmentForm(ModelForm):
    
    class Meta:
        model = Enrollment
        fields = ['course', 'student', 'balance', 'discount', 'trial_lesson']


class UpdateEnrollmentForm(ModelForm):
    
    class Meta:
        model = Enrollment
        fields = ['balance', 'discount', 'hold', 'trial_lesson', 'status']

