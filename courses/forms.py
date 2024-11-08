from django import forms
from .models import CourseModel

class CourseUpdateForm(forms.ModelForm):

    class Meta:
        model = CourseModel
        fields = "__all__"
        exclude = ['is_started']