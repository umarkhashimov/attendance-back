from django.db import models
from courses.models import SubjectModel
# Create your models here.
from datetime import datetime
import os


def course_material_upload_path(instance, filename):
    # Get extension
    ext = filename.split('.')[-1]
    # Sanitize subject name (avoid spaces/special chars)
    subject_name = instance.subject.name.replace(' ', '_') if instance.subject else 'unknown_subject'
    # Remove extension from original file name
    base_name = os.path.splitext(filename)[0]
    # Add timestamp for uniqueness
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    # Construct new filename
    new_filename = f"{base_name}_{timestamp}.{ext}"
    # Path inside media root
    return os.path.join("course", "materials", new_filename)

class CourseMaterials(models.Model):
    subject = models.ForeignKey(SubjectModel, on_delete=models.SET_NULL, null=True, verbose_name="Предмет")
    file_name = models.CharField(max_length=150, verbose_name="Имя файла")
    file = models.FileField(upload_to=course_material_upload_path, verbose_name="Файл")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено в")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано в")

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'
