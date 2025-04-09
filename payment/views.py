from calendar import month
from datetime import datetime, timedelta

from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import View, ListView, UpdateView

from courses.models import CourseModel
from users.filters import AdminRequired, SuperUserRequired
from users.helpers import record_action
from users.models import UsersModel
from .models import PaymentModel
from .forms import CreatePaymentForm, ConfirmPaymentForm, PaymentHistoryFilterForm, UpdatePaymentDatesForm
from students.models import Enrollment, StudentModel
from .helpers import calculate_payment_due_date, calculate_payment_amount, next_closest_session_date
from collections import defaultdict

class PaymentsListView(ListView):
    model = PaymentModel
    template_name = 'payment/payments_list.html'
    context_object_name = 'payments'
    ordering = ['-id']
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = self.request.GET.copy()
        teacher_id = data.get('teacher')
        course_id = data.get('course')
        student_id = data.get('student')

        context['filter_form'] = PaymentHistoryFilterForm(initial=data, teacher_id=teacher_id, course_id=course_id, student_id=student_id)
        context['queryset_length'] = self.get_queryset().count()
        return context

    def get_queryset(self):
        queryset = PaymentModel.objects.all()
        teacher = self.request.GET.get('teacher', None)
        course = self.request.GET.get('course', None)
        student_id = self.request.GET.get('student', None)
        sort_by = self.request.GET.get('sort_by', None)
        payment_date_start = self.request.GET.get('payment_date_start', None)
        payment_date_end = self.request.GET.get('payment_date_end', None)

        if student_id:
            queryset = queryset.filter(enrollment__student_id=student_id)

            if course:
                courses = CourseModel.objects.filter(enrollment__student_id=student_id).values_list('id', flat=True)
                if str(course) in str(courses):
                    queryset = queryset.filter(enrollment__course=course)

        if course and not student_id:
            queryset = queryset.filter(enrollment__course=course)
            if teacher:
                course = get_object_or_404(CourseModel, id=course)
                if course.teacher.id == teacher:
                    queryset = queryset.filter(enrollment__course__teacher=teacher)

        if teacher and not course:
            queryset = queryset.filter(enrollment__course__teacher=teacher)

        if payment_date_start:
            queryset = queryset.filter(date__gt=payment_date_start)

        if payment_date_end:
            end_date = datetime.strptime(payment_date_end, '%Y-%m-%d')
            queryset = queryset.filter(date__lte=end_date+timedelta(days=1))

        if sort_by:
            if sort_by == '1':
                queryset = queryset.order_by('-id')
            elif sort_by == '2':
                queryset = queryset.order_by('id')
            elif sort_by == '3':
                queryset = queryset.filter(enrollment__status=False).order_by('-id')
            elif sort_by == '4':
                queryset = queryset.order_by('-months')
        else:
            queryset = queryset.order_by('-id')

        return queryset


class CreatePaymentView(View):

    def post(self, request, enrollment_id):
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        form = CreatePaymentForm(request.POST)
        if form.is_valid():
            last_payment_due = PaymentModel.objects.filter(enrollment=enrollment).order_by('-date').first()
            payment = PaymentModel.objects.create(enrollment=enrollment, months=form.cleaned_data['months'])
            payment.amount = calculate_payment_amount(enrollment, payment.months)

            if form.cleaned_data['start_date']:
                payment.payed_from = form.cleaned_data['start_date']
            elif payment.enrollment.payment_due:
                payment.payed_from = next_closest_session_date(course=enrollment.course, today= payment.enrollment.payment_due) if payment.enrollment.payment_due else datetime.now().date()
            else:
                payment.payed_from = next_closest_session_date(course=enrollment.course)


            if form.cleaned_data['end_date']:
                payment.payed_due = form.cleaned_data['end_date']
            else:
                payment.payed_due = calculate_payment_due_date(enrollment, 12 * payment.months, payment.payed_from)

            payment.save()

            if payment.enrollment.payment_due:
                if payment.payed_due > payment.enrollment.payment_due:
                    payment.enrollment.payment_due = payment.payed_due
                    payment.enrollment.save()

            else:
                payment.enrollment.payment_due = payment.payed_due
                payment.enrollment.save()

            action_message = f"Оплата ученика <b>{payment.enrollment.student}</b> в группу <b>{payment.enrollment.course}</b>"
            record_action(1, self.request.user, payment, payment.id, action_message)

        next_url = self.request.GET.get('next', '/')
        return redirect(next_url)

class DebtPaymentsListView(View, AdminRequired):
    template_name = 'payment/debt_payments_list.html'

    def get(self, request):
        teachers = UsersModel.objects.filter(role='1').distinct()

        teacher_enrollments = {}

        for teacher in teachers:
            courses = CourseModel.objects.filter(teacher=teacher, enrollment__payment_due__lt=datetime.today().date(), enrollment__status=True).distinct().order_by('weekdays', 'lesson_time')
            if len(courses) > 0:
                teacher_enrollments[teacher] = {
                    course: list(Enrollment.objects.filter(course=course, payment_due__lt=datetime.today().date(), status=True))
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

class UpdatePaymentDatesView(SuperUserRequired, UpdateView):
    model = PaymentModel
    form_class = UpdatePaymentDatesForm
    template_name = 'payment/update_dates.html'

    def form_valid(self, form):
        # Perform any custom actions before saving
        instance = form.save(commit=False)

        instance.payed_due = calculate_payment_due_date(instance.enrollment, iterate_balance=instance.current_balance if instance.current_balance else None, count_from=instance.payed_from)
        # Save the instance
        instance.save()

        return super().form_valid(form)

    def get_success_url(self):
        return  reverse('students:student_update', kwargs={'pk': self.object.enrollment.student.id})