from django.urls import path

from .views import LeadsListView, CreateLeadView, LeadDetailView, LeadUpdateView

app_name = 'leads'

urlpatterns = [
    path('leads/', LeadsListView.as_view(), name='leads_list'),
    path('leads/create/', CreateLeadView.as_view(), name='create_lead'),
    path('leads/detail/<int:pk>', LeadDetailView.as_view(), name='lead_detail'),
    path('leads/update/<int:pk>', LeadUpdateView.as_view(), name='lead_update'),
]