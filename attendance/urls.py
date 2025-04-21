from django.urls import path
from .views import RedirecToSessionByDate, GetSessionView

app_name = 'attendance'

urlpatterns = [
    path('course/<int:course_id>/session/<int:session_id>/<str:session_date>',  GetSessionView.as_view(), name='session_detail'),
    path('session_date/<int:course_id>', RedirecToSessionByDate.as_view(), name='session_date'),
]
