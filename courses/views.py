from pyexpat.errors import messages
from django.contrib import messages
from users.filters import AdminRequired, SuperUserRequired
from django.views.generic import DetailView,  UpdateView, View, CreateView, ListView, TemplateView
from django.core.exceptions import PermissionDenied

from users.helpers import record_action
from .models import CourseModel, SessionsModel, SubjectModel
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from datetime import datetime

from students.models import Enrollment
from students.forms import CourseEnrollmentForm, ReEnrollmentForm
from attendance.models import AttendanceModel
from .forms import CancelCauseForm, CourseCreateForm,CreateSubjectForm
from payment.forms import CreatePaymentForm
from payment.models import PaymentModel

class CourseUpdateView(AdminRequired, UpdateView):
    model = CourseModel
    template_name = "course_detail.html"
    form_class = CourseCreateForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        data = form.cleaned_data
        if data['days'] == '1':
            obj.weekdays = ['0', '2', '4']
        elif data['days'] == '2':
            obj.weekdays = ['1', '3', '5']
        else:
            obj.weekdays = data['weekdays']

        obj.save()
        form.save_m2m()

        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Now add your custom props here
        weekdays = ",".join(filter(None, self.get_object().weekdays))

        if weekdays == '0,2,4':
            kwargs['days'] = 1
        elif weekdays == '1,3,5':
            kwargs['days'] = 2
        else:
            kwargs['days'] = 3

        # kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return self.request.path
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['obj'] = self.get_object()
        context['enrollment_form'] = CourseEnrollmentForm(course=self.get_object().id)
        context['enrollments'] = Enrollment.objects.all().filter(course=self.get_object(), status=True).order_by('hold', '-trial_lesson', 'trail_used_once','student__first_name', 'student__last_name')
        context['payment_form'] = CreatePaymentForm

        # Get the course and its related sessions
        course = CourseModel.objects.get(id=self.get_object().id)
        sessions = SessionsModel.objects.filter(course=course)

        # Get all enrollments for the course
        enrollments = Enrollment.objects.filter(course=course, status=True).order_by('student__first_name', 'student__last_name')

        # Get the attendance records for the sessions
        attendance_data = []
        for enrollment in enrollments:
            student_attendance = []
            for session in sessions:
                attendance = AttendanceModel.objects.filter(
                    session=session,
                    enrollment=enrollment
                ).first()
                student_attendance.append(
                    {
                        'status': attendance.status if attendance else None,
                        'homework_grade': attendance.homework_grade if attendance else None,
                        'participation_grade': attendance.participation_grade if attendance else None,
                    })

            attendance_data.append({
                'student': enrollment.student.full_name,
                'attendance': student_attendance,
            })

        context.update({
            'course': course,
            'sessions': sessions,
            'attendance_data': attendance_data
        })

        # Payment History
        payments = PaymentModel.objects.all().filter(enrollment__course=course).order_by('-date')
        context['payment_history'] = payments

        return context

class StartCourseView(AdminRequired, View):
    def get(self, request, pk):
        return redirect("courses:course_update", pk=pk)

    def post(self, request, pk):
        course = CourseModel.objects.get(id=pk)
        if course.is_started == False:

            course.create_sessions()
        return redirect("courses:course_update", pk=pk)

class CreateCourseView(AdminRequired, CreateView):
    model = CourseModel
    template_name = 'create_course.html'
    form_class = CourseCreateForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        data = form.cleaned_data
        if data['days'] == '1':
            obj.weekdays = ['0', '2', '4']
        elif data['days'] == '2':
            obj.weekdays = ['1', '3', '5']
        else:
            obj.weekdays = data['weekdays']

        obj.save()
        form.save_m2m()

        return super().form_valid(form)

    def get_success_url(self):
        action_message = f"Создал группу <b>{self.object}</b>"
        record_action(1, self.request.user, self.object, self.object.id, action_message)
        return reverse('courses:course_update', kwargs={'pk': self.object.id})

