from datetime import datetime

from django.views.generic import UpdateView, CreateView, View
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from collections import defaultdict
from django.forms.models import model_to_dict
from django.contrib import messages

from users.filters import AdminRequired
from users.forms import TeacherSelectForm
from users.helpers import record_action
from .models import StudentModel, Enrollment
from .forms import StudentInfoForm, ReEnrollmentForm, ReEnrollmentFilterForm
from courses.models import CourseModel
from payment.forms import CreatePaymentForm
from payment.models import PaymentModel
from .forms import EnrollmentForm, UpdateEnrollmentForm, StudentEnrollmentForm, CourseEnrollmentForm
from attendance.models import AttendanceModel
from payment.helpers import last_closest_session_date

class StudentUpdateView(AdminRequired, UpdateView):
    model = StudentModel
    template_name = 'student_update.html'
    form_class = StudentInfoForm

    def get_success_url(self):
        return self.request.path
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student"] = self.get_object()
        context["teacher_select_form"] = TeacherSelectForm(initial=self.request.GET)
        context['enrollment_update_form'] = UpdateEnrollmentForm
        context['enrollments'] = Enrollment.objects.all().filter(student=self.get_object(), status=True)
        context['enrollment_form'] = StudentEnrollmentForm(student=self.get_object(), teacher=self.request.GET.get('teacher', None))
        context['payment_form'] = CreatePaymentForm

        # Payment history
        enrolled = Enrollment.objects.filter(student=self.get_object())

        payments_grouped = defaultdict(list)
        for enrollment in enrolled:
            course = enrollment.course
            payments_grouped[course] = [payment for payment in PaymentModel.objects.filter(enrollment=enrollment).order_by('-date')]
        context['payments_grouped'] = dict(payments_grouped)


        # Student Attendance info
        attendance_grouped = defaultdict(list)
        for enrollment in enrolled:
            course = enrollment.course
            attendance_grouped[course] = AttendanceModel.objects.filter(enrollment=enrollment).order_by('-session__date').values('session__date', 'status', 'homework_grade', 'participation_grade' )
        context['attendance_grouped'] = dict(attendance_grouped)

        return context
    
    
class CreateStudentView(AdminRequired, CreateView):
    template_name = 'create_student.html'
    model = StudentModel
    form_class = StudentInfoForm
    exclude = ['courses']

    def get_success_url(self):
        action_message = f"Создал ученика: <b>{self.object.id} - {self.object.full_name}</b>"
        record_action(1, self.request.user, self.object, self.object.id, action_message)
        return reverse('students:student_update', kwargs={'pk': self.object.id})

class CreateEnrollmentView(AdminRequired, View):

    def post(self, request, course_id=None, student_id=None):
        form = EnrollmentForm(request.POST)
        if student_id:
            form = StudentEnrollmentForm(request.POST)

        if course_id:
            form = CourseEnrollmentForm(request.POST)

        if form.is_valid():
            course = CourseModel.objects.get(id=course_id) if course_id else None
            student = StudentModel.objects.get(id=student_id) if student_id else None
            
            enrollment, created = Enrollment.objects.update_or_create(
                course=course if course else form.cleaned_data['course'],
                student=student if student else form.cleaned_data['student'],
                defaults={**form.cleaned_data, 'status': True, 'enrolled_at':datetime.now(), 'payment_due': None},
            )

            if created:
                enrollment.enrolled_by = self.request.user

            enrollment.save()

            action_message = f"Записал ученика <b>{enrollment.student}</b> в группу <b>{enrollment.course}</b>"
            record_action(1, self.request.user, enrollment, enrollment.id, action_message)
            if course_id:
                return redirect('courses:course_update', pk=course_id)
            elif student_id:
                return redirect('students:student_update', pk=student_id)
            else:
                return redirect('main:main')

        return redirect('main:main')
    

class UpdateEnrollmentView(AdminRequired, View):

    def post(self, request, pk):
        enrollment = get_object_or_404(Enrollment, id=pk)
        form = UpdateEnrollmentForm(request.POST)
        if form.is_valid():
            enrollment, created = Enrollment.objects.update_or_create(
                course=enrollment.course,
                student=enrollment.student,
                defaults={**form.cleaned_data, 'payment_due':enrollment.payment_due},
            )

            enrollment.save()

        next_url  = self.request.GET.get('next', '/')
        return redirect(next_url + '#enrollmentsTable')

class DeactivateEnrollmentView(AdminRequired, View):
    def post(self, request, enrollment_id):
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        enrollment.trial_lesson = False
        enrollment.hold = False
        enrollment.payment_due = None
        enrollment.debt_note = None
        enrollment.status = False
        enrollment.save()
        action_message = f"Удалил ученика <b>{enrollment.student}</b> из группы <b>{enrollment.course}</b>"
        record_action(3, self.request.user, enrollment, enrollment.id, action_message)
        next_url  = self.request.GET.get('next', '/')
        return redirect(next_url)


class UpdateEnrollmentNote(AdminRequired, View):
    def post(self, request, pk):
        enrollment = get_object_or_404(Enrollment, id=pk)
        text = request.POST.get('text', None)
        enrollment.note = text.strip()
        enrollment.save()
        next_url = self.request.GET.get('next', '/')
        return redirect(next_url)

class ReEnrollStudentView(AdminRequired, View):

    def get(self, request, pk):
        enrollment = get_object_or_404(Enrollment, id=pk)
        weekdays = request.GET.get('weekdays', None)
        teacher = request.GET.get('teacher', None)

        context = {
            're_enrollment_form': ReEnrollmentForm(student=enrollment.student, teacher=teacher or None, weekdays=weekdays or None),
            'filter_form': ReEnrollmentFilterForm(request.GET),
            'enrollment': enrollment,
        }
        return render(request, 're_enrollment.html', context)

    def post(self, request, pk):
        form = ReEnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = get_object_or_404(Enrollment, id=pk)
            try:
                data = model_to_dict(enrollment)

                # Remove fields you want to set explicitly
                data.pop('id', None)
                data['course'] = form.cleaned_data['course']
                data['student'] = enrollment.student
                data['enrolled_by'] = enrollment.enrolled_by
                data['enrolled_at'] = datetime.now()

                new_enrollment, created = Enrollment.objects.update_or_create(
                    student=enrollment.student,
                    course=form.cleaned_data['course'],
                    defaults=data
                )

                if created:
                    new_enrollment.enrolled_by = self.request.user
                    new_enrollment.transferred = True
                    new_enrollment.transferred_from = enrollment
                    new_enrollment.save()

            except Exception as e:
                messages.error(request, f"Произошла ошибка. {e}")
                return redirect(self.request.path)
            else:
                enrollment.status = False
                enrollment.save()

                messages.success(request, "Запись успешно перенаправлена.")
                next_url = self.request.GET.get('next_url', '/')
                return redirect(next_url)

        return redirect('main:main')