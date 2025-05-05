from django.urls import path
from .views import GetSessionView

app_name = 'attendance'

urlpatterns = [
    path('course/<int:course_id>/session/<int:session_id>/<str:session_date>',  GetSessionView.as_view(), name='session_detail'),

]
