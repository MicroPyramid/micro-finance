from django.conf.urls import url
from loans.views import *

urlpatterns = [
    # Client Loans (apply, view, list)
    url(r'^client/(?P<client_id>\d+)/loan/apply/$', ClientLoanApplicationView.as_view(), name='clientloanapplication'),
    url(r'^client/(?P<client_id>\d+)/loans/list/$', ClientLoansListView.as_view(), name="clientloanaccountslist"),
    url(r'^client/loan/(?P<pk>\d+)/view/$', ClientLoanAccount.as_view(), name='clientloanaccount'),
    url(r'^client/(?P<client_id>\d+)/loan/(?P<loanaccount_id>\d+)/deposits/list/$', ClientLoanDepositsListView.as_view(), name='listofclientloandeposits'),

    # Client Loans - Ledger (view, CSV, Excel, PDF downloads)
    url(r'^client/(?P<client_id>\d+)/loan/(?P<loanaccount_id>\d+)/ledger/$', ClientLoanLedgerView.as_view(), name="clientloanledgeraccount"),
    url(r'^client/(?P<client_id>\d+)/loan/(?P<loanaccount_id>\d+)/ledger/download/csv/$', ClientLedgerCSVDownload.as_view(), name="clientledgercsvdownload"),
    url(r'^client/(?P<client_id>\d+)/loan/(?P<loanaccount_id>\d+)/ledger/download/excel$', ClientLedgerExcelDownload.as_view(), name="clientledgerexceldownload"),
    url(r'^client/(?P<client_id>\d+)/loan/(?P<loanaccount_id>\d+)/ledger/download/pdf/$', ClientLedgerPDFDownload.as_view(), name="clientledgerpdfdownload"),

    # Group Loans (apply, view, list)
    url(r'^group/(?P<group_id>\d+)/loan/apply/$', GroupLoanApplicationView.as_view(), name='grouploanapplication'),
    url(r'^group/(?P<group_id>\d+)/loans/list/$', GroupLoansListView.as_view(), name="grouploanaccountslist"),
    url(r'^group/loan/(?P<pk>\d+)/view/$', GroupLoanAccount.as_view(), name='grouploanaccount'),
    url(r'^group/(?P<group_id>\d+)/loan/(?P<loanaccount_id>\d+)/deposits/list/$', GroupLoanDepositsListView.as_view(), name='viewgrouploandeposits'),

    # Change Loan Account Status
    url(r'^loan/(?P<pk>\d+)/change-status/$', ChangeLoanAccountStatus.as_view(), name='change_loan_account_status'),

    # Issue Loan
    url(r'^loan/(?P<loanaccount_id>\d+)/issue/$', IssueLoan.as_view(), name='issueloan'),
]
