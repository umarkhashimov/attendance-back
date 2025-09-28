from asgiref.sync import sync_to_async
from django.db.models import Q
from django.conf import settings
from students.models import Enrollment, StudentModel
from attendance.models import AttendanceModel
from django.db import close_old_connections
from courses.models import SubjectModel
from users.models import UsersModel

@sync_to_async
def get_enrollments(st_id):
    close_old_connections()
    results =  list(
        Enrollment.objects.filter(status=True, student__id=st_id).distinct()
    )

    return [{'id': enrollment.id, 'course': enrollment.course.name} for enrollment in results]

@sync_to_async
def get_students(phone_number):
    close_old_connections()

    results = list(
        StudentModel.objects.filter(Q(phone_number=str(phone_number)) | Q(additional_number=str(phone_number))).values_list("id", "first_name", "last_name")
    )

    return [{'id': id, 'fname':first, 'lname': last} for id, first, last in results]

@sync_to_async
def get_student(st_id):
    close_old_connections()

    results = StudentModel.objects.get(id=st_id)
    return {'id': results.id, 'fname': results.first_name, 'lname': results.last_name}

@sync_to_async
def get_enrollment_balance(enrollment_id):
    close_old_connections()

    enrollment = Enrollment.objects.get(id=enrollment_id)

    return {'payed_due': enrollment.payment_due, 'balance': enrollment.balance}

@sync_to_async
def get_enrollment_attendance_list(enrollment_id):
    close_old_connections()

    enrollment = Enrollment.objects.get(id=enrollment_id)
    attendances = AttendanceModel.objects.filter(enrollment=enrollment).order_by('session__date')[:12]

    attendance_list = []
    for attendance in attendances:
        status = '❓'
        if attendance.status == 1:
            status = '✅ Присутствует'
        elif attendance.status == 2:
            status = '⌛ Опоздал'
        elif attendance.status == 3:
            status = '❄️ Заморожен'
        elif attendance.status == 0:
            status = "❌ Отсутствует"

        attendance_list.append({'date': attendance.session.date, 'status': status})

    return attendance_list

@sync_to_async
def get_subjects():
    close_old_connections()

    subjects = SubjectModel.objects.all()

    return [{'id': subject.id, 'name': subject.name} for subject in subjects]


@sync_to_async
def get_subject_teachers(subject_id):
    close_old_connections()

    teachers = (
        UsersModel.objects.filter(
            role='1',
            coursemodel__subject_id=subject_id,
            is_active=True,
            display_in_bot=True
        )
        .exclude(Q(bio__isnull=True) | Q(bio=''))
        .exclude(Q(image__isnull=True) | Q(image=''))
        .exclude(Q(first_name__isnull=True) | Q(first_name=''))
        .exclude(Q(last_name__isnull=True) | Q(last_name=''))
        .distinct()
    )
    return [{'id': teacher.id,'fname': teacher.first_name, 'lname': teacher.last_name} for teacher in teachers]

@sync_to_async
def get_teacher_info(teacher_id):
    close_old_connections()

    teacher = UsersModel.objects.get(id=teacher_id, is_active=True, display_in_bot=True)

    return {'id': teacher.id, 'fname': teacher.first_name, 'lname': teacher.last_name, 'bio': teacher.bio, 'image': teacher.image}
