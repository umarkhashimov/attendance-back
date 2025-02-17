from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView

from users.filters import AdminRequired
from .models import PaymentModel
from .forms import CreatePaymentForm, ConfirmPaymentForm
from students.models import Enrollment
from .helpers import calculate_payment_amount
from collections import defaultdict

class PaymentsListView(ListView):
    model = PaymentModel
    template_name = 'payment/payments_list.html'
    context_object_name = 'payments'
    ordering = ['-id']
    paginate_by = 10

class CreatePaymentView(View):

    def get(self, request):
        return redirect('main:main')

    def post(self, request, enrollment_id):
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        form = CreatePaymentForm(request.POST)

        if form.is_valid():
            payment = PaymentModel.objects.create(enrollment=enrollment, months=form.cleaned_data['months'])
            payment.amount = calculate_payment_amount(enrollment, payment.months)
            payment.enrollment.add_balance(payment.months * 12)
            payment.save()

        next_url = self.request.GET.get('next', '/')
        print(next_url)
        return redirect(next_url)
        # form = CreatePaymentForm(request.POST)
        # if form.is_valid():
        #     payment = form.save(commit=True)
        #     payment.amount = calculate_payment_amount(payment.enrollment, payment.lessons_covered)
        #     payment.save()
        #     return redirect('payment:view_payment', payment_id=payment.id)

class DebtPaymentsListView(View, AdminRequired):
    template_name = 'payment/debt_payments_list.html'

    def get(self, request):
        enrollments = Enrollment.objects.filter(balance__lt=0).select_related('course__teacher')

        # Group enrollments by teacher
        enrollments_grouped = defaultdict(list)
        for enrollment in enrollments:
            teacher = enrollment.course.teacher
            enrollments_grouped[teacher].append(enrollment)

        context = {'enrollments_grouped': dict(enrollments_grouped)}
        return render(request, self.template_name, context)
    
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
                payment.enrollment.add_balance(payment.lessons_covered * 12)

        return redirect('payment:payments_list')