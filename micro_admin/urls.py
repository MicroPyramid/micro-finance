from django.conf.urls import patterns, include, url

urlpatterns = patterns('micro_admin.views',

    url(r'^$', 'index', name='microadmin_index'),
    url(r'^login/$', 'user_login', name='login'),
    url(r'^createbranch/$', 'create_branch', name='createbranch'),
    url(r'^createclient/$', 'create_client', name='createclient'),
    url(r'^branchprofile/(?P<branch_id>\d+)/$', 'branch_profile', name='branchprofile'),
    url(r'^clientprofile/$', 'client_profile', name='clientprofile'),
    url(r'^viewbranch/$', 'view_branch', name='viewbranch'),
    url(r'^editbranch/(?P<branch_id>\d+)/$', 'edit_branch', name='editbranch'),
    url(r'^deletebranch/(?P<branch_id>\d+)/$', 'delete_branch', name='deletebranch'),
    url(r'^logout/$', 'user_logout', name='logout'),

)