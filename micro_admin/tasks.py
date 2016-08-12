from celery import task
from micro_admin.models import SavingsAccount
from decimal import Decimal as d
from datetime import datetime
import calendar


@task()
def calculate_interest_of_savings_account():
    savings_accounts = SavingsAccount.objects.filter(status='Approved')
    for savings_account in savings_accounts:
        current_date = datetime.now().date()
        year_days = 366 if calendar.isleap(current_date.year) else 365
        daily_interest_rate_charged = (
            savings_account.savings_balance * savings_account.annual_interest_rate) / (d(year_days) * 100)
        savings_account.savings_balance += daily_interest_rate_charged
        savings_account.save()
