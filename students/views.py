from django.views.generic import UpdateView, CreateView
from django.urls import reverse

from users.filters import AdminRequired
from .models import StudentModel
from .forms import StudentInfoForm

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