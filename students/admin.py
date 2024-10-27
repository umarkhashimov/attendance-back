from django.contrib import admin
from .models import StudentModel, Enrollment

admin.site.register(StudentModel)
admin.site.register(Enrollment)
