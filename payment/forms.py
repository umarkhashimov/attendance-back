from calendar import month

from django import forms
from django_select2.forms import Select2Widget

from .models import PaymentModel

class CreatePaymentForm(forms.ModelForm):
    class Meta:
        model = PaymentModel
        fields = ['months', 'amount']

        widgets = {
            'months': Select2Widget(attrs={'class':'form-control mt-2'}),
            'amount': forms.NumberInput(attrs={'readonly':True}),
        }

class ConfirmPaymentForm(forms.ModelForm):
    class Meta:
        model = PaymentModel
        fields = ['enrollment', 'months', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set all fields to use a text widget for read-only display
        for field in self.fields.values():
            field.widget.attrs['readonly'] = True
            field.widget.attrs['class'] = 'readonly'  # Optional: for custom styling
            field.disabled = True