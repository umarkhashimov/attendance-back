from datetime import datetime, date, timedelta
from django.views.generic import UpdateView, CreateView, View
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from collections import defaultdict
from django.forms.models import model_to_dict
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from users.filters import AdminRequired
from users.models import UsersModel
from users.forms import TeacherSelectForm
from users.helpers import record_action
from .models import StudentModel, Enrollment
from .forms import StudentInfoForm, ReEnrollmentForm, ReEnrollmentFilterForm
from courses.models import CourseModel
from payment.forms import CreatePaymentForm
from payment.models import PaymentModel
from .forms import EnrollmentForm, UpdateEnrollmentForm, StudentEnrollmentForm, CourseEnrollmentForm
from attendance.models import AttendanceModel
from leads.models import LeadsModel
from leads.forms import LeadForm
from rapidfuzz import fuzz

def autocomplete_students(request):
    q = request.GET.get('q')

    if not q:
        return JsonResponse({'results': []})

    # Take only the last word the user typed
    last_word = q.split()[-1].lower()

    # Collect all unique first and last names
    all_first_names = set(StudentModel.objects.values_list('first_name', flat=True))
    all_last_names = set(StudentModel.objects.values_list('last_name', flat=True))

    suggestions = set()

    for name in all_first_names.union(all_last_names):
        if fuzz.ratio(last_word, name.lower()) >= 70:
            suggestions.add(name)

    results = [{"id": i, "text": name} for i, name in enumerate(sorted(suggestions))]
    return JsonResponse({'results': results})

class StudentUpdateView(AdminRequired, UpdateView):
    model = StudentModel
    template_name = 'student_update.html'
    form_class = StudentInfoForm

    def get_success_url(self):
        return self.request.path
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student"] = self.get_object()
        context["teacher_select_form"] = TeacherSelectForm(initial=self.request.GET)
        context['enrollment_update_form'] = UpdateEnrollmentForm
        context['enrollments'] = Enrollment.objects.all().filter(student=self.get_object(), status=True)
        context['enrollment_form'] = StudentEnrollmentForm(student=self.get_object(), teacher=self.request.GET.get('teacher', None))
        context['payment_form'] = CreatePaymentForm
        context['lead_form'] = LeadForm

        # Payment history
        enrolled = Enrollment.objects.filter(student=self.get_object())

        payments_grouped = defaultdict(list)
        for enrollment in enrolled:
            course = enrollment.course
            payments_grouped[course] = [payment for payment in PaymentModel.objects.filter(enrollment=enrollment).order_by('-date')]
        context['payments_grouped'] = dict(payments_grouped)


        # Student Attendance info
        attendance_grouped = defaultdict(list)
        for enrollment in enrolled:
            course = enrollment.course
            attendance_grouped[course] = AttendanceModel.objects.filter(enrollment=enrollment).order_by('-session__date').values('session__date', 'status', 'homework_grade', 'participation_grade' )
        context['attendance_grouped'] = dict(attendance_grouped)

        return context
    
    
class CreateStudentView(AdminRequired, CreateView):
    template_name = 'create_student.html'
    model = StudentModel
    form_class = StudentInfoForm
    exclude = ['courses']

    def get_success_url(self):
        action_message = f"Создал ученика: <b>{self.object.id} - {self.object.full_name}</b>"
        record_action(1, self.request.user, self.object, self.object.id, action_message)
        return reverse('students:student_update', kwargs={'pk': self.object.id})

