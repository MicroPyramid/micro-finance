from django.conf.urls import url
from core.views import(
    Receipts_Deposit,
    PaySlip,
)
urlpatterns = [
    url(r'^receiptsdeposit/$', Receipts_Deposit.as_view(), name="receiptsdeposit"),
    url(r'^payslip/$', PaySlip.as_view(), name="payslip"),
]
