from django.views.generic import TemplateView

from courses.models import CourseModel

class MainPageView(TemplateView):
    template_name = 'main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role == '1':
            context["courses"] = CourseModel.objects.all().filter(teacher__id=self.request.user.id)
        else:
            context["courses"] = CourseModel.objects.all()
        return context