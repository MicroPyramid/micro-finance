from django.conf.urls import url
from savings import views

urlpatterns = [
    # Client Savings
    url(r'^client/(?P<client_id>\d+)/savings/application/$', views.client_savings_application_view, name='clientsavingsapplication'),
    url(r'^client/(?P<client_id>\d+)/savings/account/view/$', views.client_savings_account_view, name='clientsavingsaccount'),
    url(r'^client/(?P<client_id>\d+)/savings/deposits/list/$', views.client_savings_deposits_list_view, name='listofclientsavingsdeposits'),
    url(r'^client/(?P<client_id>\d+)/savings/withdrawals/list/$', views.client_savings_withdrawals_list_view, name='listofclientsavingswithdrawals'),

    # Group Savings
    url(r'^group/(?P<group_id>\d+)/savings/application/$', views.group_savings_application_view, name='groupsavingsapplication'),
    url(r'^group/(?P<group_id>\d+)/savings/account/view/$', views.group_savings_account_view, name='groupsavingsaccount'),
    url(r'^group/(?P<group_id>\d+)/savings/deposits/list/$', views.group_savings_deposits_list_view, name='viewgroupsavingsdeposits'),
    url(r'^group/(?P<group_id>\d+)/savings/withdrawals/list/$', views.group_savings_withdrawals_list_view, name='viewgroupsavingswithdrawals'),

    # Change Savings Account Status
    url(r'^savings/account/(?P<savingsaccount_id>\d+)/change-status/$', views.change_savings_account_status,
        name='change-savings-account-status'),
]
