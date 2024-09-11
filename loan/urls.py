from django.urls import path
import loan
from .views import (
    LoanCreateView, LoanListView, LoanDetailView, LoanApprovalView,
    LoanRepaymentCreateView, LoanRepaymentListView, LoanStatementView, LoanReportView,
    LoanSearchView
)

app_name = loan

urlpatterns = [
    path('api/loans/', LoanListView.as_view(), name='loan_list'),
    path('api/loans/create/', LoanCreateView.as_view(), name='loan_create'),
    path('api/loans/<int:pk>/', LoanDetailView.as_view(), name='loan_detail'),
    path('api/loans/<int:pk>/approve/', LoanApprovalView.as_view(), name='loan_approve'),

    path('api/loan-repayments/', LoanRepaymentListView.as_view(), name='loan_repayment_list'),
    path('api/loan-repayments/create/', LoanRepaymentCreateView.as_view(), name='loan_repayment_create'),

    path('api/loans/<int:loan_id>/statements/', LoanStatementView.as_view(), name='loan_statement'),
    path('api/admin/loan-reports/', LoanReportView.as_view(), name='loan_reports'),
    path('api/loans/search/', LoanSearchView.as_view(), name='loan_search'),
]
