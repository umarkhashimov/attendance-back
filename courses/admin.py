from django.contrib import admin
from .models import CourseModel, SessionsModel, SubjectModel

admin.site.register(CourseModel)
admin.site.register(SessionsModel)
admin.site.register(SubjectModel)


