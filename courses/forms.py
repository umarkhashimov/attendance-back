from django import forms
from .models import CourseModel, WEEKDAY_CHOICES, SessionsModel, SubjectModel
from django_select2.forms import Select2Widget, Select2MultipleWidget
from multiselectfield import MultiSelectField
from users.models import UsersModel

class CourseUpdateForm(forms.ModelForm):

    subject = forms.ModelChoiceField(
        queryset=SubjectModel.objects.all(),
        widget=Select2Widget(attrs={'class':' w-100'}),
        label="Курс"
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
            'subject': Select2Widget(attrs={'class':'form-control'}),
            'teacher': Select2Widget(attrs={'class':'form-control'}),
            'course_name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Введите имя курса'}),
            'weekdays': Select2MultipleWidget(attrs={'class':'form-control multiplechoices'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add attributes to all fields
        for field_name, field in self.fields.items():
            if field_name in ['weekdays', 'status']:
                continue
            field.widget.attrs.update({
                "class": "form-control",  # Add Bootstrap class
                "placeholder": ' ',  # Optional: Use label as placeholder
            })


class CourseCreateForm(forms.ModelForm):

    weekdays = MultiSelectField(choices=WEEKDAY_CHOICES)
    days = forms.ChoiceField(
        choices=[(1, "Нечетные"), (2, "Четные"), (3, "Другие")], label="Дни уроков",
        widget=forms.Select(attrs={'class':'form-control', 'onchange': 'setMultipleWeekdays(this)'}),
        required=False)

    subject = forms.ModelChoiceField(
        queryset=SubjectModel.objects.all(),
        widget=Select2Widget(attrs={'class': ' w-100'}),
        label="Курс"
    )


    class Meta:
        model = CourseModel
        fields = ['subject', 'course_name', 'teacher', 'days', 'weekdays', 'lesson_time', 'duration', 'session_cost', 'last_topic', 'status']
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
            'subject': Select2Widget(attrs={'class': 'form-control'}),
            'teacher': Select2Widget(attrs={'class': 'form-control'}),
            'course_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя курса'}),
            'weekdays': Select2MultipleWidget(attrs={'class': 'form-control multiplechoices w-100'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add attributes to all fields
        self.fields['weekdays'].initial = ['0']
        self.fields['weekdays'].required = False
        for field_name, field in self.fields.items():
            if field_name in ['weekdays', 'status']:
                continue
            field.widget.attrs.update({
                "class": "form-control",  # Add Bootstrap class
                "placeholder": ' ',  # Optional: Use label as placeholder
            })

class CancelCauseForm(forms.Form):
    CAUSE_OPTIONS = [
        ("1", 'Праздник'),
        ("2", 'Другая причина')
    ]

    cause = forms.ChoiceField(choices=CAUSE_OPTIONS, widget=forms.RadioSelect, label="", initial='1')


class DaysMultiselectForm(forms.Form):
    weekdays = forms.MultipleChoiceField(
        choices = WEEKDAY_CHOICES,
        widget=forms.SelectMultiple(attrs={"id": "id_soft_skills", 'class':'form-select border border-3 border-danger w-100', 'onchange':'submit()'}),
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

