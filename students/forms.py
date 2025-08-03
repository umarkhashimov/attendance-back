from django.forms import ModelForm
from django import forms
from django.db.models import Q
from django_select2.forms import Select2Widget

from users.models import UsersModel
from .models import StudentModel, Enrollment
from courses.models import CourseModel

class StudentInfoForm(ModelForm):
    
    class Meta:
        model = StudentModel
        exclude = ['courses', 'archived']
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

            if field.required:
                field.widget.attrs.update({
                    'aria-required': 'True',
                })


class EnrollmentForm(ModelForm):
    
    student = forms.ModelChoiceField(
        queryset=StudentModel.objects.all(),
        widget=Select2Widget(),
    )

    class Meta:
        model = Enrollment
        fields = ['course', 'student', 'discount', 'trial_lesson']

class StudentEnrollmentForm(ModelForm):
    
    course = forms.ModelChoiceField(
        queryset=CourseModel.objects.all().exclude(archived=True),
        widget=Select2Widget(),
        label='Курс'
    )

    class Meta:
        model = Enrollment
        fields = ['course', 'discount', 'note', 'trial_lesson']
        widgets = {
            'trial_lesson': forms.CheckboxInput(
                attrs={
                'class': 'form-check-input',
            })
        }

    def __init__(self, *args, student=None, teacher=None, subject=None, weekdays=None, **kwargs):
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
            queryset = CourseModel.objects.all().exclude(Q(id__in=enrolled) | Q(archived=True))
            if teacher:
                queryset = queryset.filter(teacher_id=teacher)

            if subject:
                queryset = queryset.filter(subject=subject)

            if weekdays:
                if str(weekdays) == "1":
                    queryset = queryset.filter(weekdays__contains='0,2,4')
                elif str(weekdays) == "2":
                    queryset = queryset.filter(weekdays__contains='1,3,5')
                elif str(weekdays) == "3":
                    queryset = queryset.exclude(Q(weekdays__contains="0,2,4") | Q(weekdays__contains="1,3,5"))

            self.fields['course'].queryset = queryset


class CourseEnrollmentForm(ModelForm):
    
    student = forms.ModelChoiceField(
        queryset=StudentModel.objects.all(),
        widget=Select2Widget(),
        label='Студент'
    )

    class Meta:
        model = Enrollment
        fields = ['student',  'discount', 'note', 'debt_note', 'trial_lesson']
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

        if course:
            enrolled = Enrollment.objects.filter(course=course, status=True).values_list('student__id', flat=True)
            self.fields['student'].queryset = StudentModel.objects.all().exclude(id__in=enrolled)


class UpdateEnrollmentForm(forms.Form):
    discount = forms.IntegerField(min_value=0, max_value=100)
    # balance = forms.IntegerField(required=False)
    payment_due = forms.DateField(required=False)
    hold = forms.BooleanField(required=False)
    trial_lesson = forms.BooleanField(required=False)
    debt_note = forms.CharField(max_length=200, required=False)
    note = forms.CharField(max_length=200, required=False)


class ReEnrollmentForm(forms.Form):
    course = forms.ModelChoiceField(queryset=CourseModel.objects.exclude(Q(archived=True) | Q(status=False)),
                                    widget=Select2Widget(attrs={'class': 'form-control'}), label="Группа")

    def __init__(self, *args, student=None, teacher=None, weekdays=None, exclude_course=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = CourseModel.objects.all().exclude(Q(archived=True))

        if student:
            active_enrollments = Enrollment.objects.filter(student=student, status=True).values_list('course__id', flat=True)
            queryset = queryset.exclude(Q(archived=True)  | Q(id__in=active_enrollments))

        if teacher:
            queryset = queryset.filter(teacher_id=teacher)

        if weekdays:
            if weekdays == "1":
                queryset = queryset.filter(weekdays__contains='0,2,4')
            elif weekdays == "2":
                queryset = queryset.filter(weekdays__contains='1,3,5')
            elif weekdays == "3":
                queryset = queryset.exclude(Q(weekdays__contains="0,2,4") | Q(weekdays__contains="1,3,5"))

        if exclude_course:
            queryset = queryset.exclude(id=exclude_course)

        self.fields['course'].queryset = queryset


class ReEnrollmentFilterForm(forms.Form):
    weekdays = forms.ChoiceField(
        choices=[(1, "Нечетные"), (2, "Четные"), (3, "Другие")], label="Дни уроков",
        widget=Select2Widget(attrs={'class': 'form-control'}),
        required=False)

    teacher = forms.ModelChoiceField(queryset=UsersModel.objects.filter(role='1', is_active=True),
                                     widget=Select2Widget(attrs={'class': 'form-control'}),
                                     required=False, label="Учитель")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
