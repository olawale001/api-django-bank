from pypdf import PdfMerger
from pytz import timezone
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render

import account
from .utils import render_to_pdf
from authentication import serializers
from .models import Account, Transaction
from .serializers import AccountSerializer, TransactionSerializer
from rest_framework.parsers import MultiPartParser, FormParser



class AccountDetailView(generics.RetrieveAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, *args, **kwargs):
        account = Account.objects.get(user=request.user)
        serializer = AccountSerializer(account)
        return Response(serializer.data)
    
class DepositView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]    
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        account = Account.objects.get(user=request.user)
        amount = request.data.get('amount')
        account.balance += float(amount)
        account.save()
        Transaction.objects.create(account=account, amount=amount, transaction_type='deposit')
        return Response({'message': 'Deposit successful'}, status=status.HTTP_200_OK)
    

class WithdrawView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        account = Account.objects.get(user=request.user)
        amount = request.data.get('amount')
        if account.balance >= float(amount):
            account.balance -= float(amount)
            account.save()
            Transaction.objects.create(account=account, amount=amount, transaction_type='withdrawal')
            return Response({'message': 'withdrawal successful'}, status=status.HTTP_200_OK)
        return Response({'message': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
    

class TransferView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        account = Account.objects.get(user=request.user)
        recipient_account = Account.objects.get(user__username=request.data.get('recipient'))
        amount = request.data.get('amount')

        if account.balance >= float(amount):
            account.balance -= float(amount)
            recipient_account.balance += float(amount)
            account.save()
            recipient_account.save()
            Transaction.objects.create(account=account, amount=amount, transaction_type='transfer')
            return Response({'message': 'Transfer Successful'}, status=status.HTTP_200_OK)
        return Response({'message': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)


class TransactionHistoryView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['transaction_type', 'created_at', 'amount']

    def get_queryset(self):
        account = self.request.user.account
        return Transaction.objects.filter(account=account)
    
class AccountStatementView(APIView): 
    permission_classes = [IsAuthenticated]   
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        account = request.user.account
        transaction = Transaction.objects.filter(account=account)
        context = {
            'account': account,
            'transaction': transaction,
            'date': timezone.now()
        }
        pdf = render_to_pdf('account_statement.html', context)
        return pdf