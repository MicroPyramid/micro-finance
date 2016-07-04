from django.conf.urls import url
from micro_admin.views import *

urlpatterns = [

    url(r'^$', index, name='microadmin_index'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name="logout"),
    # ------------------------------------------- #
    # Branch model urls
    url(r'^branch/create/$', CreateBranchView.as_view(), name='createbranch'),
    url(r'^branch/edit/(?P<pk>\d+)/$', UpdateBranchView.as_view(), name='editbranch'),
    url(r'^branch/view/$', BranchListView.as_view(), name='viewbranch'),
    url(r'^branch/delete/(?P<pk>\d+)/$', BranchInactiveView.as_view(), name='deletebranch'),
    url(r'^branch/profile/(?P<pk>\d+)/$', BranchProfileView.as_view(), name='branchprofile'),
    # ------------------------------------------- #
    # User model urls
    url(r'^user/edit/(?P<pk>\d+)/$', UpdateUserView.as_view(), name='edituser'),
    url(r'^user/create/$', CreateUserView.as_view(), name='createuser'),
    url(r'^user/profile/(?P<pk>\d+)/$', UserProfileView.as_view(), name='userprofile'),
    url(r'^users/list/$', UsersListView.as_view(), name='userslist'),
    url(r'^user/delete/(?P<pk>\d+)/$', UserInactiveView.as_view(), name='deleteuser'),
    # ------------------------------------------- #
    # Client model urls
    url(r'^client/create/$', CreateClientView.as_view(), name='createclient'),
    url(r'^client/edit/(?P<pk>\d+)/$', UpdateClientView.as_view(), name='editclient'),
    url(r'^clients/list/$', ClientsListView.as_view(), name='viewclient'),
    url(r'^client/profile/(?P<pk>\d+)/$', ClienProfileView.as_view(), name='clientprofile'),
    url(r'^client/delete/(?P<pk>\d+)/$', ClientInactiveView.as_view(), name='deleteclient'),
    url(r'^client/profile/update/(?P<client_id>\d+)/$', update_clientprofile, name='updateclientprofile'),
    # ------------------------------------------- #
    # Group
    url(r'^group/create/$', CreateGroupView.as_view(), name='creategroup'),
    url(r'^group/(?P<group_id>\d+)/profile/$', GroupProfileView.as_view(), name='groupprofile'),
    url(r'^groups/list/$', GroupsListView.as_view(), name='groupslist'),
    url(r'^group/(?P<group_id>\d+)/delete/$', GroupInactiveView.as_view(), name='deletegroup'),

    # Group - Assign Staff
    url(r'^group/(?P<group_id>\d+)/assign-staff/$', GroupAssignStaffView.as_view(), name='assignstaff'),

    # Group Members (add, remove, view)
    url(r'^group/(?P<group_id>\d+)/members/add/$', GroupAddMembersView.as_view(), name='addmember'),
    url(r'^group/(?P<group_id>\d+)/members/list/$', GroupMembersListView.as_view(), name='viewmembers'),
    url(r'^group/(?P<group_id>\d+)/member/(?P<client_id>\d+)/remove/$', GroupRemoveMembersView.as_view(), name='removemember'),

    # Group Meeting (list, add)
    url(r'^group/(?P<group_id>\d+)/meetings/list/$', GroupMeetingsListView.as_view(), name='groupmeetings'),
    url(r'^group/(?P<group_id>\d+)/meetings/add/$', GroupMeetingsAddView.as_view(), name='addgroupmeeting'),

    url(r'^receiptsdeposit/$', receipts_deposit, name="receiptsdeposit"),
    url(r'^receiptslist/$', ReceiptsList.as_view(), name="receiptslist"),
    url(r'^ledgeraccount/(?P<client_id>\d+)/(?P<loanaccount_id>\d+)/$', LedgerAccount.as_view(), name="ledgeraccount"),
    url(r'^generalledger/$', GeneralLedger.as_view(), name="generalledger"),
    url(r'^fixeddeposits/$', FixedDepositsView.as_view(), name="fixeddeposits"),
    url(r'^clientfixeddepositsprofile/(?P<fixed_deposit_id>\d+)/$', ClientFixedDepositsProfile.as_view(), name="clientfixeddepositsprofile"),
    url(r'^viewclientfixeddeposits/$', ViewClientFixedDeposits.as_view(), name="viewclientfixeddeposits"),
    url(r'^viewdaybook/$', view_day_book, name="viewdaybook"),
    url(r'^viewparticularclientfixeddeposits/(?P<client_id>\d+)/$', ViewParticularClientFixedDeposits.as_view(), name="viewparticularclientfixeddeposits"),
    url(r'^payslip/$', pay_slip, name="payslip"),
    url(r'^grouploanaccountslist/(?P<group_id>\d+)/$', ViewGroupLoansList.as_view(), name="grouploanaccountslist"),
    url(r'^clientloanaccountslist/(?P<client_id>\d+)/$', ViewClientLoansList.as_view(), name="clientloanaccountslist"),
    url(r'^paymentslist/$', PaymentsList.as_view(), name="paymentslist"),
    url(r'^recurringdeposits/$', RecurringDepositsView.as_view(), name="recurringdeposits"),
    url(r'^clientrecurringdepositsprofile/(?P<recurring_deposit_id>\d+)/$', ClientRecurringDepositsProfile.as_view(), name="clientrecurringdepositsprofile"),
    url(r'^viewclientrecurringdeposits/$', ViewClientRecurringDeposits.as_view(), name="viewclientrecurringdeposits"),
    url(r'^viewparticularclientrecurringdeposits/(?P<client_id>\d+)/$', ViewParticularClientRecurringDeposits.as_view(), name="viewparticularclientrecurringdeposits"),
    url(r'^clientledgercsvdownload/(?P<client_id>\d+)/$', ClientLedgerCSVDownload.as_view(), name="clientledgercsvdownload"),
    url(r'^clientledgerexceldownload/(?P<client_id>\d+)/$', ClientLedgerExcelDownload.as_view(), name="clientledgerexceldownload"),
    url(r'^clientledgerpdfdownload/(?P<client_id>\d+)/$', ClientLedgerPDFDownload.as_view(), name="clientledgerpdfdownload"),
    url(r'^generalledgerpdfdownload/$', GeneralLedgerPdfDownload.as_view(), name="generalledgerpdfdownload"),
    url(r'^daybookpdfdownload/(?P<date>\d{4}-\d{2}-\d{2})/$', DayBookPdfDownload.as_view(), name="daybookpdfdownload"),
    url(r'^userchangepassword/$', UserChangePassword.as_view(), name="userchangepassword"),
    url(r'^getmemberloanaccounts/$', getmember_loanaccounts, name="getmemberloanaccounts"),
    url(r'^getloandemands/$', getloan_demands, name="getloandemands"),
]
