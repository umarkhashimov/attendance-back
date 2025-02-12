from django import forms
from .models import CourseModel, WEEKDAY_CHOICES, SessionsModel, SubjectModel
from django_select2.forms import Select2Widget, Select2MultipleWidget
from multiselectfield import MultiSelectField

class CourseUpdateForm(forms.ModelForm):

    subject = forms.ModelChoiceField(
        queryset=SubjectModel.objects.all(),
        widget=Select2Widget(),
    )

    weekdays = MultiSelectField(choices=WEEKDAY_CHOICES)

    class Meta:
        model = CourseModel
        fields = "__all__"
        exclude = []
        widgets = {
            'lesson_time': forms.TimeInput(
                format='%H:%M', 
                attrs={
                    'class': 'form-control',  
                    'placeholder': 'HH:MM',
                    'type': 'time', 
                    'id': 'LessonTimePicker',
                }
            ),
            'subject': forms.ModelChoiceField(
                queryset=SubjectModel.objects.all(),
                widget=Select2Widget(attrs={'class':'form-control'}),
            ),
            'course_name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Введите имя курса'}),
            'weekdays': Select2MultipleWidget(attrs={'class':'form-control multiplechoices'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

        }

    def __init__(self, *args, student=None, course=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Add attributes to all fields
        for field_name, field in self.fields.items():
            if field_name in ['weekdays', 'status']:
                continue
            field.widget.attrs.update({
                "class": "form-control",  # Add Bootstrap class
                "placeholder": ' ',  # Optional: Use label as placeholder
            })


class LessonsWeekdaysForm(forms.ModelForm):
    weekdays = forms.MultipleChoiceField(
        choices=CourseModel.weekdays,
        widget=forms.CheckboxSelectMultiple,  # You can also use a `SelectMultiple` widget
        required=True,  # Ensure at least one option is selected
    )

    class Meta:
        model = CourseModel
        fields = ["weekdays"]

    def clean_multi_select_field(self):
        data = self.cleaned_data['weekdays']
        
        # Example validation: Ensure at least two options are selected
        if len(data) < 1:
            raise forms.ValidationError("Please select at least two options.")
        
        return data

        
class CourseCreateForm(forms.ModelForm):

    class Meta:
        model = CourseModel
        fields = "__all__"
        widgets = {
            'lesson_time': forms.TimeInput(
                format='%H:%M', 
                attrs={
                    'class': 'form-control',  
                    'placeholder': 'HH:MM',
                    'type': 'time', 
                    'id': 'LessonTimePicker',
                }
            ),
            'duration':  forms.NumberInput(
                attrs={
                    'oninput': 'this.value = this.value.replace(/[^0-9]/g, '');',
                    'placeholder': 'Длительность занятий',
                }
            ),
            'session_cost': forms.NumberInput(
                attrs={
                    'oninput': 'this.value = this.value.replace(/[^0-9]/g, '');',
                    'placeholder': '123',
                }
            )
        }

class CancelCauseForm(forms.Form):
    CAUSE_OPTIONS = [
        ("1", 'Праздник'),
        ("2", 'Другая причина')
    ]

    cause = forms.ChoiceField(choices=CAUSE_OPTIONS, widget=forms.RadioSelect, label="", initial='1')


class DaysMultiselectForm(forms.Form):
    weekdays = forms.MultipleChoiceField(
        choices = WEEKDAY_CHOICES,
        widget=Select2MultipleWidget(attrs={"id": "id_soft_skills", 'class':'form-select border border-3 border-danger w-100', 'onchange':'submit()'}),
        label=False, required=False
    )

class SessionTopicFieldForm(forms.ModelForm):

    class Meta:
        model = SessionsModel
        fields = ['topic']

        widgets = {
            'topic': forms.TextInput(
                attrs={
                    'class': 'border border-2 rounded-1 form-control',
                    'placeholder': '...',
                },

            )
        }

