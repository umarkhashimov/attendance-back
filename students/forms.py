from django.forms import ModelForm
from django import forms
from django_select2.forms import Select2Widget
from .models import StudentModel, Enrollment
from courses.models import CourseModel

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

class StudentEnrollmentForm(ModelForm):
    
    course = forms.ModelChoiceField(
        queryset=CourseModel.objects.all(),
        widget=Select2Widget(),
    )

    class Meta:
        model = Enrollment
        fields = ['course', 'balance', 'discount', 'trial_lesson']
        widgets = {
            'trial_lesson': forms.CheckboxInput(
                attrs={
                'class': 'form-check-input',
            })
        }

    def __init__(self, *args, student=None, course=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Add attributes to all fields
        for field_name, field in self.fields.items():
            if field_name in ['trial_lesson']:
                continue
            field.widget.attrs.update({
                "class": "form-control",  # Add Bootstrap class
                "placeholder": ' ',  # Optional: Use label as placeholder
            })

        if student:
            enrolled = Enrollment.objects.filter(student=student, status=True).values_list('course__id', flat=True)
            self.fields['course'].queryset = CourseModel.objects.all().exclude(id__in=enrolled)


class UpdateEnrollmentForm(ModelForm):
    

    class Meta:
        model = Enrollment
        fields = ['balance', 'discount', 'hold', 'trial_lesson', 'status']

