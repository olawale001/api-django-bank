from django.contrib import admin
from .models import Loan, User

class LoanAdmin(admin.ModelAdmin):
    list_display = ('user', 'loan_amount', 'status', 'approved_at')
    search_fields = ('user__username', 'status')
    list_filter = ('status', 'created_at')

admin.site.register(Loan, LoanAdmin)    
