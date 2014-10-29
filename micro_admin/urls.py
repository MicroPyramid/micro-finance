from django.conf.urls import patterns, include, url

urlpatterns = patterns('micro_admin.views',

    url(r'^$', 'index', name='microadmin_index'),
    url(r'^login/$', 'user_login', name='login'),
    url(r'^logout/$', 'user_logout', name='logout'),

)