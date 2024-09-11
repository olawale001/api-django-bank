from rest_framework import serializers
from .models import Loan, LoanRepayment

class LoanSerializer(serializers.ModelSerializer):
    total_repayment = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = [
            'id', 'user', 'interest_rate','loan_amount', 'approved_at', 'status', 'currency', 'duration_months', 'created_at', 'updated_at', 'total_repayment'
        ]


    def get_total_repayment(self, obj):
        return obj.calculate_total_repayment()

class LoanRepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRepayment
        fields = ['id', 'loan', 'amount_paid', 'payment_date']