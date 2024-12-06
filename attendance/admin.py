from django.contrib import admin
from .models import AttendanceModel



class AttendanceModelAdmin(admin.ModelAdmin):
    list_display = ('enrollment__student', 'session', 'status')  # Fields to display in the list view
    search_fields = ('enrollment', 'session')         # Fields searchable in the admin
    list_filter = ('enrollment__course',)           # Add filter options in the list view
    ordering = ('session',) 

admin.site.register(AttendanceModel, AttendanceModelAdmin)