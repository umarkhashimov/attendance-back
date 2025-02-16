# forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from .models import UsersModel

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control border-3'}),
        label=_("Имя пользователя")
    )
    password = forms.CharField(
        label=_("Пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control border-3'}),
    )

    # Optional: Add custom validation, error messages, etc.
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                _("This account is inactive."),
                code='inactive',
            )


class TeacherUpdateForm(forms.ModelForm):

    class Meta:
        model = UsersModel
        # fields = "__all__"
        fields = ['first_name', 'last_name', 'phone_number']
        # exclude = ['password', 'last_login']'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add attributes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "form-control",  # Add Bootstrap class
                "placeholder": ' ',  # Optional: Use label as placeholder
            })

class TeacherSelectForm(forms.Form):
    teacher = forms.ModelChoiceField(
        queryset=UsersModel.objects.all().filter(role='1'),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder':'...', 'onchange':'submit()'}),
        label="Учитель"
    )