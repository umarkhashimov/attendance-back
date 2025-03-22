from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView

from courses.models import CourseModel
from users.filters import AdminRequired
from users.models import UsersModel
from .models import PaymentModel
from .forms import CreatePaymentForm, ConfirmPaymentForm, PaymentHistoryFilterForm
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

        # payment_date_start = data.get('payment_date_start')
        # payment_date_end = data.get('payment_date_end')
        # print((payment_date_start, payment_date_end))
        # # if payment_date_start and payment_date_end:
        # #     payment_date_start =  datetime.strptime(data['payment_date_start'], '%Y-%m-%d')
        # #     payment_date_end = datetime.strptime(data['payment_date_end'], '%Y-%m-%d')
        # #     print("worked")
        # #     if payment_date_start > payment_date_end:
        # #         print('comparing')
        # #
        # #         data['payment_date_end'] = data.get('payment_date_start')

        context['filter_form'] = PaymentHistoryFilterForm(initial=data, teacher_id=teacher_id, course_id=course_id)
        context['queryset_length'] = self.get_queryset().count()
        return context

    def get_queryset(self):
        queryset = PaymentModel.objects.all()
        teacher = self.request.GET.get('teacher', None)
        course = self.request.GET.get('course', None)
        student_id = self.request.GET.get('student', None)
        payment_date_start = self.request.GET.get('payment_date_start', None)
        payment_date_end = self.request.GET.get('payment_date_end', None)

        if teacher:
            queryset = queryset.filter(enrollment__course__teacher=teacher)

            if course:
                teacher_courses = CourseModel.objects.filter(teacher=teacher).values_list('id', flat=True)
                if str(course) in str(teacher_courses):
                    queryset = queryset.filter(enrollment__course=course)

            if student_id:
                teacher_students = StudentModel.objects.filter(enrollment__course__teacher=teacher).distinct().values_list('id', flat=True)
                if str(student_id) in str(teacher_students):
                    queryset = queryset.filter(enrollment__student_id=student_id)


        if course:
            courses_teacher = CourseModel.objects.filter(id=course).values_list('teacher_id', flat=True)
            if str(teacher) in str(courses_teacher):
                queryset = queryset.filter(enrollment__course=course)

        if student_id and not teacher:
            # student = StudentModel.objects.filter(id=student_id)
            # print(student, student_id)
            # course_students = CourseModel.objects.filter(enrollment__student_id=student).distinct()
            # print('>>>', course_students)
            # if str(student) in str(course_students):
            #     print(('yes'))
            #     queryset = queryset.filter(enrollment__course__student=student)
            # if course:
            #     student_courses = CourseModel.objects.filter(id=course).distinct().values_list('enrollment__student_id', flat=True)
            #     if str(student_id) in str(student_courses):
            #         queryset = queryset.filter(enrollment__student_id=student_id)
            # elif teacher:
            #     student_teachers = CourseModel.objects.filter(teacher=teacher).distinct().values_list('enrollment__student_id', flat=True)
            #     if str(student_id) in str(student_teachers):
            #         queryset = queryset.filter(enrollment__student_id=student_id)
            # else:
            queryset = queryset.filter(enrollment__student=student_id)

        if payment_date_start:
            queryset = queryset.filter(date__gt=payment_date_start)

        if payment_date_end:
            end_date = datetime.strptime(payment_date_end, '%Y-%m-%d')
            queryset = queryset.filter(date__lte=end_date+timedelta(days=1))

        return queryset.order_by('-id')


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