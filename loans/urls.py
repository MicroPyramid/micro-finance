from django.conf.urls import url
from loans.views import *

urlpatterns = [

    # function based views
    url(r'^client/(?P<client_id>\d+)/loan/apply/$', client_loan_application, name='clientloanapplication'),
    url(r'^client/(?P<client_id>\d+)/loans/list/$', client_loan_list, name="clientloanaccountslist"),
    url(r'^client/loan/(?P<pk>\d+)/view/$', client_loan_account, name='clientloanaccount'),
    url(r'^client/(?P<client_id>\d+)/loan/(?P<loanaccount_id>\d+)/deposits/list/$', client_loan_deposit_list, name='listofclientloandeposits'),
    url(r'^client/(?P<client_id>\d+)/loan/(?P<loanaccount_id>\d+)/ledger/$', client_loan_ledger_view, name="clientloanledgeraccount"),
    url(
        r'^client/(?P<client_id>\d+)/loan/(?P<loanaccount_id>\d+)/ledger/download/csv/$', client_ledger_csv_download,
        name="clientledgercsvdownload"),
    url(
        r'^client/(?P<client_id>\d+)/loan/(?P<loanaccount_id>\d+)/ledger/download/excel/$', client_ledger_excel_download,
        name="clientledgerexceldownload"),
    url(
        r'^client/(?P<client_id>\d+)/loan/(?P<loanaccount_id>\d+)/ledger/download/pdf/$', client_ledger_pdf_download,
        name="clientledgerpdfdownload"),
    url(r'^group/(?P<group_id>\d+)/loan/apply/$', group_loan_application, name='grouploanapplication'),
    url(r'^group/(?P<group_id>\d+)/loans/list/$', group_loan_list, name="grouploanaccountslist"),
    url(r'^group/loan/(?P<pk>\d+)/view/$', group_loan_account, name='grouploanaccount'),
    url(r'^group/(?P<group_id>\d+)/loan/(?P<loanaccount_id>\d+)/deposits/list/$', group_loan_deposits_list, name='viewgrouploandeposits'),
    url(r'^loan/(?P<pk>\d+)/change-status/$', change_loan_account_status, name='change_loan_account_status'),
    url(r'^loan/(?P<loanaccount_id>\d+)/issue/$', issue_loan, name='issueloan'),
]
