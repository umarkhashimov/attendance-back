from django.urls import path
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

from .views import LoginPageView, ProfileView, TeacherUpdateView, CustomPasswordChangeView, SalaryUsersListView, SalaryCourseDetailView, AdminActionsView, UsersListView

app_name = 'users'

urlpatterns = [
    path('login/', LoginPageView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('home')), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('teacher/<int:pk>', TeacherUpdateView.as_view(), name='teacher_update'),
    path('profile/password-change/', CustomPasswordChangeView.as_view(), name='update_password'),
    path('actions-history/', AdminActionsView.as_view(), name='admin_actions'),

    path('users/', UsersListView.as_view(), name='users_list'),

    path('salary/users/', SalaryUsersListView.as_view(), name='salary_users_list'),
    path('salary/course/<int:course_id>', SalaryCourseDetailView.as_view(), name='salary_course_detail'),
]