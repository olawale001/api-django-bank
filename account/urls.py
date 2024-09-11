from os import name
from django.urls import path
import account
from .views import AccountDetailView, DepositView, TransferView, WithdrawView, TransactionHistoryView, AccountStatementView


app_name = account

urlpatterns = [
    path('account/', AccountDetailView.as_view(), name='account_details'),
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('transfer/', TransferView.as_view(), name='transfer'),
    path('transactions/', TransactionHistoryView.as_view(), name='transaction-history'),
    path('acount/statement/', AccountStatementView.as_view(), name='account-statements'),
]
