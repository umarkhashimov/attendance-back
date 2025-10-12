from django.contrib import admin

# Register your models here.
from .models import CourseMaterials

@admin.register(CourseMaterials)
class CourseMaterialsAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'file_name', 'created_at', 'updated_at']
    list_display_links = ['id', 'subject', 'file_name']
    list_filter = ['subject','created_at', 'updated_at']