from django.urls import path
from .views import RecordAttendanceView

app_name = 'attendance'

urlpatterns = [
    path('session/<int:session_id>', RecordAttendanceView.as_view(), name='session_detail'),
]
