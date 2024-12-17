from django.forms import ModelForm

from .models import StudentModel

class StudentInfoForm(ModelForm):
    
    class Meta:
        model = StudentModel
        exclude = ['courses']