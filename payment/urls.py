from django.urls import path

from .views import PaymentsListView, CreatePaymentView, DebtPaymentsListView, TrialEnrollmentsView, UpdatePaymentDatesView

app_name = 'payment'

urlpatterns = [
    path('payments/', PaymentsListView.as_view(), name='payments_list'),
    path('payments/debt', DebtPaymentsListView.as_view(), name='debt_payments_list'),
    path('payments/trials', TrialEnrollmentsView.as_view(), name='trial_enrollments_list'),
    path('payments/create/enrollment/<int:enrollment_id>', CreatePaymentView.as_view(), name='create_payment_enrollment'),
    path('payment/<int:pk>/update/', UpdatePaymentDatesView.as_view(), name='update_payment_dates'),
]
