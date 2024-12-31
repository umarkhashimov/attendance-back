from django.forms import ModelForm

from .models import StudentModel, Enrollment

class StudentInfoForm(ModelForm):
    
    class Meta:
        model = StudentModel
        exclude = ['courses']


class EnrollmentForm(ModelForm):
    
    class Meta:
        model = Enrollment
        fields = ['course', 'student', 'balance']

    