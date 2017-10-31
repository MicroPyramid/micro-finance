from django.conf.urls import url
from core.views import receipts_deposit, client_loan_accounts_view, get_loan_demands_view, payslip_create_view, get_group_loan_accounts, \
    get_member_loan_accounts, get_fixed_deposit_accounts_view, get_recurring_deposit_accounts_view, client_deposit_accounts_view, \
    get_fixed_deposit_paid_accounts_view, get_recurring_deposit_paid_accounts_view

urlpatterns = [
    url(r'^receiptsdeposit/$', receipts_deposit, name="receiptsdeposit"),
    url(r'^getmemberloanaccounts/$', client_loan_accounts_view, name="getmemberloanaccounts"),
    url(r'^getloandemands/$', get_loan_demands_view, name="getloandemands"),
    url(r'^payslip/$', payslip_create_view, name="payslip"),
    url(r'^loanaccounts/group$', get_group_loan_accounts, name="get_group_loan_accounts"),
    url(r'^loanaccounts/member$', get_member_loan_accounts, name="get_member_loan_accounts"),
    url(r'^getmemberfixeddepositaccounts/$', get_fixed_deposit_accounts_view, name="getmemberfixeddepositaccounts"),
    url(r'^getmemberrecurringdepositaccounts/$', get_recurring_deposit_accounts_view, name="getmemberrecurringdepositaccounts"),
    url(r'^getmemberdepositaccounts/$', client_deposit_accounts_view, name="getmemberdepositaccounts"),
    url(r'^getmemberfixeddepositpaidaccounts/$', get_fixed_deposit_paid_accounts_view, name="getmemberfixeddepositpaidaccounts"),
    url(r'^getmemberrecurringdepositpaidaccounts/$', get_recurring_deposit_paid_accounts_view, name="getmemberrecurringdepositpaidaccounts"),
]
