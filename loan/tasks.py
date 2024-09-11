from email import message
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import LoanRepayment, Loan

@shared_task
def send_payment_reminders():
    today = timezone.now().date()
    due_repayments = LoanRepayment.objects.filter(due_date__date=today)

    for repayment in due_repayments:
        subject = 'Payment Reminder'
        message = f'Dear {repayment.loan.user.username}, \n\nThis is a reminder that your repayment of {repayment.amount_paid} is due today.'
        recipient_list = [repayment.loan.user.email]
        send_mail(subject, message, 'form olacodeire@gmail.com', recipient_list)

@shared_task
def send_loan_approval_email(loan_id):
    loan = Loan.objects.get(id=loan_id)       
    send_mail(
        'Loan Approved',
        f'Your loan of {loan.loan_amount} {loan.currency} has been approved',
        'from:olacodeire@gmail.com',
        [loan.user.email],
        fail_silently=False,
    )