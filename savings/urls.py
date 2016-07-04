from django.conf.urls import url
from savings.views import *

urlpatterns = [
    # Client Savings
    url(r'^client/(?P<client_id>\d+)/savings/application/$', ClientSavingsApplicationView.as_view(), name='clientsavingsapplication'),
    url(r'^client/(?P<client_id>\d+)/savings/account/view/$', ClientSavingsAccountView.as_view(), name='clientsavingsaccount'),

    # Group Savings
    url(r'^group/(?P<group_id>\d+)/savings/application/$', GroupSavingsApplicationView.as_view(), name='groupsavingsapplication'),
    url(r'^group/(?P<group_id>\d+)/savings/account/view/$', GroupSavingsAccountView.as_view(), name='groupsavingsaccount'),

    # Change Savings Account Status
    url(r'^savings/account/(?P<savingsaccount_id>\d+)/change-status/$', ChangeSavingsAccountStatus.as_view(),
        name='change-savings-account-status'),
]
