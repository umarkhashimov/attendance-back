from django.views.generic import UpdateView
from django.urls import reverse

from users.filters import AdminRequired
from .models import StudentModel

class StudentUpdateView(AdminRequired, UpdateView):
    model = StudentModel
    template_name = 'student_update.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse('main:students_list')