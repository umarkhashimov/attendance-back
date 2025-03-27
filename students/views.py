from django.views.generic import UpdateView, CreateView, View
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from collections import defaultdict

from users.filters import AdminRequired
from users.forms import TeacherSelectForm
from users.helpers import record_action
from .models import StudentModel, Enrollment
from .forms import StudentInfoForm
from courses.models import CourseModel
from payment.forms import CreatePaymentForm
from payment.models import PaymentModel
from .forms import EnrollmentForm, UpdateEnrollmentForm, StudentEnrollmentForm, CourseEnrollmentForm
from attendance.models import AttendanceModel
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
    template_name = 'create_enrollment.html'

    # def get(self, request, course_id=None, student_id=None):
    #     # Get the course or student based on the URL parameters
    #     course = None
    #     student = None

    #     if course_id:
    #         course = CourseModel.objects.get(id=course_id)
    #     if student_id:
    #         student = StudentModel.objects.get(id=student_id)

    #     # Create a new EnrollmentForm instance, pre-filling course or student if necessary
    #     form = EnrollmentForm(initial={
    #         'course': course,
    #         'student': student
    #     })

    #     return render(request, self.template_name, {
    #         'form': form,
    #         'course': course,
    #         'student': student
    #     })
    
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
                defaults={**form.cleaned_data, 'status': True}
            )

            if course_id:
                return redirect('courses:course_update', pk=course_id)
            elif student_id:
                return redirect('students:student_update', pk=student_id)
            else:
                return redirect('main:main')


        return render(request, self.template_name, {'form': form})
    

class UpdateEnrollmentView(View, AdminRequired):
    template_name = "update_enrollment.html"

    def post(self, request, pk):
        enrollment = get_object_or_404(Enrollment, id=pk)
        form = UpdateEnrollmentForm(request.POST)
        if form.is_valid():
            if not form.cleaned_data['balance']:
                form.cleaned_data['balance'] = enrollment.balance
            enrollment, created = Enrollment.objects.update_or_create(
                course=enrollment.course,
                student=enrollment.student,
                defaults={**form.cleaned_data}
            )
        
        next_url  = self.request.GET.get('next', '/')
        return redirect(next_url)

class DeactivateEnrollmentView(View):
    def post(self, request, enrollment_id):
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        enrollment.status = False
        enrollment.save()
        next_url  = self.request.GET.get('next', '/')
        return redirect(next_url)
