from django.conf.urls import url
from micro_admin.views import *

urlpatterns = [

    url(r'^$', index, name='microadmin_index'),
    url(r'^login/$', getin, name='login'),
    url(r'^logout/$', getout, name="logout"),
    # ------------------------------------------- #
    # Branch model urls
    url(r'^branch/create/$', create_branch_view, name='createbranch'),
    url(r'^branch/edit/(?P<pk>\d+)/$', update_branch_view, name='editbranch'),
    url(r'^branch/view/$', branch_list_view, name='viewbranch'),
    url(r'^branch/delete/(?P<pk>\d+)/$', branch_inactive_view, name='deletebranch'),
    url(r'^branch/profile/(?P<pk>\d+)/$', branch_profile_view, name='branchprofile'),
    # ------------------------------------------- #
    # User model urls
    url(r'^users/list/$', users_list_view, name='userslist'),
    url(r'^user/create/$', create_user_view, name='createuser'),
    url(r'^user/edit/(?P<pk>\d+)/$', update_user_view, name='edituser'),
    url(r'^user/profile/(?P<pk>\d+)/$', user_profile_view, name='userprofile'),
    url(r'^user/delete/(?P<pk>\d+)/$', user_inactive_view, name='deleteuser'),
    # ------------------------------------------- #
    # Client model urls
    url(r'^clients/list/$', clients_list_view, name='viewclient'),
    url(r'^client/create/$', create_client_view, name='createclient'),
    url(r'^client/edit/(?P<pk>\d+)/$', update_client_view, name='editclient'),
    url(r'^client/delete/(?P<pk>\d+)/$', client_inactive_view, name='deleteclient'),
    url(r'^client/profile/(?P<pk>\d+)/$', client_profile_view, name='clientprofile'),
    url(r'^client/profile/update/(?P<pk>\d+)/$', updateclientprofileview, name='updateclientprofile'),
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

    # Receipts(create, list)
    # url(r'^receiptsdeposit/$', receipts_deposit, name="receiptsdeposit"),
    url(r'^receiptslist/$', ReceiptsList.as_view(), name="receiptslist"),

    url(r'^generalledger/$', GeneralLedger.as_view(), name="generalledger"),
    url(r'^fixeddeposits/$', FixedDepositsView.as_view(), name="fixeddeposits"),
    url(r'^clientfixeddepositsprofile/(?P<fixed_deposit_id>\d+)/$', ClientFixedDepositsProfile.as_view(), name="clientfixeddepositsprofile"),
    url(r'^viewclientfixeddeposits/$', ViewClientFixedDeposits.as_view(), name="viewclientfixeddeposits"),

    # Day Book
    url(r'^viewdaybook/$', DayBookView.as_view(), name="viewdaybook"),
    url(r'^viewparticularclientfixeddeposits/(?P<client_id>\d+)/$', ViewParticularClientFixedDeposits.as_view(), name="viewparticularclientfixeddeposits"),
    # url(r'^payslip/$', pay_slip, name="payslip"),
    url(r'^paymentslist/$', PaymentsList.as_view(), name="paymentslist"),
    url(r'^recurringdeposits/$', RecurringDepositsView.as_view(), name="recurringdeposits"),
    url(r'^clientrecurringdepositsprofile/(?P<recurring_deposit_id>\d+)/$', ClientRecurringDepositsProfile.as_view(), name="clientrecurringdepositsprofile"),
    url(r'^viewclientrecurringdeposits/$', ViewClientRecurringDeposits.as_view(), name="viewclientrecurringdeposits"),
    url(r'^viewparticularclientrecurringdeposits/(?P<client_id>\d+)/$', ViewParticularClientRecurringDeposits.as_view(), name="viewparticularclientrecurringdeposits"),
    url(r'^generalledgerpdfdownload/$', GeneralLedgerPdfDownload.as_view(), name="generalledgerpdfdownload"),
    url(r'^daybookpdfdownload/(?P<date>\d{4}-\d{2}-\d{2})/$', DayBookPdfDownload.as_view(), name="daybookpdfdownload"),
    url(r'^userchangepassword/$', UserChangePassword.as_view(), name="userchangepassword"),
]
