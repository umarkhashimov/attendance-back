from django import forms
from .models import CourseModel

class CourseUpdateForm(forms.ModelForm):

    class Meta:
        model = CourseModel
        fields = "__all__"
        exclude = ['is_started', 'weekdays', 'total_lessons', 'finished', 'start_date', 'lesson_time']


class LessonTimeForm(forms.ModelForm):

    class Meta:
        model = CourseModel
        fields = ["lesson_time"]
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