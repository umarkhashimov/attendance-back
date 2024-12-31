from django.views.generic import UpdateView, CreateView, View
from django.urls import reverse
from django.shortcuts import render, redirect

from users.filters import AdminRequired
from .models import StudentModel, Enrollment
from .forms import StudentInfoForm
from courses.models import CourseModel
from .forms import EnrollmentForm



class StudentUpdateView(AdminRequired, UpdateView):
    model = StudentModel
    template_name = 'student_update.html'
    form_class = StudentInfoForm

    def get_success_url(self):
        return reverse('main:students_list')
    
class CreateStudentView(AdminRequired, CreateView):
    template_name = 'create_student.html'
    model = StudentModel
    form_class = StudentInfoForm
    exclude = ['courses']

    def get_success_url(self):
        return reverse('main:courses_list')
    


class CreateEnrollmentView(View):
    template_name = 'create_enrollment.html'

    def get(self, request, course_id=None, student_id=None):
        # Get the course or student based on the URL parameters
        course = None
        student = None

        if course_id:
            course = CourseModel.objects.get(id=course_id)
        if student_id:
            student = StudentModel.objects.get(id=student_id)

        # Create a new EnrollmentForm instance, pre-filling course or student if necessary
        form = EnrollmentForm(initial={
            'course': course,
            'student': student
        })

        return render(request, self.template_name, {
            'form': form,
            'course': course,
            'student': student
        })
    
    def post(self, request, course_id=None, student_id=None):
        # Handle form submission and create the enrollment
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            if course_id:
                enrollment.course = CourseModel.objects.get(id=course_id)
            if student_id:
                enrollment.student = StudentModel.objects.get(id=student_id)
            enrollment.save()
            return redirect('courses:course_update', pk=course_id)  # Redirect to success page

        # Re-render form with errors if invalid
        return render(request, self.template_name, {'form': form})