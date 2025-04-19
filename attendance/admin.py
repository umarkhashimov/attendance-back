from django.contrib import admin
from .models import AttendanceModel



class AttendanceModelAdmin(admin.ModelAdmin):
    list_display = ['enrollment__student', 'session__course', 'session__date', 'status']
    search_fields = ('enrollment', 'session')
    list_filter = ('enrollment__course',)
    ordering = ('session',) 

admin.site.register(AttendanceModel, AttendanceModelAdmin)