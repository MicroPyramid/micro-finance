from django.conf.urls import patterns, include, url

urlpatterns = patterns('micro_admin.views',

    url(r'^$', 'index', name='microadmin_index'),
    url(r'^login/$', 'user_login', name='login'),
    url(r'^createbranch/$', 'create_branch', name='createbranch'),
    url(r'^createclient/$', 'create_client', name='createclient'),
    url(r'^createuser/$', 'create_user', name='createuser'),
    url(r'^creategroup/$', 'create_group', name='creategroup'),
    url(r'^editbranch/(?P<branch_id>\d+)/$', 'edit_branch', name='editbranch'),
    url(r'^edituser/(?P<user_id>\d+)/$', 'edit_user', name='edituser'),
    url(r'^editgroup/(?P<group_id>\d+)/$', 'edit_group', name='editgroup'),
    url(r'^branchprofile/(?P<branch_id>\d+)/$', 'branch_profile', name='branchprofile'),
    url(r'^userprofile/(?P<user_id>\d+)/$', 'user_profile', name='userprofile'),
    url(r'^clientprofile/$', 'client_profile', name='clientprofile'),
    url(r'^groupprofile/(?P<group_id>\d+)/$', 'group_profile', name='groupprofile'),
    url(r'^userslist/$', 'users_list', name='userslist'),
    url(r'^viewbranch/$', 'view_branch', name='viewbranch'),
    url(r'^deletebranch/(?P<branch_id>\d+)/$', 'delete_branch', name='deletebranch'),
    url(r'^deleteuser/(?P<user_id>\d+)/$', 'delete_user', name='deleteuser'),
    url(r'^assignstaff/(?P<group_id>\d+)/$', 'assign_staff_to_group', name='assignstaff'),
    url(r'^logout/$', 'user_logout', name="logout"),

)