from django import forms
from .models import PaymentModel
from students.forms import EnrollmentForm
from students.models import Enrollment

class CreatePaymentForm(forms.ModelForm):
    class Meta:
        model = PaymentModel
        fields = ['enrollment', 'lessons_covered'] 

        widgets = {
        'lessons_covered':  forms.NumberInput(
            attrs={
                'oninput': 'this.value = this.value.replace(/[^0-9]/g, '');',
                'placeholder': 'Кол-во занатий',
            }
        ),
    }
        

class ConfirmPaymentForm(forms.ModelForm):
    class Meta:
        model = PaymentModel
        fields = ['enrollment', 'lessons_covered', 'amount', 'status'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set all fields to use a text widget for read-only display
        for field in self.fields.values():
            field.widget.attrs['readonly'] = True
            field.widget.attrs['class'] = 'readonly'  # Optional: for custom styling
            field.disabled = True