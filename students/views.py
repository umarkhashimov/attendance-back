from django.views.generic import UpdateView, CreateView, View
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect

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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student"] = self.get_object()
        context['enrollments'] = Enrollment.objects.all().filter(student=self.get_object(), status=True)
        return context
    
    
class CreateStudentView(AdminRequired, CreateView):
    template_name = 'create_student.html'
    model = StudentModel
    form_class = StudentInfoForm
    exclude = ['courses']

    def get_success_url(self):
        return reverse('main:courses_list')
    


class CreateEnrollmentView(AdminRequired, View):
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
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            # Retrieve the cleaned data
            course = CourseModel.objects.get(id=course_id) if course_id else None
            student = StudentModel.objects.get(id=student_id) if student_id else None

            # Use update_or_create to either update or create the enrollment
            enrollment, created = Enrollment.objects.update_or_create(
                course=course,
                student=student,
                defaults=form.cleaned_data
            )
            
            # if created:
            #     pass
            
            next_url = 'main:main' 

            if course_id:
                return redirect('courses:course_update', pk=course_id)
            elif student_id:
                return redirect('students:student_update', pk=student_id)
            else:
                return redirect('main:main')


        return render(request, self.template_name, {'form': form})
    

class UpdateEnrollmentView(UpdateView, AdminRequired):
    model = Enrollment
    fields = '__all__'
    template_name = "update_enrollment.html"
    
    def get_success_url(self):
        next_url  = self.request.GET.get('next', '/')
        return next_url