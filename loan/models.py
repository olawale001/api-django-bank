from email import message
from django.db import models
from authentication.models import User

class Loan(models.Model):
    LOAN_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EOR', 'Euro'),
        ('GBP', 'Britsh Pound'),
        ('NIR', 'Naira'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    duration_months = models.IntegerField()
    status = models.CharField(max_length=10, choices=LOAN_CHOICES, default='pending')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total_repaymeny(self):
        total_interest = (self.loan_amount * (self.interest_rate / 100)) * self.duration_months
        return self.loan_amount + total_interest
    
    def __str__(self):
        return f"{self.user.username} - {self.loan_amount}"
    
class LoanRepayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)    
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.loan.user.username} - {self.amount_paid} on {self.payment_date}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.message}'
