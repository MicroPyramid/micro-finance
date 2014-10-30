from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'micro_finance.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^', include('micro_admin.urls', namespace='micro_admin')),
    url(r'^admin/', include(admin.site.urls)),
)
