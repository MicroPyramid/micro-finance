from django.conf.urls import url
from core.views import Receipts_Deposit, PaySlip, ClientLoanAccountsView, GetLoanDemandsView

urlpatterns = [
    url(r'^receiptsdeposit/$', Receipts_Deposit.as_view(), name="receiptsdeposit"),
    url(r'^getmemberloanaccounts/$', ClientLoanAccountsView.as_view(), name="receiptsdeposit"),
    url(r'^getloandemands/$', GetLoanDemandsView.as_view(), name="getloandemands"),
    url(r'^payslip/$', PaySlip.as_view(), name="payslip"),
]
