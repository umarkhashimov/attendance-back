from calendar import month
from datetime import datetime, timedelta, time, timezone

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import View, ListView, UpdateView
from django.db.models import Q
from courses.models import CourseModel
from users.filters import AdminRequired, SuperUserRequired
from users.helpers import record_action
from users.models import UsersModel
from .models import PaymentModel
from .forms import CreatePaymentForm, PaymentHistoryFilterForm, UpdatePaymentDatesForm, TrialStudentsFilterForm
from students.models import Enrollment, StudentModel
from .helpers import calculate_payment_due_date, calculate_payment_amount, next_closest_session_date
from collections import defaultdict
from django.urls import reverse
from urllib.parse import urlencode
import traceback

class PaymentsListView(AdminRequired, ListView):
    model = PaymentModel
    template_name = 'payment/payments_list.html'
    context_object_name = 'payments'
    ordering = ['-id']
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        # If no filters provided, but session has saved filters — redirect with them
        if not request.GET and request.session.get("payments_filters"):
            return redirect(f"{reverse('payment:payments_list')}?{urlencode(request.session['payments_filters'])}")

        # If GET has filters, store them
        if request.GET:
            request.session["payments_filters"] = request.GET.dict()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = self.request.GET.copy()
        teacher_id = data.get('teacher')
        course_id = data.get('course')
        student_id = data.get('student')

        context['filter_form'] = PaymentHistoryFilterForm(initial=data, teacher_id=teacher_id, course_id=course_id, student_id=student_id)
        context['queryset_length'] = self.get_queryset().count()
        context['today'] = datetime.now().date()
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


class CreatePaymentView(AdminRequired, View):
    def post(self, request, enrollment_id):
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        form = CreatePaymentForm(request.POST)
        next_url = request.GET.get('next', '/')

        if self.request.user.is_superuser or 'create_payment' in request.user.custom_permissions:
            if form.is_valid():

                months = form.cleaned_data['months']
                auto_date = form.cleaned_data['automatic_date']
                start_date = form.cleaned_data.get('start_date')
                end_date = form.cleaned_data.get('end_date')
                lessons_count = form.cleaned_data.get('lessons_count')
                payment_type = form.cleaned_data.get('payment_type')

                try:
                    payment = PaymentModel.objects.create(enrollment=enrollment, months=months, payment_type=payment_type)

                    payed_lessons = 0
                    if int(months) == 0:
                        if int(lessons_count) > 0:
                            payed_lessons = int(lessons_count)
                    else:
                        payed_lessons = 12 * int(months)

                    payment.payed_lessons = payed_lessons
                    payment.amount = calculate_payment_amount(enrollment, payed_lessons)


                    # Determine payed_from and payed_due
                    if auto_date:
                        base_date = enrollment.payment_due if enrollment.payment_due else datetime.today().date()
                        payment.payed_from = next_closest_session_date(course=enrollment.course, today=base_date, include_today=True if not enrollment.payment_due else False)
                        payment.payed_due = calculate_payment_due_date(enrollment, payed_lessons, payment.payed_from)
                    else:
                        payment.payed_from = start_date if start_date else datetime.today()
                        payment.payed_due = end_date or calculate_payment_due_date(enrollment, payed_lessons, payment.payed_from)
                        payment.manual_dates = True

                    payment.save()

                    # Update enrollment's payment_due if necessary
                    if enrollment.payment_due is None:
                            enrollment.payment_due = payment.payed_due
                    else:
                        if enrollment.payment_due < payment.payed_due:
                            enrollment.payment_due = payment.payed_due

                    enrollment.save()

                    # Record action
                    action_message = f"Оплата ученика <b>{payment.enrollment.student}</b> в группу <b>{payment.enrollment.course}</b>"
                    record_action(1, request.user, payment, payment.id, action_message)

                    messages.success(request, "Оплата успешно добавлена.")
                except Exception as e:
                    messages.error(request, "Что-то пошло не так.")
                    traceback.print_exc()

            else:
                messages.success(request, "Ошибка в форме")
        else:
            messages.warning(request, 'У вас не доступа к этой функции')

        return redirect(next_url)


