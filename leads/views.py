from sqlite3 import IntegrityError

from django.db.models.functions import Lead
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, View
from django.contrib import messages


from students.models import StudentModel
from users.models import UsersModel
from .forms import LeadForm
from .models import LeadsModel
from students.forms import StudentInfoForm
# Create your views here.

class LeadsListView(ListView):
    model = LeadsModel
    template_name = 'leads/leads_list.html'
    context_object_name = 'leads'


class CreateLeadView(View):
    template_name = 'leads/create_lead.html'

    def get(self, request):

        context = {
            'lead_form': LeadForm(),
            'student_form': StudentInfoForm(),
        }

        return render(request, self.template_name, context)

    def post(self, request):
        data = request.POST.dict()
        for key, value in data.items():
            data[key] = value if value != '' else None

        select_student = request.POST.get('select_student')
        select_student = True if select_student else False
        student_id = request.POST.get('student')

        if not select_student and student_id:
            # Use existing student
            student = get_object_or_404(StudentModel, pk=student_id)
        else:
            # Create new student
            student_fields = [f.name for f in StudentModel._meta.get_fields()]
            student_data = {k: v for k, v in data.items() if k in student_fields}
            student = StudentModel.objects.create(**student_data)

        try:
            lead_fields = [f.name for f in LeadsModel._meta.get_fields()]
            lead_data = {k: v for k, v in data.items() if k in lead_fields}

            teacher_id = data.get('teacher')
            teacher = get_object_or_404(UsersModel, pk=teacher_id) if teacher_id else None

            # Remove FK fields if already handled manually
            lead_data.pop('student', None)
            lead_data.pop('teacher', None)

            # Normalize weekdays (optional: convert to int)
            if lead_data.get('weekdays') is not None:
                lead_data['weekdays'] = int(lead_data['weekdays'])

            lead = LeadsModel.objects.create(student=student, teacher=teacher, **lead_data)

            messages.success(request, 'Лид успешно создан')
            return redirect('leads:leads_list')
        except Exception as e:
            messages.error(request, f'Ошибка при создании лида')


        context = {
            'lead_form': LeadForm(request.POST),
            'student_form': StudentInfoForm(request.POST),
        }

        return render(request, self.template_name, context)

