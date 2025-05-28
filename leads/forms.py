from django import forms
from django_select2.forms import Select2Widget
from .models import LeadsModel
from students.models import StudentModel

class LeadForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=StudentModel.objects.all(),
                                     widget=Select2Widget(attrs={'class': 'form-control'}),required=False, label='Выберите ученика')
    select_student = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'onclick': 'toggleStudentInputType(this)'}), label='Создать нового ученика', initial=True)

    class Meta:
        model = LeadsModel
        fields = ['weekdays', 'lesson_time', 'teacher', 'arrival_date', 'note']
        widgets = {
            'teacher': Select2Widget(attrs={'class': 'form-control'}),
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

        if self.fields['select_student'].initial:
            self.fields['student'].required = True

        for field_name, field in self.fields.items():
            if field_name not in ['lesson_time', 'select_student']:
                field.widget.attrs.update({
                    "class": "form-control",  # Add Bootstrap class
                    "placeholder": ' ',  # Optional: Use label as placeholder
                })

