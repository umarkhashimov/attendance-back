from django.urls import path
from .views import RecordAttendanceView, RedirecToSessionByDate

app_name = 'attendance'

urlpatterns = [
    path('session/<int:session_id>', RecordAttendanceView.as_view(), name='session_detail'),
    path('session_date/<int:course_id>', RedirecToSessionByDate.as_view(), name='session_date'),
]
