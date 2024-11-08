from django.urls import path
from .views import StudentUpdateView

app_name = 'students'

urlpatterns = [
    path('student/<int:pk>', StudentUpdateView.as_view(), name='student_update'),

]
