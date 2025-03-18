from django.urls import path
from .views import PaymentsListView, CreatePaymentView, ConfirmPaymentView, DebtPaymentsListView, TrialEnrollmentsView

app_name = 'payment'

urlpatterns = [
    path('payments/', PaymentsListView.as_view(), name='payments_list'),
    path('payments/debt', DebtPaymentsListView.as_view(), name='debt_payments_list'),
    path('payments/trials', TrialEnrollmentsView.as_view(), name='trial_enrollments_list'),
    # path('payments/create', CreatePaymentView.as_view(), name='create_payment'),
    # path('payments/create/student/<int:student_id>', CreatePaymentView.as_view(), name='create_payment_student'),
    # path('payments/create/course/<int:course_id>', CreatePaymentView.as_view(), name='create_payment_course'),
    path('payments/create/enrollment/<int:enrollment_id>', CreatePaymentView.as_view(), name='create_payment_enrollment'),
    # path('payments/<int:payment_id>', ConfirmPaymentView.as_view(), name='view_payment'),
]
