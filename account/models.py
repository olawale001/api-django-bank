from sqlite3 import Timestamp
from django.db import models
import random
from authentication.models import User

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=12, unique=True, editable=False)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def generate_account_number(self):
        return ''.join([str(random.randint(0, 9)) for _ in range(12)])        

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generat_account_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.account_number}"
    

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    TRANSACTION_TYPE = [('deposit', 'Deposit'), ('withdraw', 'Withdraw'), ('transfer', 'Transfer')]
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} on {self.created_at}"