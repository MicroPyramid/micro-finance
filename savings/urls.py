from django.conf.urls import url
from savings.views import *

urlpatterns = [
    # Client Savings
    url(r'^client/(?P<client_id>\d+)/savings/application/$', client_savings_application_view, name='clientsavingsapplication'),
    url(r'^client/(?P<client_id>\d+)/savings/account/view/$', client_savings_account_view, name='clientsavingsaccount'),
    url(r'^client/(?P<client_id>\d+)/savings/deposits/list/$', ClientSavingsDepositsListView.as_view(), name='listofclientsavingsdeposits'),
    url(r'^client/(?P<client_id>\d+)/savings/withdrawals/list/$', ClientSavingsWithdrawalsListView.as_view(), name='listofclientsavingswithdrawals'),

    # Group Savings
    url(r'^group/(?P<group_id>\d+)/savings/application/$', GroupSavingsApplicationView.as_view(), name='groupsavingsapplication'),
    url(r'^group/(?P<group_id>\d+)/savings/account/view/$', GroupSavingsAccountView.as_view(), name='groupsavingsaccount'),
    url(r'^group/(?P<group_id>\d+)/savings/deposits/list/$', GroupSavingsDepositsListView.as_view(), name='viewgroupsavingsdeposits'),
    url(r'^group/(?P<group_id>\d+)/savings/withdrawals/list/$', GroupSavingsWithdrawalsListView.as_view(), name='viewgroupsavingswithdrawals'),

    # Change Savings Account Status
    url(r'^savings/account/(?P<savingsaccount_id>\d+)/change-status/$', ChangeSavingsAccountStatus.as_view(),
        name='change-savings-account-status'),
]
