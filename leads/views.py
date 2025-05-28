from django.db.models.functions import Lead
from django.shortcuts import render
from django.views.generic import ListView, View

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
        print(request.POST)
        context = {
            'lead_form': LeadForm(request.POST),
            'student_form': StudentInfoForm(request.POST),
        }

        return render(request, self.template_name, context)


        return render(request, self.template_name, {'data': data})