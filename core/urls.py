from django.conf.urls import url
from core.views import Receipts_Deposit, ClientLoanAccountsView, GetLoanDemandsView, PaySlipCreateView, get_group_loan_accounts, \
	get_member_loan_accounts, GetFixedDepositAccountsView, GetRecurringDepositAccountsView, ClientDepositAccountsView, \
	GetFixedDepositPaidAccountsView, GetRecurringDepositPaidAccountsView

urlpatterns = [
    url(r'^receiptsdeposit/$', Receipts_Deposit.as_view(), name="receiptsdeposit"),
    url(r'^getmemberloanaccounts/$', ClientLoanAccountsView.as_view(), name="receiptsdeposit"),
    url(r'^getloandemands/$', GetLoanDemandsView.as_view(), name="getloandemands"),
    url(r'^payslip/$', PaySlipCreateView.as_view(), name="payslip"),
    url(r'^loanaccounts/group$', get_group_loan_accounts, name="get_group_loan_accounts"),
    url(r'^loanaccounts/member$', get_member_loan_accounts, name="get_member_loan_accounts"),
    url(r'^getmemberfixeddepositaccounts/$', GetFixedDepositAccountsView.as_view(), name="getmemberfixeddepositaccounts"),
    url(r'^getmemberrecurringdepositaccounts/$', GetRecurringDepositAccountsView.as_view(), name="getmemberrecurringdepositaccounts"),
    url(r'^getmemberdepositaccounts/$', ClientDepositAccountsView.as_view(), name="getmemberdepositaccounts"),
    url(r'^getmemberfixeddepositpaidaccounts/$', GetFixedDepositPaidAccountsView.as_view(), name="getmemberfixeddepositpaidaccounts"),
    url(r'^getmemberrecurringdepositpaidaccounts/$', GetRecurringDepositPaidAccountsView.as_view(), name="getmemberrecurringdepositpaidaccounts"),
]
