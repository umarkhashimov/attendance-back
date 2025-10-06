from django.urls import path

from .views import LeadsListView, CreateLeadView, LeadDetailView, LeadUpdateView, LeadEnrollView, LeadCancelView, LeadCreateCourseEnrollView

app_name = 'leads'

urlpatterns = [
    path('leads/', LeadsListView.as_view(), name='leads_list'),
    path('leads/create/', CreateLeadView.as_view(), name='create_lead'),
    path('leads/detail/<int:pk>', LeadDetailView.as_view(), name='lead_detail'),
    path('leads/update/<int:pk>', LeadUpdateView.as_view(), name='lead_update'),
    path('leads/<int:pk>/enroll/<int:student_id>', LeadEnrollView.as_view(), name='lead_enroll'),
    path('leads/<int:pk>/cancel', LeadCancelView.as_view(), name='lead_cancel'),
    path('leads/<int:pk>/create-course-enroll/<int:student_id>', LeadCreateCourseEnrollView.as_view(), name='lead_create_course_enroll'),
]