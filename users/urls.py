from django.urls import path
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

from .views import CustomUserCreateView, reset_user_password, UserUpdateView, LoginPageView, ProfileView, TeacherUpdateView, CustomPasswordChangeView, SalaryUsersListView, SalaryCourseDetailView, AdminActionsView, UsersListView

# Api
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserProfileView
app_name = 'users'

urlpatterns = [
    path('login/', LoginPageView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('home')), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('teacher/<int:pk>', TeacherUpdateView.as_view(), name='teacher_update'),
    path('profile/password-change/', CustomPasswordChangeView.as_view(), name='update_password'),
    path('actions-history/', AdminActionsView.as_view(), name='admin_actions'),

    path('users/', UsersListView.as_view(), name='users_list'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/reset-password/', reset_user_password, name='reset_user_password'),
    path('users/create/', CustomUserCreateView.as_view(), name='user_create'),
    path('salary/users/', SalaryUsersListView.as_view(), name='salary_users_list'),
    path('salary/teacher/<int:teacher_id>/course/<int:course_id>', SalaryCourseDetailView.as_view(), name='salary_course_detail'),


    #     API
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/profile/', UserProfileView.as_view(), name='user-profile'),
]