class DebtPaymentsListView(AdminRequired, View):
    template_name = 'payment/debt_payments_list.html'

    def get(self, request):
        # If no filters provided, but session has saved filters — redirect with them
        if not request.GET and request.session.get("debts_filters"):
            return redirect(f"{reverse('payment:debt_payments_list')}?{urlencode(request.session['debts_filters'])}")

        # If GET has filters, store them
        if request.GET:
            request.session["debts_filters"] = request.GET.dict()


        teachers = UsersModel.objects.filter(role='1').distinct()
        # Filters
        weekdays = self.request.GET.get('weekdays', None)

        enrollments = Enrollment.objects.select_related('course__teacher').filter(Q(payment_due__lt=datetime.today().date()) | Q(payment_due__isnull=True), status=True).order_by('course__teacher__first_name', 'course__teacher__last_name','course__lesson_time', 'student__first_name', 'student__last_name')

        if weekdays:
            if weekdays == '1':
                enrollments = enrollments.filter(course__weekdays__contains='0,2,4')
            elif weekdays == '2':
                enrollments = enrollments.filter(course__weekdays__contains='1,3,5')
            else:
                enrollments = enrollments.exclude(
                    Q(course__weekdays__contains='0,2,4') | Q(course__weekdays__contains='1,3,5'))

        course_enrollment_map = defaultdict(list)
        for enrollment in enrollments:
            course = enrollment.course
            course_enrollment_map[course].append(enrollment)

        teacher_data = defaultdict(lambda: defaultdict(list))
        for course, enrollment_list in course_enrollment_map.items():
            teacher = course.teacher
            teacher_data[teacher][course] = enrollment_list

        teacher_data = {
            teacher: dict(course_map)
            for teacher, course_map in teacher_data.items()
        }

        context = {'teacher_enrollments': teacher_data}
        context['filter_form'] = TrialStudentsFilterForm(initial=self.request.GET)
        return render(request, self.template_name, context)

class TrialEnrollmentsView(AdminRequired, View):
    template_name = 'payment/trial_students_list.html'

    def get(self, request):
        # If no filters provided, but session has saved filters — redirect with them
        if not request.GET and request.session.get("trials_filters"):
            return redirect(f"{reverse('payment:trial_enrollments_list')}?{urlencode(request.session['trials_filters'])}")

        # If GET has filters, store them
        if request.GET:
            request.session["trials_filters"] = request.GET.dict()

        teachers = UsersModel.objects.filter(role='1').distinct()

        # Filters
        weekdays = self.request.GET.get('weekdays', None)

        enrollments = Enrollment.objects.select_related('course__teacher').filter(trial_lesson=True, status=True).order_by('course__teacher__first_name', 'course__teacher__last_name','course__lesson_time', 'student__first_name', 'student__last_name')

        if weekdays:
            if weekdays == '1':
                enrollments = enrollments.filter(course__weekdays__contains='0,2,4')
            elif weekdays == '2':
                enrollments = enrollments.filter(course__weekdays__contains='1,3,5')
            else:
                enrollments = enrollments.exclude(Q(course__weekdays__contains='0,2,4') | Q(course__weekdays__contains='1,3,5'))


        course_enrollment_map = defaultdict(list)
        for enrollment in enrollments:
            course = enrollment.course
            course_enrollment_map[course].append(enrollment)

        teacher_data = defaultdict(lambda: defaultdict(list))
        for course, enrollment_list in course_enrollment_map.items():
            teacher = course.teacher
            teacher_data[teacher][course] = enrollment_list

        teacher_data = {
            teacher: dict(course_map)
            for teacher, course_map in teacher_data.items()
        }

        context = {'teacher_enrollments':teacher_data}
        context['filter_form'] = TrialStudentsFilterForm(initial=self.request.GET)
        return render(request, self.template_name, context)

class UpdatePaymentDatesView(SuperUserRequired, UpdateView):
    model = PaymentModel
    form_class = UpdatePaymentDatesForm
    template_name = 'payment/update_dates.html'

    def form_valid(self, form):
        instance = form.save(commit=False)
        if form.cleaned_data['manual_due_date']:
            instance.payed_due = calculate_payment_due_date(instance.enrollment, count_from=instance.payed_from, iterate_balance=instance.enrollment.balance)
        else:
            instance.payed_due = instance.payed_due
        instance.date = datetime.combine(form.cleaned_data['factual_date'].date(), datetime.now().time())
        instance.save()

        return super().form_valid(form)

    def get_success_url(self):
        return  reverse('students:student_update', kwargs={'pk': self.object.enrollment.student.id})
