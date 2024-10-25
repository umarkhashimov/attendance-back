from django.contrib import admin
from .models import CourseModel, SessionsModel

admin.site.register(CourseModel)
admin.site.register(SessionsModel)
