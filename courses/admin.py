from django.contrib import admin
from .models import CourseModel, SessionsModel, SubjectModel

admin.site.register(SubjectModel)


@admin.register(CourseModel)
class CourseModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name','teacher', 'get_enrolled_count', 'status']
    list_filter = ['teacher', 'status']


@admin.register(SessionsModel)
class SessionsModelAdmin(admin.ModelAdmin):
    list_display = ['id','course', 'course__teacher', 'status', 'record_by']
    list_filter = ['course']
