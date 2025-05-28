from django.urls import path

from .views import LeadsListView, CreateLeadView

app_name = 'leads'

urlpatterns = [
    path('leads/', LeadsListView.as_view(), name='leads_list'),
    path('leads/create/', CreateLeadView.as_view(), name='create_lead'),
]