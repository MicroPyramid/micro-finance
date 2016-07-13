from django import template
import decimal
from micro_admin.models import (
    Branch, User, Group, Client, SavingsAccount, LoanAccount, FixedDeposits, Receipts, Payments, RecurringDeposits, GroupMeetings,
    ClientBranchTransfer)
register = template.Library()


@register.filter
def has_payment_reciept(client):
    pass
