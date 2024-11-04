from django import forms
from .models import AttendanceModel

class AttendanceStatusForm(forms.ModelForm):
    class Meta:
        model = AttendanceModel
        fields = ['status'] 