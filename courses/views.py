

from users.filters import AdminRequired
from django.views.generic import DetailView,  UpdateView, View
from django.core.exceptions import PermissionDenied
from .models import CourseModel, SessionsModel
from django.urls import reverse
from django.shortcuts import redirect

from .forms import CourseUpdateForm

class CourseUpdateView(AdminRequired, UpdateView):
    model = CourseModel
    template_name = "course_detail.html"
    form_class = CourseUpdateForm

    def get_success_url(self):
        return reverse('main:courses_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['obj'] = self.get_object()
        return context


class CourseDetailView(DetailView):
    model = CourseModel
    template_name = 'course_sessions_list.html'
    context_object_name = 'course'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_superuser and obj.teacher != self.request.user:
            raise PermissionDenied()  # Raises a 403 error if the teacher is not assigned to the course
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['sessions'] = SessionsModel.objects.all().filter(course=course)
        return context
    
class StartCourseView(AdminRequired, View):
    def get(self, request, pk):
        return redirect("courses:course_update", pk=pk)

    def post(self, request, pk):
        course = CourseModel.objects.get(id=pk)
        course.create_sessions()
        print('Success')
        return redirect("courses:course_update", pk=pk)