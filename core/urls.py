from django.conf.urls import url
from core.views import Receipts_Deposit, ClientLoanAccountsView, GetLoanDemandsView, PaySlipCreateView

urlpatterns = [
    url(r'^receiptsdeposit/$', Receipts_Deposit.as_view(), name="receiptsdeposit"),
    url(r'^getmemberloanaccounts/$', ClientLoanAccountsView.as_view(), name="receiptsdeposit"),
    url(r'^getloandemands/$', GetLoanDemandsView.as_view(), name="getloandemands"),
    url(r'^payslip/$', PaySlipCreateView.as_view(), name="payslip"),
]
