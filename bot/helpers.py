from asgiref.sync import sync_to_async
from django.db.models import Q
from students.models import Enrollment, StudentModel
from attendance.models import AttendanceModel

@sync_to_async
def get_enrollments(st_id):

    results =  list(
        Enrollment.objects.filter(status=True, student__id=st_id).distinct()
    )

    return [{'id': enrollment.id, 'course': enrollment.course.name} for enrollment in results]

@sync_to_async
def get_students(phone_number):

    results = list(
        StudentModel.objects.filter(Q(phone_number=str(phone_number)) | Q(additional_number=str(phone_number))).values_list("id", "first_name", "last_name")
    )

    return [{'id': id, 'fname':first, 'lname': last} for id, first, last in results]

@sync_to_async
def get_student(st_id):
    results = StudentModel.objects.get(id=st_id)
    return {'id': results.id, 'fname': results.first_name, 'lname': results.last_name}

@sync_to_async
def get_enrollment_balance(enrollment_id):
    enrollment = Enrollment.objects.get(id=enrollment_id)

    return {'payed_due': enrollment.payment_due, 'balance': enrollment.balance}

@sync_to_async
def get_enrollment_attendance_list(enrollment_id):
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
