from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls'), name='users'),
    path('', include('main.urls'), name='main'),
    path('', include('attendance.urls'), name='attendance'),
    path('', include('students.urls'), name='students'),
    path('', include('courses.urls'), name='courses'),
    path('', include('payment.urls'), name='payment'),
    path('', include('leads.urls'), name='leads'),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)