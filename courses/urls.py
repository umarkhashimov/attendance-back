from django.urls import path
from .views import UpdateCourseWeekdaysView, CourseUpdateView, CourseDetailView, StartCourseView, RedirectCourseToCloseSession, ConductSession, CreateCourseView

app_name = 'courses'

urlpatterns = [
    path('course_sessions/<int:pk>', CourseDetailView.as_view(), name='course_sessions'),
    path('course/<int:pk>', CourseUpdateView.as_view(), name='course_update'),
    path('course_start/<int:pk>', StartCourseView.as_view(), name='course_start'),
    path('closest_session/<int:course_id>', RedirectCourseToCloseSession.as_view(), name="closest_session"),
    path('conduct_session/<int:course_id>', ConductSession.as_view(), name="conduct_session"),
    path('create_course/', CreateCourseView.as_view(), name="create_course"),
    path('update_course_weekdays/<int:pk>', UpdateCourseWeekdaysView.as_view(), name='update_course_weekdays'),
]
