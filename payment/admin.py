from django.contrib import admin
from .models import PaymentModel

# admin.site.register(PaymentModel)

@admin.register(PaymentModel)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ['enrollment__student', 'enrollment__course', 'date']
    list_filter = ['date', 'enrollment__course']
    search_fields = ['enrollment__student__first_name', 'enrollment__student__last_name']