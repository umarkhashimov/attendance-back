from django.db.models import Q
from django.forms.models import model_to_dict
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, View, DetailView
from django.contrib import messages


from students.models import StudentModel
from users.models import UsersModel
from .forms import LeadForm, LeadsListFilterForm
from .models import LeadsModel
from students.forms import StudentInfoForm, StudentEnrollmentForm
from courses.models import SubjectModel

class LeadsListView(ListView):
    model = LeadsModel
    template_name = 'leads/leads_list.html'
    context_object_name = 'leads'
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.request.GET.copy()
        context['filter_form'] = LeadsListFilterForm(initial=data)

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        subject = self.request.GET.get('subject', None)
        days = self.request.GET.get('weekdays', None)
        teacher = self.request.GET.get('teacher', None)
        status = self.request.GET.get('status', None)
        date_from = self.request.GET.get('date_from', None)
        date_to = self.request.GET.get('date_to', None)
        student_id = self.request.GET.get('student', None)
        created_by = self.request.GET.get('created_by', None)

        if student_id:
            queryset = queryset.filter(student__id=student_id)

        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)

        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        elif not date_to and date_from:
            queryset = queryset.filter(created_at__lte=date_from)

        if status:
            queryset = queryset.filter(status=status)

        if subject:
            queryset = queryset.filter(subject=subject)

        if days:
            if days == "1":
                queryset = queryset.filter(weekdays__contains='0,2,4')
            elif days == "2":
                queryset = queryset.filter(weekdays__contains='1,3,5')
            elif days == "3":
                queryset = queryset.exclude(Q(weekdays__contains="0,2,4") | Q(weekdays__contains="1,3,5"))

        if teacher:
            queryset = queryset.filter(teacher_id=teacher)

        if created_by:
            queryset = queryset.filter(created_by=created_by)

        return queryset


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

            subject_id = data.get('subject')
            subject = get_object_or_404(SubjectModel, pk=subject_id) if subject_id else None

            # Remove FK fields if already handled manually
            lead_data.pop('student', None)
            lead_data.pop('subject', None)
            lead_data.pop('teacher', None)

            # Normalize weekdays (optional: convert to int)
            if lead_data.get('weekdays') is not None:
                lead_data['weekdays'] = int(lead_data['weekdays'])

            lead = LeadsModel.objects.create(student=student, teacher=teacher, subject=subject, **lead_data, created_by=self.request.user)

            messages.success(request, 'Лид успешно создан')
            return redirect('leads:leads_list')
        except Exception as e:
            messages.error(request, f'Ошибка при создании лида')


        context = {
            'lead_form': LeadForm(request.POST),
            'student_form': StudentInfoForm(request.POST),
        }

        return render(request, self.template_name, context)

class LeadDetailView(DetailView):
    template_name = 'leads/lead_detail.html'
    model = LeadsModel
    context_object_name = 'lead'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.request.GET.dict()
        object_data = model_to_dict(self.get_object())
        merged_data = {**object_data, **data}
        context['filter_form'] = LeadsListFilterForm(initial=merged_data)
        context['enroll_form'] = StudentEnrollmentForm(student=self.get_object().student, teacher=self.request.GET.get('teacher', None))
        return context