class CreateEnrollmentView(AdminRequired, View):

    def post(self, request, course_id=None, student_id=None):
        form = EnrollmentForm(request.POST)
        if student_id:
            form = StudentEnrollmentForm(request.POST)

        if course_id:
            form = CourseEnrollmentForm(request.POST)

        if form.is_valid():
            course = CourseModel.objects.get(id=course_id) if course_id else None
            student = StudentModel.objects.get(id=student_id) if student_id else None
            
            enrollment, created = Enrollment.objects.update_or_create(
                course=course if course else form.cleaned_data['course'],
                student=student if student else form.cleaned_data['student'],
                defaults={**form.cleaned_data, 'status': True, 'enrolled_at':datetime.now(), 'payment_due': None},
            )

            if created:
                enrollment.enrolled_by = self.request.user

            enrollment.save()

            action_message = f"Записал ученика <b>{enrollment.student}</b> в группу <b>{enrollment.course}</b>"
            record_action(1, self.request.user, enrollment, enrollment.id, action_message)
            if course_id:
                return redirect('courses:course_update', pk=course_id)
            elif student_id:
                return redirect('students:student_update', pk=student_id)
            else:
                return redirect('main:main')

        return redirect('main:main')
    

class UpdateEnrollmentView(AdminRequired, View):

    def post(self, request, pk):
        enrollment = get_object_or_404(Enrollment, id=pk)
        form = UpdateEnrollmentForm(request.POST)
        if form.is_valid():
            payment_due = enrollment.payment_due

            if form.cleaned_data['payment_due']:
                payment_due = form.cleaned_data['payment_due']


            enrollment, created = Enrollment.objects.update_or_create(
                course=enrollment.course,
                student=enrollment.student,
                defaults={**form.cleaned_data, 'payment_due':payment_due},
            )

            enrollment.save()

        next_url  = self.request.GET.get('next', '/')
        return redirect(next_url + '#enrollmentsTable')

class DeactivateEnrollmentView(AdminRequired, View):
    def get(self, request, enrollment_id):
        next_url  = self.request.GET.get('next', '/')
        if self.request.user.has_permission('delete_enrollment') or self.request.user.is_superuser:
            try:
                enrollment = get_object_or_404(Enrollment, id=enrollment_id)
                enrollment.trial_lesson = False
                enrollment.hold = False
                enrollment.status = False
                enrollment.save()
                messages.success(request, 'Запись отключена успешно')
                action_message = f"Удалил ученика <b>{enrollment.student}</b> из группы <b>{enrollment.course}</b>"
                record_action(3, self.request.user, enrollment, enrollment.id, action_message)
            except Exception as e:
                messages.error(request, 'Что-то пошло не так')
        else:
            messages.warning(request, 'У вас нет доступа к этой функции')

        return redirect(next_url)


class UpdateEnrollmentNote(AdminRequired, View):
    def post(self, request, pk):
        enrollment = get_object_or_404(Enrollment, id=pk)
        text = request.POST.get('text', None)
        enrollment.note = text.strip()
        enrollment.save()
        next_url = self.request.GET.get('next', '/')
        return redirect(next_url)

