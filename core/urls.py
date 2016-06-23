from django.conf.urls import url
from core.views import(
    Receipts_Deposit,
)
urlpatterns = [
    url(r'^receiptsdeposit/$', Receipts_Deposit.as_view(), name="receiptsdeposit"),
]
