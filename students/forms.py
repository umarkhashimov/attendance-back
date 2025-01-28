from django.forms import ModelForm
from django import forms
from django_select2.forms import Select2Widget
from .models import StudentModel, Enrollment

class StudentInfoForm(ModelForm):
    
    class Meta:
        model = StudentModel
        exclude = ['courses']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': '2'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add attributes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "form-control",  # Add Bootstrap class
                "placeholder": ' ',  # Optional: Use label as placeholder
            })


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

