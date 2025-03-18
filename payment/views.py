from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView

from courses.models import CourseModel
from users.filters import AdminRequired
from users.models import UsersModel
from .models import PaymentModel
from .forms import CreatePaymentForm, ConfirmPaymentForm
from students.models import Enrollment
from .helpers import calculate_payment_due_date, calculate_payment_amount, next_closest_session_date
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
            date = next_closest_session_date(course=enrollment.course)
            last_payment_due = PaymentModel.objects.filter(enrollment=enrollment).order_by('-date').first()
            payment = PaymentModel.objects.create(enrollment=enrollment, months=form.cleaned_data['months'])
            payment.amount = calculate_payment_amount(enrollment, payment.months)

            if form.cleaned_data['start_date']:
                payment.payed_from = form.cleaned_data['start_date']
            elif last_payment_due:
                payment.payed_from = next_closest_session_date(course=enrollment.course, today=last_payment_due.payed_due) if last_payment_due.payed_due else datetime.now().date()
            else:
                payment.payed_from = next_closest_session_date(course=enrollment.course)

            payment.enrollment.add_balance(payment.months * 12)

            if form.cleaned_data['end_date']:
                payment.payed_due = form.cleaned_data['end_date']
            else:
                payment.payed_due = calculate_payment_due_date(enrollment)

            payment.save()

        next_url = self.request.GET.get('next', '/')
        print(next_url)
        return redirect(next_url)

class DebtPaymentsListView(View, AdminRequired):
    template_name = 'payment/debt_payments_list.html'

    def get(self, request):
        teachers = UsersModel.objects.filter(role='1').distinct()

        teacher_enrollments = {}

        for teacher in teachers:
            courses = CourseModel.objects.filter(teacher=teacher, enrollment__balance__lte=0, enrollment__status=True).distinct().order_by('weekdays', 'lesson_time')
            if len(courses) > 0:
                teacher_enrollments[teacher] = {
                    course: list(Enrollment.objects.filter(course=course, balance__lte=0, status=True))
                    for course in courses
                }

        context = {'teacher_enrollments': teacher_enrollments}
        return render(request, self.template_name, context)

class TrialEnrollmentsView(View, AdminRequired):
    template_name = 'payment/trial_students_list.html'

    def get(self, request):
        teachers = UsersModel.objects.filter(role='1').distinct()

        teacher_enrollments = {}

        for teacher in teachers:
            courses = CourseModel.objects.filter(teacher=teacher, enrollment__trial_lesson=True, enrollment__status=True).distinct().order_by('weekdays', 'lesson_time')
            if len(courses) > 0:
                teacher_enrollments[teacher] = {
                    course: list(Enrollment.objects.filter(course=course, trial_lesson=True, status=True))
                    for course in courses
                }

        context = {'teacher_enrollments': teacher_enrollments}
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