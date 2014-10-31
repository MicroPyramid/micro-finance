from django.conf.urls import patterns, include, url

urlpatterns = patterns('micro_admin.views',

    url(r'^$', 'index', name='microadmin_index'),
    url(r'^login/$', 'user_login', name='login'),
    url(r'^createbranch/$', 'create_branch', name='createbranch'),
    url(r'^createuser/$', 'create_user', name='createuser'),
    url(r'^editbranch/(?P<branch_id>\d+)/$', 'edit_branch', name='editbranch'),
    url(r'^edituser/(?P<user_id>\d+)/$', 'edit_user', name='edituser'),
    url(r'^branchprofile/$', 'branch_profile', name='branchprofile'),
    url(r'^userprofile/(?P<user_id>\d+)/$', 'user_profile', name='userprofile'),
    url(r'^logout/$', 'user_logout', name="logout"),

)