class ReEnrollStudentView(AdminRequired, View):

    def get(self, request, pk):
        if self.request.user.is_superuser or 're_enrollment' in self.request.user.custom_permissions:
            enrollment = get_object_or_404(Enrollment, id=pk)
            weekdays = request.GET.get('weekdays', None)
            teacher = request.GET.get('teacher', None)

            context = {
                're_enrollment_form': ReEnrollmentForm(student=enrollment.student, teacher=teacher or None, weekdays=weekdays or None),
                'filter_form': ReEnrollmentFilterForm(request.GET),
                'enrollment': enrollment,
            }
            return render(request, 're_enrollment.html', context)
        else:
            messages.warning(request, 'У вас нет доступа к этой функции')
            return redirect(request.META.get('HTTP_REFERER', '/'))

    def post(self, request, pk):
        next_url = self.request.GET.get('next_url', '/')
        if self.request.user.is_superuser or 're_enrollment' in self.request.user.custom_permissions:
            enrollment = get_object_or_404(Enrollment, id=pk)
            form = ReEnrollmentForm(request.POST)
            if form.is_valid():
                try:
                    data = model_to_dict(enrollment)

                    # Remove fields you want to set explicitly
                    data.pop('id', None)
                    data.pop('transferred_from', None)
                    data.pop('transferred', None)
                    data['course'] = form.cleaned_data['course']
                    data['student'] = enrollment.student
                    data['enrolled_by'] = enrollment.enrolled_by
                    data['enrolled_at'] = datetime.now()

                    new_enrollment, created = Enrollment.objects.update_or_create(
                        student=enrollment.student,
                        course=form.cleaned_data['course'],
                        defaults=data
                    )


                    if created:
                        new_enrollment.enrolled_by = self.request.user
                        new_enrollment.transferred = True
                        new_enrollment.transferred_from = enrollment
                        new_enrollment.save()

                    new_enrollment.calculate_new_payment_due([x for x in new_enrollment.course.weekdays], balance=enrollment.balance)

                except Exception as e:
                    messages.error(request, f"Произошла ошибка. {e}")
                    return redirect(self.request.path)
                else:
                    enrollment.status = False
                    enrollment.save()

                    messages.success(request, "Запись успешно перенаправлена.")
                    return redirect(next_url)
        else:
            messages.warning(request,'У вас нет доступа к этой функции')

        return redirect(next_url)

class GroupReEnrollmentView(AdminRequired, View):
    def get(self, request, group_id):
        if self.request.user.is_superuser or 're_enrollment' in self.request.user.custom_permissions:
            course = get_object_or_404(CourseModel, id=group_id)
            weekdays = request.GET.get('weekdays', None)
            teacher = request.GET.get('teacher', None)

            # Get list of IDs passed via GET
            enrollment_ids = request.GET.get('enrollmentid', '')
            id_list = enrollment_ids.split(',') if enrollment_ids else []
            enrollments = Enrollment.objects.filter(id__in=id_list, course=course)

            if not enrollments or enrollments.count() == 0:
                return redirect('courses:course_update', pk=course.id)

            return render(request, 'group_re_enrollment.html', {
                'course': course,
                'enrollments': enrollments.order_by('student__first_name', 'student__last_name'),
                're_enrollment_form': ReEnrollmentForm(exclude_course=course.id, teacher=teacher or None, weekdays=weekdays or None),
                'filter_form': ReEnrollmentFilterForm(request.GET),
            })
        else:
            messages.warning(request,'У вас нет доступа к этой функции')
            return  redirect(request.META.get('HTTP_REFERER', '/'))


    def post(self, request, group_id):
        course = get_object_or_404(CourseModel, id=group_id)
        if self.request.user.is_superuser or 're_enrollment' in self.request.user.custom_permissions:

            enrollment_ids = request.POST.getlist('enrollment_ids')
            enrollments = Enrollment.objects.filter(id__in=enrollment_ids, course=course)

            form = ReEnrollmentForm(request.POST)
            if form.is_valid() and enrollments.count() > 0:
                for enrollment in enrollments:
                    if not Enrollment.objects.filter(student=enrollment.student, course=form.cleaned_data['course'], status=True).exists():
                        try:
                            data = model_to_dict(enrollment)

                            # Remove fields you want to set explicitly
                            data.pop('id', None)
                            data.pop('transferred_from', None)
                            data.pop('transferred', None)
                            data['course'] = form.cleaned_data['course']
                            data['student'] = enrollment.student
                            data['enrolled_by'] = enrollment.enrolled_by
                            data['enrolled_at'] = datetime.now()

                            new_enrollment, created = Enrollment.objects.update_or_create(
                                student=enrollment.student,
                                course=form.cleaned_data['course'],
                                defaults=data
                            )

                            if created:
                                new_enrollment.enrolled_by = self.request.user
                                new_enrollment.transferred = True
                                new_enrollment.transferred_from = enrollment
                                new_enrollment.save()

                            new_enrollment.calculate_new_payment_due([x for x in new_enrollment.course.weekdays],
                                                                     balance=enrollment.balance)
                        except Exception as e:
                            messages.error(request, f"Произошла ошибка. {e}")
                        else:
                            enrollment.status = False
                            enrollment.save()

                            messages.success(request, "Запись успешно перенаправлена.")
                    else:
                        messages.error(request, "Запись уже существует.")
        else:
            messages.warning(request, 'У вас нет доступа к этой функции')
        return redirect('courses:course_update', pk=course.id)