class CancelSessionView(View):

    def post(self, request, course_id, session_date):
        form = CancelCauseForm(request.POST)
        if form.is_valid():
            cause = form.cleaned_data['cause']
            today = datetime.now().date()
            course= get_object_or_404(CourseModel, id=course_id)
            session, created = SessionsModel.objects.get_or_create(course=course, date=session_date, defaults={'status': False, 'record_by_id': self.request.user.id, 'cause': cause})
            # generate empty attendance based on enrollment status
            enrollments = Enrollment.objects.filter(course=course, status=True)

            if created:
                for obj in enrollments:
                    enrolled = Enrollment.objects.get(student__student_id=obj.student.student_id, course=course)
                    AttendanceModel.objects.get_or_create(enrollment=enrolled, session=session)


                if self.request.user.is_superuser:
                    action_message = f"Отметил урок <b>{session}</b> как отмененный"
                    record_action(1, self.request.user, session, session.id, action_message)

        # return redirect('attendance:session_detail', course_id=course_id)
        return redirect('/?date=' + session_date)

class ConductSession(View):

    def get(self, request, course_id, session_date):
        today = datetime.now().date()
        course= get_object_or_404(CourseModel, id=course_id)
        session, created = SessionsModel.objects.get_or_create(course=course, date=session_date, defaults={'status': True, 'record_by_id': self.request.user.id, 'topic': course.last_topic})

        if created:
            # generate empty attendance based on enrollment status
            enrollments = Enrollment.objects.filter(course=course, status=True)
            for obj in enrollments:
                enrolled = Enrollment.objects.get(student__student_id=obj.student.student_id, course=course)
                AttendanceModel.objects.get_or_create(enrollment=enrolled, session=session, defaults={'status': 3 if obj.hold else None})

            # Record Action
            if self.request.user.is_superuser:
                action_message = f"Отметил урок <b>{session}</b> как проведенный"
                record_action(1, self.request.user, session, session.id, action_message)

        # return redirect('attendance:session_detail', course_id=course_id)
        return redirect('/?date=' + session_date)


class MyCoursesView(ListView):
    queryset = CourseModel.objects.all()
    template_name = "my_groups.html"
    context_object_name = 'courses'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == '1':
            queryset = queryset.filter(teacher_id=user.id)

        return queryset

class GroupInfoView(DetailView):
    template_name = 'group_info.html'
    model = CourseModel
    context_object_name = 'group'
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the course and its related sessions
        course = CourseModel.objects.get(id=self.get_object().id)
        sessions = SessionsModel.objects.filter(course=course)

        # Get all enrollments for the course
        enrollments = Enrollment.objects.filter(course=course, status=True).order_by('student__first_name', 'student__last_name')

        # Get the attendance records for the sessions
        attendance_data = []
        for enrollment in enrollments:
            student_attendance = []
            for session in sessions:
                attendance = AttendanceModel.objects.filter(
                    session=session,
                    enrollment=enrollment
                ).first()
                student_attendance.append(
                    {
                        'status': attendance.status if attendance else None,
                        'homework_grade': attendance.homework_grade if attendance else None,
                        'participation_grade': attendance.participation_grade if attendance else None,
                    })

            attendance_data.append({
                'student': enrollment.student.full_name,
                'attendance': student_attendance,
            })

        context.update({
            'course': course,
            'sessions': sessions,
            'attendance_data': attendance_data
        })

        return context

class UpdateGroupTopicView(View):

    def post(self, request, pk):
        course = get_object_or_404(CourseModel, id=pk)

        new_topic = request.POST['topic']
        print("HIII", new_topic)

        if new_topic:
            course.last_topic = new_topic
            course.save()

        messages.success(request, 'Успешно сохранено')
        return redirect("courses:groupinfo", pk=course.id)


class ArchiveCourseView(SuperUserRequired,View):
    def get(self, request, pk):
        course = get_object_or_404(CourseModel, id=pk)
        status = course.archive_course()
        print('aaaaaaaaaaaaaaaaaa')
        if status:
            return redirect("main:courses_list")

        return redirect("courses:course_update", pk=course.id)


class CreateSubjectView(AdminRequired,CreateView):
    model = SubjectModel
    template_name = "create_subject.html"
    form_class = CreateSubjectForm

    def get_success_url(self):
        return reverse('main:courses_list')
