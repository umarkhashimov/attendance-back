from django import forms
from .models import CourseModel

class CourseUpdateForm(forms.ModelForm):

    class Meta:
        model = CourseModel
        fields = "__all__"
        exclude = ['is_started', 'weekdays', 'total_lessons', 'finished', 'start_date']
        widgets = {
            'lesson_time': forms.TimeInput(
                format='%H:%M', 
                attrs={
                    'class': 'form-control',  
                    'placeholder': 'HH:MM',
                    'type': 'time', 
                    'id': 'LessonTimePicker',
                }
            )
        }


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


class LessonsWeekdaysForm(forms.ModelForm):

    class Meta:
        model = CourseModel
        fields = ["weekdays"]
        



class CourseCreateForm(forms.ModelForm):

    class Meta:
        model = CourseModel
        fields = "__all__"
        exclude = ['is_started', 'finished']
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
            'start_date': forms.DateInput(
                attrs={
                    'class': 'form-control', 
                    'type': 'date', 
                    'id': 'StartDatePicker',
                    'placeholder': 'день.месяц.год'
                }
            ),
            'duration':  forms.NumberInput(
                attrs={
                    'oninput': 'this.value = this.value.replace(/[^0-9]/g, '');',
                    'placeholder': 'Длительность занятий',
                }
            ),
            'total_lessons': forms.NumberInput(
                attrs={
                    'oninput': 'this.value = this.value.replace(/[^0-9]/g, '');',
                    'placeholder': 'Сколько уроков',
                }
            ),
            'session_cost': forms.NumberInput(
                attrs={
                    'oninput': 'this.value = this.value.replace(/[^0-9]/g, '');',
                    'placeholder': 'Стоимость одного урока ?',
                }
            )
        }