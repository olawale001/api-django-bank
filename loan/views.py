from email import message
from pytz import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Loan, LoanRepayment, Notification
from .serializers import LoanRepaymentSerializer, LoanSerializer
from rest_framework.views import APIView
from forex_python.converter import CurrencyRates
from loan import models


class LoanCreateView(generics.CreateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def convert_currency(amount, from_currency, to_currency):
        c = CurrencyRates()
        return c.convert(from_currency, to_currency)


class LoanListView(generics.ListAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

class LoanDetailView(generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

class LoanApprovalView(generics.UpdateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, *args, **kwargs):
        loan = self.get_object()
        loan.status = 'approved'
        loan.approved_at = timezone.now()
        Notification.objects.create(
            user=loan.user,
            message=f'Your loan of {loan.loan_amount} {loan.currency} has been approved'
        )
        loan.save()
        return Response(LoanSerializer(loan).data)
    

class LoanRepaymentCreateView(generics.CreateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanRepaymentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

class LoanRepaymentListView(generics.ListAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanRepaymentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


class LoanStatementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(id=loan_id, user=request.user)
        except Loan.DoesNotExist:
            return  Response({'detail': 'Loan not found'}, status=status.HTTP_400_BAD_REQUEST)   
        
        total_paid = loan.loanrepayment_set.aggregate(total_paid=models.Sum('amount'))['total_paid']

        statement = {
            'loan_details': LoanSerializer(loan).data,
            'total_paid': total_paid,
            'total_outstanding': loan.calculate_total_repaymeny() - total_paid,
            'penalty': loan.loanrepayment_set.filter(penalty_applied=True).count(),
        }

        return Response(statement)
    

class LoanReportView(generics.ListAPIView):
    serializer_class = LoanSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = Loan.objects.all()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

class LoanSearchView(generics.ListAPIView):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        queryset = Loan.objects.filter(user=user)

        if user.is_staff:
            queryset= Loan.objects.all()

        loan_amount = self.request.query_params.get('loan_amount')    
        status = self.request.query_params.get('status')
        user_id = self.request.query_params.get('user')

        if loan_amount:
            queryset = queryset.filter(loan_amount=loan_amount)
        if status:
            queryset = queryset.filter(status=status)
        if user_id and user.is_staff:
            queryset = queryset.filter(user_id=user_id)


        return queryset