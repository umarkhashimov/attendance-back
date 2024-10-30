from django.views.generic import TemplateView, DetailView
from django.core.exceptions import PermissionDenied

from courses.models import CourseModel, SessionsModel

class MainPageView(TemplateView):
    template_name = 'main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role == '1':
            context["courses"] = CourseModel.objects.all().filter(teacher__id=self.request.user.id)
        else:
            context["courses"] = CourseModel.objects.all()
        return context
    

class CourseDetailView(DetailView):
    model = CourseModel
    template_name = 'course_detail.html'
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

class TeachersView(TemplateView):
    pass