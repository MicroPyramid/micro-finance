from django import template
import decimal
from micro_admin.models import (
    Branch, User, Group, Client, SavingsAccount, LoanAccount, FixedDeposits, Receipts, Payments, RecurringDeposits, GroupMeetings,
    ClientBranchTransfer, Menu, Page)
from django.db.models import Prefetch
register = template.Library()


@register.filter
def has_payment_reciept(client):
    pass


@register.filter
def get_range(value):
    return range(value)


@register.assignment_tag(takes_context=True)
def get_menus(context):
    menu_list = Menu.objects.filter(status="on").prefetch_related(
        Prefetch("menu_set", queryset=Menu.objects.filter(
            status="on").order_by('lvl'), to_attr="active_children"
        )
    )
    return menu_list.filter(parent=None, status="on").order_by('lvl')
