# forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django_select2.forms import Select2Widget
from django.contrib.auth.forms import UserChangeForm, SetPasswordForm
from django.contrib.admin.models import LogEntry, ContentType
from django.contrib.auth.forms import UserCreationForm
import datetime

from .filters import SuperUserRequired
from .models import UsersModel, ACTION_FLAG_CHOICES

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
        fields = ['first_name', 'last_name', 'phone_number', 'color']
        # exclude = ['password', 'last_login']'
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add attributes to all fields
        for field_name, field in self.fields.items():
            if field_name != 'color':
                field.widget.attrs.update({
                    "class": "form-control",  # Add Bootstrap class
                    "placeholder": ' ',  # Optional: Use label as placeholder
                })

class TeacherSelectForm(forms.Form):
    teacher = forms.ModelChoiceField(
        queryset=UsersModel.objects.all().filter(role='1'),
        widget=Select2Widget(attrs={'class': 'form-control', 'placeholder':'...', 'onchange':'submit()'}),
        label="Учитель"
    )


from config.settings import INSTALLED_APPS

class UserActionsFilterForm(forms.Form):
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.all().filter(app_label__in=INSTALLED_APPS),
        widget=Select2Widget(attrs={'class': 'form-control', 'placeholder':'...', 'onchange':'submit()'}),
        label="Тип Данных", required=False)

    user = forms.ModelChoiceField(
        queryset=UsersModel.objects.all().filter(role='2'),
        widget=Select2Widget(attrs={'class': 'form-control', 'placeholder':'...', 'onchange':'submit()'}),
        label="Администратор", required=False)

    action_type = forms.ChoiceField(
        choices=ACTION_FLAG_CHOICES,
        widget=Select2Widget(attrs={'class': 'form-control', 'placeholder':'...', 'onchange':'submit()'}),
        label="Действие", required=False)

    sort_by = forms.ChoiceField(
        choices=[(1, "Последние"), (2, "Ранние"), (3, "Администратор"), (4, "Действие")],
        widget=Select2Widget(attrs={'class': 'form-control mt-2', 'onchange': 'submit()'}),
        required=False, label="Сортировать по",)

    date_start = forms.DateField(
        widget=forms.DateInput(
        attrs={'type': 'date', 'onchange': 'submit()', 'class': 'form-control', 'max': datetime.date.today()}),
        required=False, label="С")

    date_end = forms.DateField(
        widget=forms.DateInput(
        attrs={'type': 'date', 'onchange': 'submit()', 'class': 'form-control', 'max': datetime.date.today()}),
        required=False, label="До")

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        start_date = self.initial.get("date_start")
        end_date = self.initial.get("date_end")

        if start_date:
            self.fields['date_end'].widget.attrs.update({'min': start_date, 'max': datetime.date.today()})

            if end_date:
                date_start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                date_end = datetime.datetime.strptime(end_date, '%Y-%m-%d')

                if date_end < date_start:
                    self.initial['date_end'] = datetime.date.today().strftime('%Y-%m-%d')
            else:
                self.initial['date_end'] = datetime.date.today().strftime('%Y-%m-%d')


class SalaryMonthFilterForm(forms.Form):
    month = forms.DateField(widget=forms.DateInput(attrs={'type': 'month', 'class': 'form-control', 'onchange': 'submit()', 'max': datetime.datetime.today().month}), required=False, label="Месяц")


class UserUpdateForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # take it out before super()
        super().__init__(*args, **kwargs)

        if 'password' in self.fields:
            del self.fields['password']

        if self.instance.pk == self.request.user.pk:
            del self.fields['is_active']

        for field_name, field in self.fields.items():
            if field_name not in ['is_active', 'role']:

                field.widget.attrs.update({
                    "class": "form-control",  # Add Bootstrap class
                    "placeholder": ' ',  # Optional: Use label as placeholder
                })

    class Meta:
        model = UsersModel
        fields = ['username', 'role', 'first_name', 'last_name', 'phone_number', 'is_active']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }


class UserSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "form-control",  # Add Bootstrap class
                "placeholder": ' ',  # Optional: Use label as placeholder
            })


class UsersListFilterForm(forms.Form):
    text = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'', 'onchange':'submit()'}), required=False, label="Имя/Фамилия/Пользователь")
    role = forms.ChoiceField(choices=[('1', 'Учитель'),('2', 'Администратор')], widget=Select2Widget(attrs={'class': 'form-control', 'placeholder':'...', 'onchange':'submit()'}), required=False, label="Роль")
    status = forms.ChoiceField(choices=[(True, 'Активный'), (False, 'Не активный')],widget=Select2Widget(attrs={'class': 'form-select d-inline', 'placeholder':'', 'onchange':'submit()'}), required=False, label="Статус")



class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = UsersModel
        fields = ['username', 'role', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "form-control",  # Add Bootstrap class
                "placeholder": ' ',  # Optional: Use label as placeholder
            })