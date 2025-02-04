from django import forms
from django_select2.forms import Select2Widget, Select2MultipleWidget, ModelSelect2Widget

from users.models import UsersModel 

class CoursesListFilterForm(forms.Form):
    teachers = forms.ModelChoiceField(
        queryset=UsersModel.objects.filter(role='1'),
        widget=Select2Widget(attrs={'class':'form-control'})
    )