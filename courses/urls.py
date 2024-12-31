from django.urls import path
from .views import CancelSessionView, CourseUpdateView, CourseDetailView, StartCourseView, ConductSession, CreateCourseView

app_name = 'courses'

urlpatterns = [
    path('course_sessions/<int:pk>', CourseDetailView.as_view(), name='course_sessions'),
    path('course/<int:pk>', CourseUpdateView.as_view(), name='course_update'),
    path('course_start/<int:pk>', StartCourseView.as_view(), name='course_start'),
    path('conduct_session/<int:course_id>', ConductSession.as_view(), name="conduct_session"),
    path('cancel_session/<int:course_id>', CancelSessionView.as_view(), name="cancel_session"),
    path('create_course/', CreateCourseView.as_view(), name="create_course"),
]
