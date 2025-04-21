from django.contrib import admin
from .models import StudentModel, Enrollment

@admin.register(StudentModel)
class StudentModelAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone_number', 'additional_number']
    list_display_links = ['first_name', 'last_name']
    search_fields = ['first_name', 'last_name', 'phone_number', 'additional_number']
    list_filter = ['enrollment_date', 'courses']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['course', 'student', 'status', 'payment_due', 'enrolled_at']
    list_filter = ['status', 'enrolled_by', 'course__teacher', 'enrolled_at', 'course']
    search_fields = ['student__first_name', 'student__last_name']