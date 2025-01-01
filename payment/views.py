from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView

from .models import PaymentModel
from .forms import CreatePaymentForm, ConfirmPaymentForm
from students.models import Enrollment
from .helpers import calculate_payment_amount

class PaymentsListView(ListView):
    model = PaymentModel
    template_name = 'payment/payments_list.html'
    context_object_name = 'payments'

class CreatePaymentView(View):

    def get(self, request, student_id=None, course_id=None, enrollment_id=None):
        form = CreatePaymentForm()
        queryset = Enrollment.objects.all().filter(status=True)
        
        if student_id:
            queryset = queryset.filter(student=student_id)

        if course_id:
            queryset = queryset.filter(course=course_id)
        
        if enrollment_id:
            queryset = queryset.filter(id=enrollment_id)
            form.initial['enrollment'] = queryset.first()

        form.fields['enrollment'].queryset = queryset

        return render(request, 'payment/create_payment.html', {'form': form})

    def post(self, request, student_id=None, course_id=None, enrollment_id=None):
    
        form = CreatePaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=True)
            payment.amount = calculate_payment_amount(payment.enrollment, payment.lessons_covered)
            payment.save()
            return redirect('payment:view_payment', payment_id=payment.id)  
     
    
class ConfirmPaymentView(View):
    
    def get(self, request, payment_id):

        payment = get_object_or_404(PaymentModel, id=payment_id)
        form = ConfirmPaymentForm(instance=payment)

        return render(request, 'payment/view_payment.html', {'form': form})
    
    def post(self, request, payment_id):
        payment = get_object_or_404(PaymentModel, id=payment_id)

        if 'confirm' in request.POST:
            if not payment.status:
                print('confirmed')
                payment.status = True
                payment.save()
                payment.enrollment.add_balance(payment.amount)

        return redirect('payment:payments_list')