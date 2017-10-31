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
    url(r'^group/create/$', create_group_view, name='creategroup'),
    url(r'^group/(?P<group_id>\d+)/profile/$', group_profile_view, name='groupprofile'),
    url(r'^groups/list/$', groups_list_view, name='groupslist'),
    url(r'^group/(?P<group_id>\d+)/delete/$', group_inactive_view, name='deletegroup'),

    # Group - Assign Staff
    url(r'^group/(?P<group_id>\d+)/assign-staff/$', group_assign_staff_view, name='assignstaff'),

    # Group Members (add, remove, view)
    url(r'^group/(?P<group_id>\d+)/members/add/$', group_add_members_view, name='addmember'),
    url(r'^group/(?P<group_id>\d+)/members/list/$', group_members_list_view, name='viewmembers'),
    url(r'^group/(?P<group_id>\d+)/member/(?P<client_id>\d+)/remove/$', group_remove_members_view, name='removemember'),

    # Group Meeting (list, add)
    url(r'^group/(?P<group_id>\d+)/meetings/list/$', group_meetings_list_view, name='groupmeetings'),
    url(r'^group/(?P<group_id>\d+)/meetings/add/$', group_meetings_add_view, name='addgroupmeeting'),

    # Receipts(create, list)
    url(r'^transactions/$', transactions, name="transactions"),
    url(r'^deposits/$', deposits, name="deposits"),
    url(r'^reports/$', reports, name="reports"),
    # url(r'^receiptsdeposit/$', receipts_deposit, name="receiptsdeposit"),
    url(r'^receiptslist/$', receipts_list, name="receiptslist"),

    url(r'^generalledger/$', general_ledger, name="generalledger"),
    url(r'^fixeddeposits/$', fixed_deposits_view, name="fixeddeposits"),
    url(r'^clientfixeddepositsprofile/(?P<fixed_deposit_id>\d+)/$', client_fixed_deposits_profile, name="clientfixeddepositsprofile"),
    url(r'^viewclientfixeddeposits/$', view_client_fixed_deposits, name="viewclientfixeddeposits"),

    # Day Book
    url(r'^viewdaybook/$', day_book_view, name="viewdaybook"),
    url(r'^viewparticularclientfixeddeposits/(?P<client_id>\d+)/$', view_particular_client_fixed_deposits, name="viewparticularclientfixeddeposits"),
    # url(r'^payslip/$', pay_slip, name="payslip"),
    url(r'^paymentslist/$', payments_list, name="paymentslist"),
    url(r'^recurringdeposits/$', recurring_deposits_view, name="recurringdeposits"),
    url(r'^clientrecurringdepositsprofile/(?P<recurring_deposit_id>\d+)/$',
        client_recurring_deposits_profile, name="clientrecurringdepositsprofile"),
    url(r'^viewclientrecurringdeposits/$', view_client_recurring_deposits, name="viewclientrecurringdeposits"),
    url(r'^viewparticularclientrecurringdeposits/(?P<client_id>\d+)/$',
        view_particular_client_recurring_deposits, name="viewparticularclientrecurringdeposits"),
    # url(r'^generalledgerpdfdownload/$', GeneralLedgerPdfDownload, name="generalledgerpdfdownload"),
    url(r'^daybookpdfdownload/(?P<date>\d{4}-\d{2}-\d{2})/$', daybook_pdf_download, name="daybookpdfdownload"),
    url(r'^userchangepassword/$', user_change_password, name="userchangepassword"),
]