class ArchiveStudent(AdminRequired,View):
    def get(self, request, pk):
        student = get_object_or_404(StudentModel, id=pk)
        if student.get_enrolled_count() < 1 and not student.archived:
            student.archived = True
            student.save()

            messages.success(request,'Студент Архивирован')
        else:
            messages.error(request,'Что-то пощло не так')

        return redirect('students:student_update', pk=student.id)


class UnArchiveStudent(AdminRequired, View):
    def get(self, request, pk):
        student = get_object_or_404(StudentModel, id=pk)

        if student.archived:
            student.archived = False
            student.save()

            messages.success(request, 'Студент разархивирован')
        else:
            messages.error(request, 'Что-то пощло не так')

        return redirect('students:student_update', pk=student.id)


class ConvertEnrollmentToLead(AdminRequired,View):

    def post(self, request, enrollment_id):
        enrollment = get_object_or_404(Enrollment, pk=enrollment_id)
        arrival_date = request.POST.get('arrival_date', '')
        note = request.POST.get('note', '')

        try:
            weekdays = 3
            if enrollment.course.weekdays == ['0', '2', '4']:
                weekdays = 1
            elif enrollment.course.weekdays == ['1', '3', '5']:
                weekdays = 2

            lead = LeadsModel.objects.create(student=enrollment.student,
                                             weekdays=weekdays,
                                             lesson_time=enrollment.course.lesson_time,
                                             subject=enrollment.course.subject,
                                             teacher=enrollment.course.teacher,
                                             arrival_date=arrival_date,
                                             note=note,
                                             created_by=request.user,
                                             status=1)
            enrollment.trial_lesson = False
            enrollment.hold = False
            enrollment.debt_note = None
            enrollment.status = False
            enrollment.save()
            messages.success(request, 'Запись отключена')
            messages.success(request, 'Лид успешно создан')
        except Exception as e:
            messages.error(request, 'Произошла ошибка')

        return  redirect(request.META.get('HTTP_REFERER', '/'))


class AbsentStudentsList(AdminRequired, View):
    template_name = 'payment/absent_students_list.html'

    def get(self, request):
        context = {}
        t = self.request.GET.get('date')
        today = date.today()
        if t:
            today = datetime.strptime(t, '%Y-%m-%d').date()
            if today > date.today():
                today = date.today()
        context['prev_date'] = today - timedelta(days=1)
        context['next_date'] = date.today() if today == date.today() else today + timedelta(days=1)

        teachers = UsersModel.objects.filter(role='1').distinct()
        # Filters
        weekdays = self.request.GET.get('weekdays', None)

        attendances = AttendanceModel.objects.select_related('enrollment__course__teacher').filter(Q(status=0) | Q(status=None), session__date=today)

        session_enrollment_map = defaultdict(list)
        for attendance in attendances:
            session = attendance.session
            session_enrollment_map[session].append(attendance)

        teacher_data = defaultdict(lambda: defaultdict(list))
        for session, attendance_list in session_enrollment_map.items():
            teacher = session.course.teacher
            teacher_data[teacher][session] = attendance_list

        teacher_data = {
            teacher: dict(course_map)
            for teacher, course_map in teacher_data.items()
        }

        context.update({
            'teacher_enrollments': teacher_data,
            'today': datetime.today().date().strftime("%Y-%m-%d"),
            'filter_date': today.strftime("%Y-%m-%d"),
        })
        return render(request, self.template_name, context)