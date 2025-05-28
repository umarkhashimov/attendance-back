from django.contrib import admin


from .models import  LeadsModel

# admin.site.register(LeadsModel)

@admin.register(LeadsModel)
class LeadsModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'lesson_time', 'teacher']
    list_display_links = ['id', 'student']
    list_filter = ['weekdays', 'status', 'teacher']
    search_fields = ['student']